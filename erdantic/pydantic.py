from __future__ import annotations

import inspect
import html
import re

from typing import Any, List, Optional, Type

import pydantic
import pydantic.fields

from erdantic.base import Field, Model, register_model_adapter
from erdantic.exceptions import InvalidFieldError, InvalidModelError
from erdantic.typing import repr_type_with_mro

USE_LEGACY = False

HEADER_ROW_COLOR = "#f3f797"
DESCRIPTION_ROW_COLOR = "#fcffcc"
ODD_ROW_COLOR = "#FFFFFF"
EVEN_ROW_COLOR = "#e3e3e3"

CHARACTER_LIMIT = 40
HEADER_CHARACTER_LIMIT = 100

_table_template = """<<table border="0" cellborder="1" cellpadding="5" cellspacing="0">{header}{rows}</table>>"""

_header_template = """<tr><td bgcolor="{row_color}" port="_root" colspan="{column_count}"><b>{name}</b></td></tr>"""
_model_description_template = """<tr><td bgcolor="{row_color}" port="description" colspan="{column_count}"><i>{description}</i></td></tr>"""

_row_template = """<tr><td bgcolor="{row_color}" port="{name}_w">{name}</td><td bgcolor="{row_color}" port="{name}_e">{type_name}</td></tr>"""
_row_with_description = """<tr><td bgcolor="{row_color}" port="{name}_w"><b>{name}</b></td><td bgcolor="{row_color}">{type_name}</td><td bgcolor="{row_color}" port="{name}_e">{description}</td></tr>"""


TEXT_OPTION_PATTERN = re.compile(r'^Union\[(".+",?)+]$')


def get_type_name(field: PydanticField) -> str:
    type_name = field.type_name

    if TEXT_OPTION_PATTERN.search(type_name):
        return "str"

    return type_name


def split_description_lines(message: str, character_limit: int = CHARACTER_LIMIT) -> str:
    if len(message) < character_limit:
        return message

    line_separator = "\n<br></br>"
    lines: List[str] = []

    message = re.sub("\n+", " ", message)
    message = re.sub(" +", " ", message)

    current_message = ""
    message_pieces = message.split(" ")

    for piece in message_pieces:
        if current_message:
            if len(current_message + piece) + 1 > character_limit:
                lines.append(current_message)
                current_message = piece
            else:
                current_message += " " + piece
        else:
            current_message = piece

    if current_message:
        lines.append(current_message)

    return line_separator.join(lines)


def get_model_name_row(name: str, column_count: int = 2) -> str:
    return _header_template.format(name=name, column_count=column_count, row_color=HEADER_ROW_COLOR)


def get_description_row(description: str = None, column_count: int = 2) -> Optional[str]:
    if description:
        description = description[0:description.index("\n\n")] if "\n\n" in description else description
        description = html.escape(description)
        description = split_description_lines(description, HEADER_CHARACTER_LIMIT)
        return _model_description_template.format(description=description, column_count=column_count, row_color=DESCRIPTION_ROW_COLOR)
    return None


def get_header_rows(name: str, description: str = None, column_count: int = 2) -> str:
    rows = [get_model_name_row(name=name, column_count=column_count)]

    description_row = get_description_row(description=description, column_count=column_count)

    if description_row:
        rows.append(description_row)

    return "".join(rows)


def get_field_row(row_index: int, field: PydanticField, render_description: bool = None) -> str:
    # The index is 0-based, but the number for the row is 1s indexed, so add 1 to get the actual row number
    row_number = row_index + 1
    is_odd_row = row_number % 2 == 1
    row_color = ODD_ROW_COLOR if is_odd_row else EVEN_ROW_COLOR

    if render_description is None:
        render_description = field.description is not None

    if render_description:
        description = field.description or ''

        # Format the description to make sure it doesn't stretch the row
        description = html.escape(description)
        description = split_description_lines(description)
        return _row_with_description.format(name=field.name, type_name=field.type_name, description=description, row_color=row_color)

    type_name = get_type_name(field)

    return _row_template.format(name=field.name, type_name=type_name, row_color=row_color)


def get_field_rows(fields: List[PydanticField], render_description: bool) -> str:
    return "".join(
        [
            get_field_row(row_index=index, field=field, render_description=render_description)
            for index, field in enumerate(fields)
        ]
    )


