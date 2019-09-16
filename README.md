# pypdftool

Tool for basic edit PDF.

Basic edit variants:
 - addText - the insert can be text in several lines, and also the insertion can be inscribed in a rectangle with a frame (you can set some parameters, see below)
 - print - in the PDF will include JavaScript code their in the opening PDF will start printing document (you can set page number for print or zero for print all pages)
 - rotate - in the PDF will rotate page (you can set angle and page number for rotate or zero for rotate all pages).

Text of insertion can be customized using color, fon and size. The color and width of line of the rectangle can also be customized.

#### Requirements

 - PyPDF2
 - ReportLab

## How to use

To use, you must specify the path to the options file as an argument. Options file need JSON format contains one object. Example of options file in repo.

Description of options file:

options.json content
````json
{
	// string - if you need to create an empty document, you can leave this field blank
	"inputFile": "",
	// string - when inputFile empty this field required, when inputFile filled you can leave this field blank and result will saved in inputFile
	"outputFile": "output.pdf",
	// bool - there are files in the cross-link table have a non-zero symbol in the first line (example "xref \n 1 7"), True in this field will mean that first number of the line following the xref will be replaced by 0 (example "xref \n 0 7")
	"reconstructPDF": true,
	// string - default 'result.log' - result file that will contains fields: "result" (bool) and "errorText" (string)
	"resultLog": "result.log",
	// object - contains insertion options
	"mod": 
	{
		// string - default 'addText' - available values: 'addText', 'print', 'rotate' - other values not yet provided
		"type": "addText",
		// array of strings - text to be inserted (only relevant for type 'addText')
		"text": 
		[
		"Line 1\nString-----2",
		"Line 3--"
		],
		// string - default #000000 - hex color format (only relevant for type 'addText')
		"textColor": "#3f48cc",
		// string - default #000000 - hex color format (only relevant for type 'addText')
		"borderColor": "#3f48cc",
		// int - default 0 (only relevant for type 'addText')
		"borderWidth": 0,
		// string - default: Verdana - if specified ont cannot be found in the system, the default font will be used, if it cannot be found in the system, we will try get the font from the pdf document and use it (only relevant for type 'addText')
		"fontName": "Arial",
		// int - default 20 (only relevant for type 'addText')
		"fontSize": 14,
		// bool - default false (only relevant for type 'addText')
		"fontBold": true,
		// int - default 1 - the page number on which to insert; if 0 is specified, the insert will be placed on each page
		"pageNumber": 1,
		// int - default 10 - distance from left page side in the per cent (only relevant for type 'addText')
		"left": 50,
		// int - default 10 - distance from top page side in the per cent (only relevant for type 'addText')
		"top": 50,
		// int - default 0 - the angle at which the insert will be rotated counterclockwise (only relevant for types 'addText' and 'rotate')
		"angle": 0,
		// string - default 'left' - available values: 'left', 'center', 'right' - text alignment in the rectangle frame (only relevant for type 'addText')
		"align": "center",
		// int - default 0 - indent text above the rectangle line (only relevant for type 'addText')
		"topPadding": 1,
		// int - default 0 - indent text to the left the rectangle line (only relevant for type 'addText')
		"leftPadding": 2,
		// int - default 0 - indent text to the right the rectangle line (only relevant for type 'addText')
		"rightPadding": 3,
		// int - default 0 - indent text below the rectangle line (only relevant for type 'addText')
		"bottomPadding": 4
	}
}
````
We compile the script into one file, put this file in a temporary directory, into which we also put the input file and options file - all this is done by another program, after which we analyze the result text and get the output file data, delete the temporary directory with all the contents.

## Attention

Testing was carried out on a small number of source files, so exceptions are likely, in this case, contact us. Thank you.

#### todo

- add img (need code for add img in pdf file like text now)
- coords (need to more understand how to correctly locate additions with processing their size)