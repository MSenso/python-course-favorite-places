from typing import Any

from fastapi import APIRouter, Depends, status

from exceptions import ApiHTTPException, ObjectNotFoundException
from fastapi_pagination.bases import AbstractPage
from schemas.places import PlaceResponse, PlacesListResponse, PlaceModel, PlaceSummary, PlaceAutoSummary
from schemas.routes import MetadataTag
from services.places_service import PlacesService
from fastapi_pagination import Page, add_pagination, paginate

router = APIRouter()

tag_places = MetadataTag(
    name="places",
    description="Управление любимыми местами.",
)


@router.get(
    "",
    summary="Получение списка объектов",
    response_model=Page[PlaceModel],
)
async def get_list(places_service: PlacesService = Depends(),
                   ) -> AbstractPage[Any]:
    """
    Получение списка любимых мест.

    :param places_service: Сервис для работы с информацией о любимых местах.
    :return:
    """

    return paginate(await places_service.get_places_list())


@router.get(
    "/{primary_key}",
    summary="Получение объекта по его идентификатору",
    response_model=PlaceResponse,
)
async def get_one(
        primary_key: int, places_service: PlacesService = Depends()
) -> PlaceResponse:
    """
    Получение объекта любимого места по его идентификатору.

    :param primary_key: Идентификатор объекта.
    :param places_service: Сервис для работы с информацией о любимых местах.
    :return:
    """

    if place := await places_service.get_place(primary_key):
        return PlaceResponse(data=place)

    raise ObjectNotFoundException


@router.post(
    "",
    summary="Создание нового объекта",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
        place: PlaceSummary, places_service: PlacesService = Depends()
) -> PlaceResponse:
    """
    Создание нового объекта любимого места по переданным данным.

    :param place: Данные создаваемого объекта.
    :param places_service: Сервис для работы с информацией о любимых местах.
    :return:
    """

    if primary_key := await places_service.create_place(place):
        return PlaceResponse(data=await places_service.get_place(primary_key))

    raise ApiHTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Объект не был создан",
    )


@router.patch(
    "/{primary_key}",
    summary="Обновление объекта по его идентификатору",
    response_model=PlaceResponse,
)
async def update(
        primary_key: int, place: PlaceSummary, places_service: PlacesService = Depends()
) -> PlaceResponse:
    """
    Обновление объекта любимого места по переданным данным.

    :param primary_key: Идентификатор объекта.
    :param place: Данные для обновления объекта.
    :param places_service: Сервис для работы с информацией о любимых местах.
    :return:
    """

    if not await places_service.update_place(primary_key, place):
        raise ObjectNotFoundException

    return PlaceResponse(data=await places_service.get_place(primary_key))


@router.delete(
    "/{primary_key}",
    summary="Удаление объекта по его идентификатору",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(primary_key: int, places_service: PlacesService = Depends()) -> None:
    """
    Удаление объекта любимого места по его идентификатору.

    :param primary_key: Идентификатор объекта.
    :param places_service: Сервис для работы с информацией о любимых местах.
    :return:
    """

    if not await places_service.delete_place(primary_key):
        raise ObjectNotFoundException


@router.post(
    "/auto",
    summary="Создание нового объекта с автоматическим определением координат",
    response_model=PlaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_auto(place_auto: PlaceAutoSummary, places_service: PlacesService = Depends()
                      ) -> PlaceResponse:
    """
    Создание нового объекта любимого места с автоматическим определением координат.

    :return:
    """

    place = PlaceSummary(latitude=None,
                         longitude=None,
                         description=place_auto.description)
    if primary_key := await places_service.create_place(place):
        return PlaceResponse(data=await places_service.get_place(primary_key))

    raise ApiHTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Объект не был создан",
    )


add_pagination(router)
