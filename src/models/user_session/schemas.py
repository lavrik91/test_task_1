from pydantic import BaseModel, ConfigDict


class UserSessionSchemas(BaseModel):
    id: int
    session_id: str

    model_config = ConfigDict(from_attributes=True)
