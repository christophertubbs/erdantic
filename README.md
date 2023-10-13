# erdantic: Entity Relationship Diagrams

**erdantic** is a simple tool for drawing [entity relationship diagrams (ERDs)](https://en.wikipedia.org/wiki/Data_modeling#Entity%E2%80%93relationship_diagrams) for Python data model classes. Diagrams are rendered using the venerable [Graphviz](https://graphviz.org/) library. Supported data modeling frameworks are:

- [Pydantic V1](https://docs.pydantic.dev/1.10/)
- [dataclasses](https://docs.python.org/3/library/dataclasses.html) from the Python standard library

Features include a convenient CLI, automatic native rendering in Jupyter notebooks, and easy extensibility to other data modeling frameworks. Docstrings are even accessible as tooltips for SVG outputs. Great for adding a simple and clean data model reference to your documentation.

<object type="image/svg+xml" data="https://raw.githubusercontent.com/drivendataorg/erdantic/main/docs/docs/examples/pydantic.svg" width="100%" typemustmatch><img alt="Example diagram created by erdantic" src="https://raw.githubusercontent.com/drivendataorg/erdantic/main/docs/docs/examples/pydantic.svg"></object>

## Installation

erdantic's graph modeling depends on [pygraphviz](https://pygraphviz.github.io/documentation/stable/index.html) and [Graphviz](https://graphviz.org/), an open-source C library.

When installing via pip, just call:

```bash
pip install git+https://github.com/christophertubbs/erdantic.git
```

## Quick Usage

The fastest way to produce a diagram like the above example is to use the erdantic CLI. Simply specify the full dotted path to your data model class and an output path. The rendered format is interpreted from the filename extension.

```bash
erdantic erdantic.examples.pydantic.Party -o diagram.png
```

You can also import the erdantic Python library and use its functions.

```python
import erdantic as erd
from erdantic.examples.pydantic import Party

# Easy one-liner
erd.draw(Party, out="diagram.png")

# Or create a diagram object that you can inspect and do stuff with
diagram = erd.create(Party)
diagram.models
#> [PydanticModel(Adventurer), PydanticModel(Party), PydanticModel(Quest), PydanticModel(QuestGiver)]
diagram.draw("diagram.png")
```

Check out the "Usage Examples" section of our [docs](https://erdantic.drivendata.org/) to see more.
