from src.database.repository import AbstractRepository
from src.database.models import UserSession


class UserSessionService:
    """Service class for managing user sessions."""

    def __init__(self, repo: AbstractRepository):
        """
        Initialize UserSessionService with a repository.

        Args:
            repo (AbstractRepository): Repository implementing database operations.
        """
        self.repo: AbstractRepository = repo()

    async def create(self, payload: dict) -> UserSession:
        """
        Create a new user session based on the provided data.

        Args:
            payload (dict): Dictionary containing the data needed to create a user session.

        Returns:
            UserSession: Created user session object.
        """

        res = await self.repo.create(payload)
        return res
