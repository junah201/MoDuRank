from typing import Annotated, Any

from typing_extensions import Doc

from shared.parser import params


def Path(  # noqa: N802
    default: Annotated[Any, Doc("Default value if the parameter field is not set.")] = ...,
    *,
    min_length: Annotated[int | None, Doc("Minimum length for strings.")] = None,
    max_length: Annotated[int | None, Doc("Maximum length for strings.")] = None,
    openapi_examples: Annotated[dict[str, Any] | None, Doc("OpenAPI examples for the parameter.")] = None,
    json_schema_extra: dict[str, Any] | None = None,
) -> Any:
    return params.Path(
        default=default,
        min_length=min_length,
        max_length=max_length,
        openapi_examples=openapi_examples,
        json_schema_extra=json_schema_extra,
    )


def Query(  # noqa: N802
    default: Annotated[Any, Doc("Default value if the parameter field is not set.")] = ...,
    *,
    min_length: Annotated[int | None, Doc("Minimum length for strings.")] = None,
    max_length: Annotated[int | None, Doc("Maximum length for strings.")] = None,
    openapi_examples: Annotated[dict[str, Any] | None, Doc("OpenAPI examples for the parameter.")] = None,
    json_schema_extra: dict[str, Any] | None = None,
) -> Any:
    return params.Query(
        default=default,
        min_length=min_length,
        max_length=max_length,
        openapi_examples=openapi_examples,
        json_schema_extra=json_schema_extra,
    )


def Body(  # noqa: N802
    default: Annotated[Any, Doc("Default value if the parameter field is not set.")] = ...,
    *,
    openapi_examples: Annotated[dict[str, Any] | None, Doc("OpenAPI examples for the parameter.")] = None,
    json_schema_extra: dict[str, Any] | None = None,
) -> Any:
    return params.Body(
        default=default,
        openapi_examples=openapi_examples,
        json_schema_extra=json_schema_extra,
    )
