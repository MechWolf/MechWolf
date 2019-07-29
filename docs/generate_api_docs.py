# type: ignore

import inspect
from pathlib import Path

import mechwolf as mw


def obj_to_mw_doc(obj):
    return (
        "```python\n"
        + obj.__name__
        + str(inspect.signature(obj))
        + "\n```\n\n"
        + str(inspect.getdoc(obj))
        + "\n\n"
    )


def document_class(cls):
    res = "---\neditLink: false\n---\n"  # the YAML header
    res += f"# {cls.__name__}\n\n"  # the title of the class
    res += obj_to_mw_doc(cls) + "\n"  # get the docstring
    for method in inspect.getmembers(cls):  # now repeat for the methods
        if (
            not inspect.isfunction(method[1])
            or method[0][0] == "_"
            or inspect.isdatadescriptor(method[1])
        ):
            continue
        res += "## " + method[0] + "\n\n"
        res += obj_to_mw_doc(method[1])
    res = (
        res.replace("Arguments:", "### Arguments")
        .replace("Returns:", "### Returns")
        .replace("Raises:", "### Raises")
        .replace("Attributes:", "### Attributes")
        .replace("Examples:", "### Examples")
        .replace("Example:", "### Example")
    )
    return res


# first, do the main objects
for cls in [mw.Apparatus, mw.Protocol, mw.Experiment]:
    print(f"Generating docs for {cls.__name__}")
    docs = document_class(cls)
    Path("api/core/" + cls.__name__.lower() + ".md").write_text(docs)

for module in [mw.components.stdlib, mw.components.contrib]:
    # find out what classes are part of the module
    classes = inspect.getmembers(module)

    # filter out internal modules
    classes = [cls for cls in classes if cls[0][0] != "_" and inspect.isclass(cls[1])]

    # determine the directory name to put it in
    print(f"Generating docs for {module.__name__}")
    for cls in classes:

        # a hack
        if cls[0] == "UnitRegistry":
            continue

        # write it out
        docs = document_class(cls[1])
        Path(
            inspect.getmodule(cls[1])
            .__name__.replace(".", "/")
            .replace("mechwolf", "api")
            + ".md"
        ).write_text(docs)
