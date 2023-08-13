from datetime import datetime

from pydantic import BaseModel

from dto.mark_dto import MarkOutDto
from dto.review_dto import ReviewOutDto


class MessageCreateDto(BaseModel):
    chat_id: int
    query: str | None = None
    answer: str | None = None
    sql: str | None = None
    table: str | None = None
    exception: str | None = None


class MessageOutDto(MessageCreateDto):
    id: int
    created_at: datetime
    review: list[ReviewOutDto] | None = None
    mark: MarkOutDto | None = None