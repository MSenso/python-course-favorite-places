import logging.config
from typing import Optional

from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from clients.geo import LocationClient
from integrations.db.session import get_session
from integrations.events.producer import EventProducer
from integrations.events.schemas import CountryCityDTO
from models import Place
from repositories.places_repository import PlacesRepository
from schemas.places import PlaceSummary, PlaceModel
from settings import settings

logging.config.fileConfig("logging.conf")
logger = logging.getLogger()


class PlacesService:
    """
    Сервис для работы с информацией о любимых местах.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        """
        Инициализация сервиса.

        :param session: Объект сессии для взаимодействия с базой данных
        """

        self.session = session
        self.places_repository = PlacesRepository(session)

    async def get_places_list(self) -> list[Place]:
        """
        Получение списка любимых мест.

        :param limit: Ограничение на количество элементов в выборке.
        :return:
        """

        return await self.places_repository.find_all_by()

    async def get_place(self, primary_key: int) -> Optional[Place]:
        """
        Получение объекта любимого места по его идентификатору.

        :param primary_key: Идентификатор объекта.
        :return:
        """

        return await self.places_repository.find(primary_key)

    async def update_place_location(self, place: PlaceModel, summary: PlaceSummary) -> PlaceModel:
        """
        Обновление локации по переданным данным.

        :param PlaceModel place: Модель места.
        :param PlaceSummary summary: Данные для поиска.
        :return:
        """
        if location := await LocationClient().get_location(
                latitude=summary.latitude, longitude=summary.longitude
        ):
            place.country = location.alpha2code
            place.city = location.city
            place.locality = location.locality
            if place.latitude is None:
                place.latitude = location.latitude
            if place.longitude is None:
                place.longitude = location.longitude
        return place

    @staticmethod
    def summary_to_model(summary: PlaceSummary) -> PlaceModel:
        """
        Трансформация PlaceSummary в PlaceModel (с не None полями).

        :param PlaceSummary summary: Данные для модели.
        :return:
        """
        model_raw = {
            key: value for key, value in summary.dict().items() if value is not None
        }

        return PlaceModel(**model_raw)

    @staticmethod
    def publish_country_event(place: PlaceModel):
        """
        Публикация ивента о попытке импорта информации из Country Informer Service.

        :param PlaceModel place: Модель места.
        :return:
        """
        try:
            place_data = CountryCityDTO(
                city=place.city if place.city else "",
                alpha2code=place.country,
            )
            EventProducer().publish(
                queue_name=settings.rabbitmq.queue.places_import, body=place_data.json()
            )
        except ValidationError:
            logger.warning(
                "The message was not well-formed during publishing event.",
                exc_info=True,
            )

    async def create_place(self, summary: PlaceSummary) -> Optional[int]:
        """
        Создание нового объекта любимого места по переданным данным.

        :param summary: Данные создаваемого объекта.
        :return: Идентификатор созданного объекта.
        """
        place = PlaceModel(latitude=summary.latitude,
                           longitude=summary.longitude,
                           description=summary.description)
        # Получение локации
        place = await self.update_place_location(place, summary)

        primary_key = await self.places_repository.create_model(place)
        await self.session.commit()

        # публикация события о создании нового объекта любимого места
        # для попытки импорта информации по нему в сервисе Countries Informer
        self.publish_country_event(place)

        return primary_key

    async def update_place(self, primary_key: int, summary: PlaceSummary) -> Optional[int]:
        """
        Обновление объекта любимого места по переданным данным.

        :param primary_key: Идентификатор объекта.
        :param summary: Данные для обновления объекта.
        :return:
        """
        # Получение модели из summary так, чтобы у модели были только not None поля из summary
        place = self.summary_to_model(summary)
        if summary.longitude or summary.latitude:
            # Обновляем локацию, если изменяются координаты
            place = await self.update_place_location(place, summary)
        matched_rows = await self.places_repository.update_model(
            primary_key, **place.dict(exclude_unset=True)
        )
        await self.session.commit()

        self.publish_country_event(place)

        return matched_rows

    async def delete_place(self, primary_key: int) -> Optional[int]:
        """
        Удаление объекта любимого места по его идентификатору.

        :param primary_key: Идентификатор объекта.
        :return:
        """

        matched_rows = await self.places_repository.delete_by(id=primary_key)
        await self.session.commit()

        return matched_rows
