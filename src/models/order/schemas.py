from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from src.models.order_types.schemas import OrderTypeEnum


class OrderIdSchemas(BaseModel):
    id: str





class CreateOrderSchemas(BaseModel):
    name: str = Field(min_length=1, frozen=True, json_schema_extra={'example': "Jane"})
    weight: Decimal = Field(
        gt=0.01,
        decimal_places=2,
        json_schema_extra={
            "description": "Weight of the order",
            "example": "123.33"
        }
    )
    cost: Decimal = Field(
        gt=0.01,
        decimal_places=2,
        json_schema_extra={
            "description": "Cost of the order",
            "example": "22.22"
        }
    )
    order_type_name: OrderTypeEnum = Field(
        default='Clothing',
        json_schema_extra={
            "description": "Type of the order",
            "examples": ['Clothing', 'Electronics', 'Miscellaneous']
        },
    )

    model_config = ConfigDict(from_attributes=True)


class OrderSchemas(CreateOrderSchemas):
    id: str
    delivery_cost: Optional[str] = Field(
        None,
        json_schema_extra={"description": "The delivery cost of the order, if calculated"}
    )
