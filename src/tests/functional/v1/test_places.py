import pytest
from starlette import status

from models import Place
from repositories.places_repository import PlacesRepository


@pytest.mark.usefixtures("session")
class TestPlaces:
    """
    Тестирование метода создания любимого места.
    """
    mock_body = {
        "latitude": 12.3456,
        "longitude": 23.4567,
        "description": "Описание тестового места",
        "city": "City",
        "locality": "Location",
        "country": "AA",
    }

    mock_response = {
        "latitude": 12.3456,
        "longitude": 23.4567,
        "city": "City",
        "description": "Описание тестового места",
        "countryCode": "AA",
        "locality": "Location",
    }

    @staticmethod
    def assert_result(place: dict, response: dict):
        assert place["country"] == response["countryCode"]
        assert place["city"] == response["city"]
        assert place["locality"] == response["locality"]
        assert place["latitude"] == response["latitude"]
        assert place["longitude"] == response["longitude"]
        assert place["description"] == response["description"]

    async def create_place(self, session):
        return await PlacesRepository(session).create_model(self.mock_body)

    @staticmethod
    def get_endpoint() -> str:
        """
        Получение адреса метода API.

        :return:
        """

        return "/api/v1/places"

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("event_producer_publish")
    async def test_create_place(self, client, session, httpx_mock):
        """
        Тестирование создания места.

        :param client: Фикстура клиента для запросов.
        :param session: Фикстура сессии для работы с БД.
        :param httpx_mock: Фикстура запроса на внешние API.
        :return:
        """
        # замена настоящего ответа от API на "заглушку" для тестирования
        # настоящий запрос на API не производится
        httpx_mock.add_response(json=self.mock_response)

        # передаваемые данные
        request_body = {
            "latitude": 12.3456,
            "longitude": 23.4567,
            "description": "Описание тестового места",
        }
        # осуществление запроса
        response = await client.post(
            self.get_endpoint(),
            json=request_body,
        )

        # проверка корректности ответа от сервера
        assert response.status_code == status.HTTP_201_CREATED

        response_json = response.json()
        assert "data" in response_json
        place = response_json["data"]
        assert isinstance(place["id"], int)
        assert isinstance(place["created_at"], str)
        assert isinstance(place["updated_at"], str)
        assert place["latitude"] == request_body["latitude"]
        assert place["longitude"] == request_body["longitude"]
        assert place["description"] == request_body["description"]
        assert place["country"] == self.mock_response["countryCode"]
        assert place["city"] == self.mock_response["city"]
        assert place["locality"] == self.mock_response["locality"]

        # проверка существования записи в базе данных
        created_data = await PlacesRepository(session).find_all_by(
            latitude=request_body["latitude"],
            longitude=request_body["longitude"],
            description=request_body["description"],
            limit=100,
        )
        assert len(created_data) == 1
        assert isinstance(created_data[0], Place)
        assert created_data[0].latitude == request_body["latitude"]
        assert created_data[0].longitude == request_body["longitude"]
        assert created_data[0].description == request_body["description"]
        assert created_data[0].country == self.mock_response["countryCode"]
        assert created_data[0].city == self.mock_response["city"]
        assert created_data[0].locality == self.mock_response["locality"]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("event_producer_publish")
    async def test_auto_route(self, client, session, httpx_mock):
        """
        Тестирование успешного сценария.
        :param client: Фикстура клиента для запросов.
        :param session: Фикстура сессии для работы с БД.
        :param httpx_mock: Фикстура запроса на внешние API.
        :return:
        """
        # замена настоящего ответа от API на "заглушку" для тестирования
        # настоящий запрос на API не производится
        httpx_mock.add_response(json=self.mock_response)

        # передаваемые данные
        request_body = {
            "description": "Описание тестового места",
        }
        # Автоматически определенные координаты
        coordinates = {"latitude": 12.3456, "longitude": 23.4567}

        # осуществление запроса
        response = await client.post(
            self.get_endpoint() + "/auto",
            json=request_body,
        )

        # проверка корректности ответа от сервера
        assert response.status_code == status.HTTP_201_CREATED

        response_json = response.json()

        assert "data" in response_json
        place = response_json["data"]
        assert isinstance(place["id"], int)
        assert isinstance(place["created_at"], str)
        assert isinstance(place["updated_at"], str)
        assert place["latitude"] == coordinates["latitude"]
        assert place["longitude"] == coordinates["longitude"]
        assert place["description"] == request_body["description"]
        assert place["country"] == self.mock_response["countryCode"]
        assert place["city"] == self.mock_response["city"]
        assert place["locality"] == self.mock_response["locality"]

        # проверка существования записи в базе данных
        created_data = await PlacesRepository(session).find_all_by(
            latitude=coordinates["latitude"],
            longitude=coordinates["longitude"],
            description=request_body["description"],
            limit=100,
        )
        assert len(created_data) == 1
        assert isinstance(created_data[0], Place)
        assert created_data[0].latitude == coordinates["latitude"]
        assert created_data[0].longitude == coordinates["longitude"]
        assert created_data[0].description == request_body["description"]
        assert created_data[0].country == self.mock_response["countryCode"]
        assert created_data[0].city == self.mock_response["city"]
        assert created_data[0].locality == self.mock_response["locality"]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("event_producer_publish")
    async def test_get_list(self, client, session):
        """
        Тестирование получения списка мест.
        :param client: Фикстура клиента для запросов.
        :param session: Фикстура сессии для работы с БД.
        :return:
        """

        # создание записи в БД
        await self.create_place(session)

        # осуществление запроса
        response = await client.get(
            self.get_endpoint(),
        )
        # проверка корректности ответа от сервера
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()

        assert len(response_json["items"]) == 1
        place = response_json["items"][0]

        self.assert_result(place, self.mock_response)

        assert response_json["total"] == 1
        assert response_json["page"] == 1
        assert response_json["size"] == 50

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("event_producer_publish")
    async def test_get_one(self, client, session):
        """
        Тестирование получения одного места.
        :param client: Фикстура клиента для запросов.
        :param session: Фикстура сессии для работы с БД.
        :return:
        """

        # создание записи в БД
        created_id = await self.create_place(session)
        # осуществление запроса
        response = await client.get((self.get_endpoint()) + f"/{created_id}")
        # проверка корректности ответа от сервера
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        place = response_json["data"]
        self.assert_result(place, self.mock_response)

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("event_producer_publish")
    async def test_patch_place(self, client, session, httpx_mock):
        """
        Тестирование успешного сценария.
        :param client: Фикстура клиента для запросов.
        :param session: Фикстура сессии для работы с БД.
        :param httpx_mock: Фикстура запроса на внешние API.
        :return:
        """
        # замена настоящего ответа от API на "заглушку" для тестирования
        # настоящий запрос на API не производится
        httpx_mock.add_response(json=self.mock_response)

        # создание записи в БД
        created_id = await self.create_place(session)

        patch_request_body = {
            "latitude": 12.3456,
            "longitude": 23.4567,
            "description": "Описание тестового места",
        }
        # осуществление запроса
        response = await client.patch(
            (self.get_endpoint()) + f"/{created_id}", json=patch_request_body
        )
        # проверка корректности ответа от сервера
        assert response.status_code == status.HTTP_200_OK

        response_json = response.json()
        place = response_json["data"]
        assert place["country"] == self.mock_response["countryCode"]
        assert place["city"] == self.mock_response["city"]
        assert place["locality"] == self.mock_response["locality"]
        assert place["latitude"] == patch_request_body["latitude"]
        assert place["longitude"] == patch_request_body["longitude"]
        assert place["description"] == patch_request_body["description"]

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("event_producer_publish")
    async def test_delete_place(self, client, session):
        """
        Тестирование успешного сценария.
        :param client: Фикстура клиента для запросов.
        :param session: Фикстура сессии для работы с БД.
        :return:
        """
        # создание записи в БД
        created_id = await self.create_place(session)
        # осуществление запроса
        response = await client.delete((self.get_endpoint()) + f"/{created_id}")
        # проверка корректности ответа от сервера
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await client.get((self.get_endpoint()) + f"/{created_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
