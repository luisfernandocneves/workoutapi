from typing import Annotated

from pydantic import Field
from workoutapi.contrib.schemas import BaseSchema


class Categoria(BaseSchema):
    nome: Annotated[
        str, Field(description="Nome da Categoria", example="Sacale", max_length=10)
    ]
