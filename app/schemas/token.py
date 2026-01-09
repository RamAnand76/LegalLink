from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzM1OTg3NjAwfQ.abc123xyz")
    token_type: str = Field(..., example="bearer")


class TokenPayload(BaseModel):
    sub: Optional[int] = Field(None, example=1)
