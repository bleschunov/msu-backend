from pydantic import BaseModel


class QuestionDto(BaseModel):
    id: int
    question: str
