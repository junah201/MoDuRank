import importlib.util
import inspect
import os
import sys
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pydantic.json_schema import GenerateJsonSchema

from openapi.models import ModelField
from shared.parser.params import Body, Path, Query
from shared.parser.utils import get_args, is_annotated

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REF_TEMPLATE = "#/components/schemas/{model}"


def import_module_from_file(filepath: str):
    """Dynamically imports a Python module from a given file path."""
    module_name = os.path.basename(filepath).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore
    return module


def extract_middleware_functions(directory: str = "lambdas") -> list:
    functions = []

    # Walk through the directory to find Python files
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):  # Only process Python files
                file_path = os.path.join(root, file)

                # Dynamically import the module
                module = import_module_from_file(file_path)

                # Check for functions decorated with the middleware decorator
                for name, func in inspect.getmembers(module, inspect.isfunction):
                    # Check if the function has the middleware decorator
                    if name in ["handler", "lambda_handler"]:
                        functions.append(func)

    functions.sort(key=lambda x: getattr(x, "path", ""))

    return functions


def get_model(name: str, type_: Any, field: FieldInfo) -> ModelField:
    field.annotation = type_
    return ModelField(
        name=name,
        field_info=field,
        mode="validation",
    )


def get_openapi_from_func(func: Callable) -> tuple[dict, dict]:
    operater = {}
    components = {}

    path: str = getattr(func, "path", None)  # type: ignore
    method: str = getattr(func, "method", None)  # type: ignore
    tags: list[str] = getattr(func, "tags", [])  # type: ignore

    openapi_path_spec = {
        "summary": f"{func.__name__} summary",
        "operationId": f"{path}-{method}",
        "responses": {
            "200": {
                "description": "Successful operation",
                "content": {"application/json": {"schema": {"type": "object", "properties": {}}}},
            },
        },
        "parameters": [],
        "tags": tags,
    }

    signature = inspect.signature(func)

    for name, param in signature.parameters.items():
        if name in ["event", "_event", "context", "_context"]:
            continue

        annotation = param.annotation
        if not is_annotated(annotation):
            continue

        base_type, metadata, *_ = get_args(annotation)

        if not issubclass(base_type, BaseModel | str | int):
            raise ValueError("Annotated type hint must be subclass of BaseModel, str or int")

        openapi_examples = getattr(metadata, "openapi_examples", None)
        if issubclass(base_type, BaseModel):
            schema = base_type.model_json_schema()
            schema_name = f"{path.strip('./')}-{method}-{base_type.__name__}"
            components[schema_name] = schema

            if isinstance(metadata, Body):
                openapi_path_spec["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": f"{REF_TEMPLATE.format(model=schema_name)}",
                            },
                        },
                    },
                }
                if openapi_examples:
                    openapi_path_spec["requestBody"]["content"]["application/json"]["examples"] = openapi_examples
            elif isinstance(metadata, Path | Query):
                openapi_path_spec["parameters"].append(
                    {
                        "name": name,
                        "in": metadata.in_.value,
                        "required": metadata.is_required(),
                        "schema": schema,
                    }
                )
                if openapi_examples:
                    openapi_path_spec["parameters"][-1]["examples"] = openapi_examples
        elif issubclass(base_type, str | int):
            schema_generator = GenerateJsonSchema(ref_template=REF_TEMPLATE)
            if isinstance(metadata, Body):
                model = get_model(name, base_type, metadata)
                inputs = [(model, model.mode, model._type_adapter.core_schema)]
                field_mapping, definitions = schema_generator.generate_definitions(inputs=inputs)  # type: ignore

                openapi_path_spec["requestBody"] = {
                    "required": metadata.is_required(),
                    "content": {
                        "application/json": {
                            "schema": field_mapping[(model, model.mode)],
                        },
                    },
                }
                if openapi_examples:
                    openapi_path_spec["requestBody"]["content"]["application/json"]["examples"] = openapi_examples
            if isinstance(metadata, Path | Query):
                model = get_model(name, base_type, metadata)
                inputs = [(model, model.mode, model._type_adapter.core_schema)]
                field_mapping, definitions = schema_generator.generate_definitions(inputs=inputs)  # type: ignore

                openapi_path_spec["parameters"].append(
                    {
                        "name": name,
                        "in": metadata.in_.value,
                        "required": metadata.is_required(),
                        "schema": field_mapping[(model, model.mode)],
                    }
                )
                if openapi_examples:
                    openapi_path_spec["parameters"][-1]["examples"] = openapi_examples
        else:
            raise ValueError("Invalid type hint")

    # Add path to openapi_spec
    operater[path] = {method.lower(): openapi_path_spec}

    return operater, components


def get_openapi():
    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "API for api.modurank.junah.dev",
            "version": "1.0.0",
        },
        "paths": {},
        "components": {"schemas": {}},
        "servers": [
            {
                "url": "https://api.modurank.junah.dev",
                "description": "Production server",
            }
        ],
    }
    functions = extract_middleware_functions()

    for func in functions:
        operater, components = get_openapi_from_func(func)
        openapi_spec["paths"].update(operater)
        openapi_spec["components"]["schemas"].update(components)

    return openapi_spec
