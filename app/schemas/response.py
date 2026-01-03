from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    message: str
    data: Optional[Any] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )
