from importlib import import_module
from pathlib import Path
from typing import List, Optional

import typer

from erdantic.enums import Orientation
from erdantic.erd import create
from erdantic.exceptions import ModelOrModuleNotFoundError


app = typer.Typer()


@app.command()
def main(
    models_or_modules: List[str] = typer.Argument(
        ...,
        help=(
            "One or more full dotted paths for data model classes, or modules containing data "
            "model classes, to include in diagram, e.g., 'erdantic.examples.pydantic.Party'. Only "
            "the root models of composition trees are needed; erdantic will traverse the "
            "composition tree to find component classes."
        ),
    ),
    out: Path = typer.Option(None, "--out", "-o", help="Output filename."),
    depth_limit: Optional[int] = typer.Option(
        1,
        "--depth",
        "-d",
        help=(
            "The depth to which dependent classes should be searched"
        )
    ),
    include_dot: Optional[bool] = typer.Option(
        False,
        "--include-dot",
        "-i",
        help="Write out a corresponding Graphviz DOT file"
    ),
    vertical: Optional[bool] = typer.Option(
        False,
        "--vertical",
        "-v",
        help="Whether the graph should be drawn as a portrait"
    )
):
    """Draw entity relationship diagrams (ERDs) for Python data model classes. Diagrams are
    rendered using the Graphviz library. Currently supported data modeling frameworks are Pydantic
    and standard library dataclasses.
    """
    orientation = Orientation.VERTICAL if vertical else Orientation.HORIZONTAL

    model_or_module_objs = [import_object_from_name(mm) for mm in models_or_modules]
    diagram = create(
        *model_or_module_objs,
        depth_limit=depth_limit,
        orientation=orientation
    )

    if out:
        if include_dot:
            with open(str(out) + ".dot", "w") as dot_file:
                dot_file.write(diagram.to_dot())

        diagram.draw(out)
        typer.echo(f"Rendered diagram to {out} and .dot to {out}.dot")
    else:
        typer.echo(diagram.to_dot())


def import_object_from_name(full_obj_name):
    # Try to import as a module
    try:
        return import_module(full_obj_name)
    except ModuleNotFoundError:
        try:
            module_name, obj_name = full_obj_name.rsplit(".", 1)
            module = import_module(module_name)
            return getattr(module, obj_name)
        except (ImportError, AttributeError):
            raise ModelOrModuleNotFoundError(f"{full_obj_name} not found")
