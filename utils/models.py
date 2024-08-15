from typing import Union, Literal
from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    category: Literal["human", "animal"] = "human"
    price: float
    tax: Union[float, None] = None
