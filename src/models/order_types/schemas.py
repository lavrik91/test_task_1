from enum import Enum

from pydantic import BaseModel, ConfigDict


class OrderTypeEnum(str, Enum):
    CLOTHING = 'Clothing'
    ELECTRONICS = 'Electronics'
    MISCELLANEOUS = 'Miscellaneous'


class OrderTypeSchemas(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)
