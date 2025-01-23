from dataclasses import dataclass
from typing import (
    Annotated,
    Any,
    Literal,
)

from pydantic import TypeAdapter
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined as Undefined


@dataclass
class ModelField:
    field_info: FieldInfo
    name: str
    mode: Literal["validation", "serialization"] = "validation"

    @property
    def alias(self) -> str:
        a = self.field_info.alias
        return a if a is not None else self.name

    @property
    def required(self) -> bool:
        return self.field_info.is_required()

    @property
    def default(self) -> Any:
        return self.get_default()

    @property
    def type_(self) -> Any:
        return self.field_info.annotation

    def __post_init__(self) -> None:
        self._type_adapter: TypeAdapter[Any] = TypeAdapter(Annotated[self.field_info.annotation, self.field_info])

    def get_default(self) -> Any:
        if self.field_info.is_required():
            return Undefined
        return self.field_info.get_default(call_default_factory=True)

    def __hash__(self) -> int:
        return hash(self.name)
