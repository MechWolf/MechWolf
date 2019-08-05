# type: ignore

import inspect
from pathlib import Path

import mechwolf as mw

NO_EDIT_HEADER = "---\neditLink: false\n---\n"


def format_signature(obj):
    declaration = ""
    if inspect.isfunction(obj):
        declaration = "def "
    elif inspect.isclass(obj):
        declaration = "class "
    return (
        "```python\n"
        + declaration
        + obj.__name__
        + str(inspect.signature(obj))
        + "\n```\n\n"
        + str(inspect.getdoc(obj))
        + "\n\n"
    )


def add_badges(obj):
    res = ""
    if obj.metadata["stability"] == "stable" and obj["supported"]:
        res += ' <Badge text="Supported" type="tip"/>'
    if obj.metadata["stability"] == "beta":
        res += ' <Badge text="Beta" type="warn"/>'
    if not obj.metadata["supported"]:
        res += ' <Badge text="Unsupported" type="error"/>'
    return res


def generate_obj_md(cls, title=None, header=NO_EDIT_HEADER):
    res = header  # the YAML header
    if title is None:
        res += f"# {cls.__name__}"  # the title of the class
    else:
        res += title
    # add badges, if applicable
    try:
        res += add_badges(cls)
        res += "\n\n"
    # core and stdlib classes don't have metadata right now
    except AttributeError:
        res += "\n\n"

    res += format_signature(cls) + "\n"  # get the docstring

    # add contact info, if possible
    try:
        cls.metadata, cls.metadata["supported"], cls.metadata["author"]
        res += f"""Built and {"" if cls.metadata["supported"] else "formerly"} maintained by:

<table>
  <tr>
    <th>Author</th>
    <th>Institution</th>
    <th>GitHub</th>
  </tr>
"""
        for author in cls.metadata["author"]:
            res += f"""
<tr>
  <td>
    <a href='mailto:{author['email']}?subject={cls.__name__}'>{author['first_name']} {author['last_name']}</a>
  </td>
  <td>
    {author["institution"]}
  </td>
  <td>
    <a href="https://github.com/{author["github_username"]}">@{author["github_username"]}</a>
  </td>
</tr>
"""
        res += "</table>\n\n"
    except (AttributeError, KeyError):
        pass

    for method in inspect.getmembers(cls):  # now repeat for the methods
        if (
            not inspect.isfunction(method[1])
            or method[0][0] == "_"
            or inspect.isdatadescriptor(method[1])
        ):
            continue
        res += "## " + method[0] + "\n\n"
        res += format_signature(method[1])
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
    docs = generate_obj_md(cls)
    path = Path("api/core/")
    path.mkdir(exist_ok=True, parents=True)
    (path / (cls.__name__.lower() + ".md")).write_text(docs)

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
        docs = generate_obj_md(cls[1])
        path = Path(
            inspect.getmodule(cls[1])
            .__name__.replace(".", "/")
            .replace("mechwolf", "api")
            + ".md"
        )
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(docs)

print("Generating docs for zoo")
for module in inspect.getmembers(mw.zoo):
    docs = ""
    if module[0][0] != "_":  # exclude internal methods
        # note that for the zoo, it's one file per module
        docs += f"# {module[0]} " + add_badges(module[1]) + "\n"  # add the title
        docs += inspect.getdoc(module[1]) + "\n\n"  # add the module docstring
        for submodule in inspect.getmembers(module[1]):  # we want its members
            # but not internal ones or recursive submodules (such as mw imports)
            if submodule[0][0] != "_" and not inspect.ismodule(submodule[1]):
                # yet another hack
                if submodule[0] == "metadata":
                    continue
                # we document each function or class as second level items
                docs += generate_obj_md(
                    submodule[1], header="", title=f"## {submodule[0]}"
                )
                docs += "\n"
        path = Path("api/zoo/" + module[0] + ".md")
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text(docs)

print("Generating docs for plugins")
plugins = f"{NO_EDIT_HEADER}\n# Plugins\n"
for fn in inspect.getmembers(mw.plugins):
    if fn[0][0] == "_" or not inspect.isfunction(fn[1]):
        continue
    plugins += generate_obj_md(fn[1], header="", title=f"## {fn[1].__name__}") + "\n"
path = Path("api/plugins.md")
path.parent.mkdir(exist_ok=True, parents=True)
path.write_text(plugins)
