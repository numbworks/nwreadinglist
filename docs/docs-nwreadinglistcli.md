# nwreadinglistcli
Contact: numbworks@gmail.com

## Revision History

| Date | Author | Description |
|---|---|---|
| 2026-05-12 | numbworks | Created. |
| 2026-07-04 | numbworks | Last update (6.0.1). |

## Introduction

`nwreadinglistcli` is a command-line application built on the top of `nwreadinglist`.

## CLI Reference

|*Command*|*Sub Command*|Options|Exit Codes|
|---|---|---|---|
|||*--help, -h*|Success|
|save||--input_path <br/> --nrows <br/> *--folder_path*|Success<br/>Failure|

|Option|Value|Default|
|---|---|---|
|--input_path|`<file path>`|-|
|--nrows|`<int>`|-|
|*--folder_path*|`<folder path>`|-|

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
**********************************************Version: 6.0.0*****

command: 'save'
input_path: '/data/Reading List.xlsx'
nrows: '371'
folder_path: 'None'

The PDF report has been successfully saved.
```

Run it against a reading list with custom `folder_path`:


```sh
root@e584fefc57f0:/# alias nwread="python src/nwreadinglistcli.py"
root@e584fefc57f0:/# nwread --input_path "/data/Reading List.xlsx" --nrow 371 --folder_path "/home/nwreadinglist/"
```

## Markdown Toolset

Suggested toolset to view and edit this Markdown file:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Markdown Preview Enhanced](https://marketplace.visualstudio.com/items?itemName=shd101wyy.markdown-preview-enhanced)
- [Markdown PDF](https://marketplace.visualstudio.com/items?itemName=yzane.markdown-pdf)