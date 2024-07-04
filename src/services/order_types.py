from src.database.models import OrderType
from src.database.repository import AbstractRepository


class OrderTypesService:
    """Service class for managing order types."""

    def __init__(self, repo: AbstractRepository):
        """
        Initialize OrderTypesService with a repository.

        Args:
            repo (AbstractRepository): Repository implementing database operations.
        """

        self.repo: AbstractRepository = repo()

    async def get_order_types(self) -> list[OrderType]:
        """
        Retrieve a list of all available order types.

        Returns:
            list[OrderType]: List of order type objects.
        """

        res = await self.repo.find_all()
        return res

