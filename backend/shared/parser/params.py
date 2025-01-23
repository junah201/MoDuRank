from enum import Enum
from typing import Any, TypedDict

from pydantic import AnyUrl
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined as Undefined

_Unset: Any = Undefined


class Example(TypedDict, total=False):
    summary: str | None
    description: str | None
    value: Any | None
    externalValue: AnyUrl | None

    __pydantic_config__ = {"extra": "allow"}  # type: ignore [misc]


class ParamType(str, Enum):
    query = "query"
    path = "path"


class Param(FieldInfo):
    in_: ParamType

    def __init__(
        self,
        default: Any = Undefined,
        *,
        min_length: int | None = None,
        max_length: int | None = None,
        openapi_examples: dict[str, Any] | None = None,
        json_schema_extra: dict[str, Any] | None = None,
    ):
        self.openapi_examples = openapi_examples
        super().__init__(
            default=default,
            min_length=min_length,
            max_length=max_length,
            json_schema_extra=json_schema_extra,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.default})"


class Path(Param):
    in_ = ParamType.path

    def __init__(
        self,
        default: Any = ...,
        *,
        min_length: int | None = None,
        max_length: int | None = None,
        openapi_examples: dict[str, Any] | None = None,
        json_schema_extra: dict[str, Any] | None = None,
    ):
        assert default is ..., "Path parameters cannot have a default value"
        self.in_ = self.in_
        super().__init__(
            default=default,
            min_length=min_length,
            max_length=max_length,
            openapi_examples=openapi_examples,
            json_schema_extra=json_schema_extra,
        )


class Query(Param):
    in_ = ParamType.query

    def __init__(
        self,
        default: Any = Undefined,
        *,
        min_length: int | None = None,
        max_length: int | None = None,
        openapi_examples: dict[str, Any] | None = None,
        json_schema_extra: dict[str, Any] | None = None,
    ):
        self.in_ = self.in_
        super().__init__(
            default=default,
            min_length=min_length,
            max_length=max_length,
            openapi_examples=openapi_examples,
            json_schema_extra=json_schema_extra,
        )


class Body(FieldInfo):
    def __init__(
        self,
        default: Any = Undefined,
        *,
        openapi_examples: dict[str, Example] | None = None,
        json_schema_extra: dict[str, Any] | None = None,
    ):
        self.openapi_examples = openapi_examples
        super().__init__(
            default=default,
            json_schema_extra=json_schema_extra,
        )
