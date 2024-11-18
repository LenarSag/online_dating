from pydantic import BaseModel


class TagBase(BaseModel):
    name: str
