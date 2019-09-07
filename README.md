# pypdftool
tool for standart pdf change

## use

one argument - path to file options.json, when other parameters

example of file options in repo

now tool can add to pdf file text in frame

options.json content
````json
inputFile: string // when stay out use '%newpdf%' - created new pdf A4
outputFile: string // when inputFile stay out - required, when inputFile have existing file can stay out and be used value from inputFile
reconstructPDF: bool // when PDF xref first line start not from 0, tool will copy input file, and replace 0 to start at the first xref line
mod: object // required
mod.type: string // default 'addText', other values not work yet
mod.text: array // array of string, required
mod.textColor: string // hex color format, default: #000000
mod.borderColor: string // hex color format, default: #000000
mod.borderWidth: int // default: 0
mod.fontName: string // default: Verdana, if Verdana can not find in system, be used first font from input pdf
mod.fontSize: int // default: 20
mod.fontBold: bool // default: false
mod.pageNumber: int // default: 1, if value == 0, will print for each page
mod.left: int // per cent, default: 10
mod.top: int // per cent, default: 10
mod.angle: int // deg counterclockwise, default: 0
mod.align: string // default: 'left', another values: 'center', 'right'
mod.topPadding: int // default: 0
mod.leftPadding: int // default: 0
mod.rightPadding: int // default: 0
mod.bottomPadding: int // default: 0
````

#### todo

- add img (need code for add img in pdf file like text now)
- coords (need to more understand how to correctly locate additions with processing their size)