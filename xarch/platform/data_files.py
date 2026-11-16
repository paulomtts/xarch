"""Reading YAML and JSON data files into plain Python values, and writing a value as JSON. Knows no module.

Both parsers refuse a mapping that repeats a key, which they would otherwise resolve silently by keeping the last.
"""
from __future__ import annotations

import json
from typing import Any

import yaml


class DataFileError(ValueError):
    """The text is not a valid data file; problems lists every reason found, each safe to show as-is."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = tuple(problems)


class DataFileReader:
    def parse(self, text: str, json_syntax: bool = False) -> Any:
        """The parsed document, as YAML or, with json_syntax, as JSON; raises DataFileError."""
        return _parse_json(text) if json_syntax else _parse_yaml(text)


class _Loader(yaml.SafeLoader):
    duplicates: list[str]


def _mapping(loader: _Loader, node: yaml.MappingNode) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=True)
        try:
            seen = key in result
        except TypeError:
            raise yaml.constructor.ConstructorError(None, None, "a mapping key must be a plain value",
                                                    key_node.start_mark) from None
        if seen:
            loader.duplicates.append(f"line {key_node.start_mark.line + 1}: duplicate key '{key}'")
        result[key] = loader.construct_object(value_node, deep=True)
    return result


_Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def _parse_yaml(text: str) -> Any:
    loader = _Loader(text)
    loader.duplicates = []
    try:
        document = loader.get_single_data()
    except yaml.MarkedYAMLError as e:
        mark = e.problem_mark or e.context_mark
        where = f"line {mark.line + 1}, column {mark.column + 1}: " if mark else ""
        raise DataFileError([f"not valid YAML: {where}{e.problem or e.context}"]) from e
    except yaml.YAMLError as e:
        raise DataFileError([f"not valid YAML: {_one_line(e)}"]) from e
    except RecursionError as e:
        raise DataFileError(["not valid YAML: nested too deeply"]) from e
    finally:
        loader.dispose()
    if loader.duplicates:
        raise DataFileError(loader.duplicates)
    return document


def _parse_json(text: str) -> Any:
    duplicates: list[str] = []

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                duplicates.append(f"duplicate key '{key}'")
            result[key] = value
        return result

    try:
        document = json.loads(text, object_pairs_hook=pairs)
    except (ValueError, RecursionError) as e:
        raise DataFileError([f"not valid JSON: {_one_line(e)}"]) from e
    if duplicates:
        raise DataFileError(duplicates)
    return document


def _one_line(error: Exception) -> str:
    return " ".join(str(error).split())


class DataFileWriter:
    def json(self, value: Any) -> str:
        """The value as a JSON document, two spaces to a level, its keys in the order given, ending in a new line;
        raises ValueError for a value JSON cannot hold."""
        return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
