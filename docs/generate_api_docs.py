from pathlib import Path


def deindent(x, levels):
    return "\n".join((line[4 * levels :] for line in x.split("\n")))  # noqa


class PyObj(object):
    def __init__(self, source_code):
        self.source_code = source_code.rstrip()

        # calculate the object's name
        name = source_code.lstrip().replace("def ", "").replace("class ", "")
        open_paren_idx = name.index("(")
        self.name = name[:open_paren_idx]

    @property
    def docstring(self):
        try:
            doctring_start_idx = self.source_code.index('"""')
            docstring = self.source_code[
                doctring_start_idx : self.source_code.index(  # noqa
                    '"""', doctring_start_idx + 1
                )
            ][3:-3].rstrip()
            return deindent(docstring, self.indentation_level)
        except ValueError:
            return ""

    @property
    def indentation_level(self):
        indentation_level = 0
        for letter in self.source_code:
            if letter == " ":
                indentation_level += 1
            else:
                break
        if indentation_level % 4:
            raise ValueError(
                "Indentation level is not a multiple of four. Got "
                + str(indentation_level)
                + "spaces"
            )

        return int(float(indentation_level) / 4) + 1

    @property
    def is_internal(self):
        return self.name.startswith("_") and not self.name.startswith("__")


class Function(PyObj):
    def __init__(self, source_code):
        super().__init__(source_code)

    def __repr__(self):
        return "<Function " + self.name + ">"

    @property
    def signature(self):
        return self.source_code[: self.source_code.index(":\n")].lstrip()


class Class(PyObj):
    def __init__(self, source_code):
        super().__init__(source_code)
        self.methods = []

    def __repr__(self):
        return "<Class " + self.name + ">"

    @property
    def parent(self):
        open_paren_idx = self.source_code.index("(")
        close_paren_idx = self.source_code.index(")")
        return self.source_code[open_paren_idx + 1 : close_paren_idx]  # noqa


def analyze_file(filename):
    with open(filename) as f:
        lines = f.readlines()
        classes = []
        for i, line in enumerate(lines):

            # parse classes
            if line.startswith("class "):
                class_str = line
                x = 1
                try:
                    while not lines[i + x].startswith("class "):
                        class_str += lines[i + x]
                        x += 1
                except IndexError:
                    pass
                current_class = Class(class_str)
                classes.append(current_class)

            # parse out functions
            elif line.lstrip().startswith("def "):
                func_str = line
                x = 1
                try:
                    while not lines[i + x].lstrip().startswith("def ") and not lines[
                        i + x
                    ].lstrip().startswith("@property"):
                        func_str += lines[i + x]
                        x += 1
                except IndexError:
                    pass
                current_class.methods.append(Function(func_str))
    if len([_class for _class in classes if not _class.is_internal]) > 1:
        raise ValueError("More than one class per file!")
    try:
        return classes[0]
    except IndexError:
        pass


def generate_markdown(_class):
    if _class is None:
        return ""
    header = "---\neditLink: false\n---\n"

    body = "# " + _class.name + "\n" + _class.docstring + "\n"

    for method in _class.methods:
        if method.is_internal:
            continue
        try:
            body += (
                "## "
                + method.name
                + "\n\n```python\n"
                + deindent(method.signature, 1)
                + "\n```\n"
                + method.docstring.replace("#", "###")
                + "\n\n"
            )
        except ValueError:
            pass

    return header + body


core = Path("../mechwolf/core/")
for f in core.glob("*.py"):
    if f.stem == "__init__":
        continue
    with open("api/core/" + f.stem + ".md", "w+") as _f:
        print(generate_markdown(analyze_file(str(f))), file=_f)

stdlib = Path("../mechwolf/components/stdlib")
for f in stdlib.glob("*.py"):
    if f.stem == "__init__":
        continue
    with open("api/components/stdlib/" + f.stem + ".md", "w+") as _f:
        print(generate_markdown(analyze_file(str(f))), file=_f)


contrib = Path("../mechwolf/components/contrib")
for f in contrib.glob("*.py"):
    if f.stem == "__init__":
        continue
    with open("api/components/contrib/" + f.stem + ".md", "w+") as _f:
        print(generate_markdown(analyze_file(str(f))), file=_f)

# with open("api/stdlib_components.md", "w+") as f:
#     results = {}
#     for filename in [
#         "../mechwolf/components/stdlib/component.py",
#         "../mechwolf/components/stdlib/pump.py",
#         "../mechwolf/components/stdlib/mixer.py",
#     ]:
#         results[filename] = analyze_file(filename)
#     print(generate_markdown(results, "Component Standard Library"), file=f)
