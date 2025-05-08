# Project description

Intelligent appending text to file names, considering file extensions
and file tags

## Usage

``` bash
./appendfilename.py [<options>] <list of files>
```

This tool inserts text between the old file name and optional tags or
file extension.

Text within file names is placed between the actual file name and the
file extension or (if found) between the actual file namd and a set of
tags separated with a space as in

``` example
Update for the Boss <NEW TEXT HERE>.pptx
2013-05-16T15.31.42 Error message <NEW TEXT HERE> screenshot projectB.png
```

## Example usages

Command

``` bash
./appendfilename.py --text="of projectA" "the presentation.pptx"
```

results in file `"the presentation of projectA.pptx"`.

Next,

``` bash
appendfilename.py "2013-05-09T16.17_img_00042 - fun.jpeg"
```

with the interactive input of `Peter` yields file
`"2013-05-09T16.17_img_00042 Peter - fun.jpeg"`.
