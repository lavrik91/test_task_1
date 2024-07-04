from typing import List, Annotated
from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from src.services.order_types import OrderTypesService
from src.models.order_types.dependencies import order_type_service
from src.models.order_types.schemas import OrderTypeSchemas
from src.database.transaction import transaction

router = APIRouter()


@router.get('/order_type_list', response_model=List[OrderTypeSchemas], status_code=status.HTTP_200_OK)
@cache(expire=None)
@transaction
async def get_types_order_list(
        service: Annotated[OrderTypesService, Depends(order_type_service)]
):
    """
    Endpoint to retrieve all available order types.

    Args:
        service (OrderTypesService): Service dependency for retrieving order types.

    Returns:
        List[OrderTypeSchema]: List of order type schemas.

    Raises:
        HTTPException: If no order types are found (status code 404).
    """

    order_types = await service.get_order_types()
    return order_types