def build_model_table(model: PydanticModel) -> str:
    column_count = 3 if model.has_field_descriptions else 2
    header = get_header_rows(name=model.name, description=model.model_description, column_count=column_count)
    rows = get_field_rows(model.fields, model.has_field_descriptions)
    return _table_template.format(header=header, rows=rows)


class PydanticField(Field[pydantic.fields.ModelField]):
    """Concrete field adapter class for Pydantic fields.

    Attributes:
        field (pydantic.fields.ModelField): The Pydantic field object that is associated with this
            adapter instance.
    """

    def __init__(self, field: pydantic.fields.ModelField):
        if not isinstance(field, pydantic.fields.ModelField):
            raise InvalidFieldError(
                f"field must be of type pydantic.fields.ModelField. Got: {type(field)}"
            )
        super().__init__(field=field)

    @property
    def name(self) -> str:
        return self.field.name

    @property
    def description(self) -> Optional[str]:
        return getattr(self.field.field_info, 'description', None)

    @property
    def type_obj(self) -> Type:
        tp = self.field.outer_type_
        if self.field.allow_none:
            return Optional[tp]
        return tp

    def is_many(self) -> bool:
        return self.field.shape > 1

    def is_nullable(self) -> bool:
        return self.field.allow_none


@register_model_adapter("pydantic")
class PydanticModel(Model[Type[pydantic.BaseModel]]):
    """Concrete model adapter class for a Pydantic
    [`BaseModel`](https://pydantic-docs.helpmanual.io/usage/models/).

    Attributes:
        model (Type[pydantic.BaseModel]): The Pydantic model class that is associated with this
            adapter instance.
        forward_ref_help (Optional[str]): Instructions for how to resolve an unevaluated forward
            reference in a field's type declaration.
    """

    forward_ref_help = (
        "Call 'update_forward_refs' after model is created to resolve. "
        "See: https://pydantic-docs.helpmanual.io/usage/postponed_annotations/"
    )

    def __init__(self, model: Type[pydantic.BaseModel]):
        if not self.is_model_type(model):
            raise InvalidModelError(
                "Argument model must be a subclass of pydantic.BaseModel. "
                f"Got {repr_type_with_mro(model)}"
            )
        super().__init__(model=model)
        self.__fields: List[PydanticField] = []

    @staticmethod
    def is_model_type(obj: Any) -> bool:
        return isinstance(obj, type) and issubclass(obj, pydantic.BaseModel)

    @property
    def fields(self) -> List[PydanticField]:
        if not self.__fields:
            self.__fields = [PydanticField(field=f) for f in self.model.__fields__.values()]
        return self.__fields

    @property
    def has_field_descriptions(self) -> bool:
        for field in self.__fields:
            if field.description:
                return True
        return False

    @property
    def model_description(self) -> Optional[str]:
        return inspect.getdoc(self.model)

    def dot_label(self) -> str:
        """Returns the DOT language "HTML-like" syntax specification of a table for this data
        model. It is used as the `label` attribute of data model's node in the graph's DOT
        representation.

        Returns:
            str: DOT language for table
        """
        if USE_LEGACY:
            return super().dot_label()
        return build_model_table(self)

    @property
    def docstring(self) -> str:
        out = super().docstring
        field_descriptions = [
            getattr(field.field.field_info, "description", None) for field in self.fields
        ]
        if any(descr is not None for descr in field_descriptions):
            # Sometimes Pydantic models have field documentation as descriptions as metadata on the
            # field instead of in the docstring. If detected, construct docstring and add.
            out += "\nAttributes:\n"
            field_defaults = [field.field.field_info.default for field in self.fields]
            for field, descr, default in zip(self.fields, field_descriptions, field_defaults):
                if descr is not None:
                    line = f"{field.name} ({field.type_name}): {descr}"
                    if (
                            not isinstance(default, pydantic.fields.UndefinedType)
                            and default is not ...
                    ):
                        if not line.strip().endswith("."):
                            line = line.rstrip() + ". "
                        else:
                            line = line.rstrip() + " "
                        if isinstance(default, str):
                            line += f"Default is '{default}'."
                        else:
                            line += f"Default is {default}."
                    out += "    " + line.strip() + "\n"

        return out
