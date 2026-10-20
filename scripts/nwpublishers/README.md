# nwreadinglist

## Introduction

This packages consists of the following modules:

- `nwreadinglist` is a library that can run several automated data analysis tasks on a reading list and save the results as a PDF report. It's designed to facilitate and gamify a continuous learning journey.
- `nwreadinglistcli` is a command-line application built on the top of `nwreadinglist`.

## Pre-Requisites

In order to work, this library requires to be run against a local Git repository and that Git itself is installed on the machine.

## Getting Started

I'll use Debian as operating system, but the concept is similar for Windows or Mac.

Procedure:

1. Install `pip` and `venv`:

```sh
sudo apt install python3-pip python3.12-venv
```

2. Create a virtual environment:

```sh
python3 -m venv /tmp/nwreadinglist
source /tmp/nwreadinglist/bin/activate
```

3. Download and install the package:

```sh
pip install nwreadinglist
```

4. Enter in the interactive Python environment:

```sh
python3
```
```
Python 3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

5. Try out if the library works:

```python
from nwreadinglist import RLReportManager

report_manager : RLReportManager = RLReportManager()
```

6. Exit from the interactive Python environment:

```python
exit()
```

7. Try out if the CLI application works:

```sh
nwreadinglistcli
```

8. Deactivate and delete the virtual environment:

```sh
deactivate
rm -rf /tmp/nwreadinglist
```

9. Done!

## Examples

Run it against a reading list:

```sh
root@e584fefc57f0:/# alias nwread="python src/nwreadinglistcli.py"
root@e584fefc57f0:/# nwread --input_path "/data/Reading List.xlsx" --nrow 371 
```

```
*****************************************************************
'##::: ##:'##:::::'##:'########::'########::::'###::::'########::
 ###:: ##: ##:'##: ##: ##.... ##: ##.....::::'## ##::: ##.... ##:
 ####: ##: ##: ##: ##: ##:::: ##: ##::::::::'##:. ##:: ##:::: ##:
 ## ## ##: ##: ##: ##: ########:: ######:::'##:::. ##: ##:::: ##:
 ##. ####: ##: ##: ##: ##.. ##::: ##...:::: #########: ##:::: ##:
 ##:. ###: ##: ##: ##: ##::. ##:: ##::::::: ##.... ##: ##:::: ##:
 ##::. ##:. ###. ###:: ##:::. ##: ########: ##:::: ##: ########::
..::::..:::...::...:::..:::::..::........::..:::::..::........:::
**********************************************Version: 6.1.0*****

command: 'save'
input_path: '/data/Reading List.xlsx'
nrows: '389'
folder_path: 'None'

The PDF report has been successfully saved.
```

Run it against a reading list with custom `folder_path`:

```sh
root@e584fefc57f0:/# alias nwread="python src/nwreadinglistcli.py"
root@e584fefc57f0:/# nwread --input_path "/data/Reading List.xlsx" --nrow 371 --folder_path "/home/nwreadinglist/"
```

## Links

- Source: https://github.com/numbworks/nwreadinglist
- License: https://github.com/numbworks/nwreadinglist/blob/master/LICENSE

## Total Downloads (PyPi)

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/nwreadinglist?period=total&units=NONE&left_color=BLACK&right_color=BLUE&left_text=TOTAL+DOWNLOADS)](https://pepy.tech/projects/nwreadinglist)