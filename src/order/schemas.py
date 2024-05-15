from decimal import Decimal
from enum import Enum
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, Field, UUID4, ConfigDict


class OrderTypeEnum(str, Enum):
    CLOTHING = 'Clothing'
    ELECTRONICS = 'Electronics'
    MISCELLANEOUS = 'Miscellaneous'


class OrderListQueryParamsSchemas(BaseModel):
    order_type: Optional[OrderTypeEnum] = Query(None,
                                                description="Type of the order: Clothing, Electronics, Miscellaneous")
    is_calculated: Optional[bool] = Query(True, description="Whether the cost of the order is calculated")


class OrderIdSchemas(BaseModel):
    id: UUID4


class CreateOrderSchemas(BaseModel):
    name: str
    weight: Decimal
    cost: Decimal
    order_type_name: OrderTypeEnum = Field(default='Clothing', description="Type of the order",
                                           examples=['Clothing', 'Electronics', 'Miscellaneous'])

    model_config = ConfigDict(from_attributes=True)


class OrderSchemas(CreateOrderSchemas):
    id: UUID4
    delivery_cost: Optional[str] = Field(None, description="The delivery cost of the order, if calculated.")


class OrderTypeSchemas(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True