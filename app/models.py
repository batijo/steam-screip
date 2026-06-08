from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Game(BaseModel):
    name: str
    steam_url: str
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
