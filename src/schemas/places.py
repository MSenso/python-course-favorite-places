from typing import Optional

from pydantic import BaseModel, Field

from models import Place
from schemas.base import ListResponse


class PlaceModel(BaseModel):
    latitude: Optional[float] = Field(title="Широта")
    longitude: Optional[float] = Field(title="Долгота")
    description: Optional[str] = Field(title="Описание", min_length=2, max_length=255)
    country: Optional[str] = Field(
        title="ISO Alpha2-код страны", min_length=2, max_length=2
    )
    city: Optional[str] = Field(title="Название города", min_length=2, max_length=50)
    locality: Optional[str] = Field(
        title="Местонахождение", min_length=2, max_length=255
    )


class PlaceSummary(BaseModel):
    """
    Схема данных для обновления любимого места.
    """

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = Field(None, min_length=3, max_length=255)


class PlaceAutoSummary(BaseModel):
    """
    Схема данных для обновления любимого места.
    """
    description: Optional[str] = Field(None, min_length=3, max_length=255)


class PlaceResponse(BaseModel):
    """
    Схема для представления данных о списке любимых мест.
    """

    data: Place


class PlacesListResponse(ListResponse):
    """
    Схема для представления данных о списке любимых мест.
    """

    data: list[Place]
