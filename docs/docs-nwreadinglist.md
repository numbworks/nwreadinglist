# nwreadinglist
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2023-08-10 | numbworks | Created. |
| 2026-05-12 | numbworks | Last update (6.0.0). |

## Introduction

`nwreadinglist` is a library that can run several automated data‑analysis tasks on a reading list and save the results as a PDF report. It’s designed to facilitate and gamify a continuous learning journey.

## Architecture

A partial class diagram showing the core architecture of the application:

![Diagram-Architecture.png](Diagrams/Diagram-Architecture.png)

## See Also: `developmentguide`

To get started with this project as a developer, please give a look to the following document:

- [docs-developmentguide-python.md](SeeAlso-developmentguide/docs-developmentguide-python.md)

## See Also: `nwmakefiles`

This project includes portions of the `nwmakefiles` project, which is documented here:

- [docs-nwmakefiles.md](SeeAlso-nwmakefiles/docs-nwmakefiles.md)

## See Also: `asciibannermanager`

This project includes portions of the `asciibannermanager` project, which is documented here:

- [docs-asciibannermanager.md](SeeAlso-asciibannermanager/docs-asciibannermanager.md)

## Known Issues: nwshared

If `nwshared` creates some issues for you, please refer to [its documentation on Github](https://github.com/numbworks/nwshared/blob/master/docs/docs-nwshared.md).

## Known Issues: "ImportError: cannot import name 'display' from 'IPython.core.display'"

Starting `v4.3.0`, the devcontainer's Dockerfile forces `ipkernel` to use a specific version of its `ipython` dependency:

```
FROM python:3.12.5-bookworm

# ...
RUN pip install ipykernel==6.29.5 ipython==7.23.1
# ...
```

Without this enforcement in place, the devcontainer would return the following error message:

> ImportError: cannot import name 'display' from 'IPython.core.display'

By investigating the dependency tree with the following commands:

```
pip install pipdeptree
pipdeptree -p ipykernel
```

I discovered that `ipykernel` has the following (very lousy) dependency constraint:

```
...
├── ipython [required: >=7.23.1, ...
...
```

The `>=` means that, even if your devcontainer uses a frozen version of `ipykernel`, the latest version of `ipython` will be downloaded at each rebuild.

When I started getting the error message, the installed `ipython` version was `9.2.0` (quite far from the original `7.23.1`). 

Forcing `pip` to use an older dependency was necessary to bring back the devcontainer to a working status.

## Known Issues: "ModuleNotFoundError: No module named 'tinycss2.color5'"

At the moment of writing, the latest version of `weasyprint` is `67.0`, but it returns the following error if run via devcontainer:

```
2025-12-22 19:40:18.005 [error] Unittest test discovery error for workspace:  /workspaces/nwreadinglist 
 Failed to import test module: nwreadinglisttests
Traceback (most recent call last):
  File "/usr/local/lib/python3.12/unittest/loader.py", line 396, in _find_test_path
    module = self._get_module_from_name(name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/unittest/loader.py", line 339, in _get_module_from_name
    __import__(name)
  File "/workspaces/nwreadinglist/tests/nwreadinglisttests.py", line 17, in <module>
    from nwreadinglist import RLCN, DEFINITIONSTR, OPTION, REPORTSTR, _MessageCollection, RLSummary, DefaultPathProvider
  File "/workspaces/nwreadinglist/src/nwreadinglist.py", line 25, in <module>
    from weasyprint import CSS, HTML
  File "/usr/local/lib/python3.12/site-packages/weasyprint/__init__.py", line 440, in <module>
    from .css import preprocess_stylesheet  # noqa: I001, E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.12/site-packages/weasyprint/css/__init__.py", line 32, in <module>
    from . import counters, media_queries
  File "/usr/local/lib/python3.12/site-packages/weasyprint/css/counters.py", line 10, in <module>
    from .tokens import remove_whitespace
  File "/usr/local/lib/python3.12/site-packages/weasyprint/css/tokens.py", line 8, in <module>
    from tinycss2.color5 import parse_color
ModuleNotFoundError: No module named 'tinycss2.color5'

2025-12-22 19:40:18.229 [info] Unittest discovery completed for workspace /workspaces/nwreadinglist
```

The root cause of the issue is that `weasyprint 67.0` forces the installation of `tinycss2 1.4.0` (which doesn't support `tinycss2.color5`), and even asking the Dockerfile to enforce the installation of `tinycss2 1.5.0` (which supports `tinycss2.color5`) doesn't work (`tinycss2` stays on `1.4.0`). 

To solve the issue we use the older `weasyprint 66.0`:

```
...
RUN pip install weasyprint==66.0
...
```

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)