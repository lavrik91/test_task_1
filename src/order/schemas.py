from decimal import Decimal
from enum import Enum
from typing import Optional


from pydantic import BaseModel, Field, ConfigDict


class OrderTypeEnum(str, Enum):
    CLOTHING = 'Clothing'
    ELECTRONICS = 'Electronics'
    MISCELLANEOUS = 'Miscellaneous'


class OrderIdSchemas(BaseModel):
    id: str


class CreateOrderSchemas(BaseModel):
    name: str
    weight: Decimal
    cost: Decimal
    order_type_name: OrderTypeEnum = Field(default='Clothing', description="Type of the order",
                                           examples=['Clothing', 'Electronics', 'Miscellaneous'])

    model_config = ConfigDict(from_attributes=True)


class OrderSchemas(CreateOrderSchemas):
    id: str
    delivery_cost: Optional[str] = Field(None, description="The delivery cost of the order, if calculated.")


class OrderTypeSchemas(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserSessionSchemas(BaseModel):
    id: int
    session_id: str

    model_config = ConfigDict(from_attributes=True)

