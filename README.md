# pypdftool

Tool for basic insert to PDF. The insert can be text in several lines, and also the insertion can be inscribed in a rectangle with a frame.

Text of insertion can be customized using color, fon and size. The color and width of line of the rectangle can also be customized.

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
		// string - default 'addText' - other values not yet provided
		"type": "addText",
		// array of strings - text to be inserted
		"text": 
		[
		"Line 1\nString-----2",
		"Line 3--"
		],
		// string - default #000000 - hex color format
		"textColor": "#3f48cc",
		// string - default #000000 - hex color format
		"borderColor": "#3f48cc",
		// int - default 0
		"borderWidth": 0,
		// string - default: Verdana - if specified ont cannot be found in the system, the default font will be used, if it cannot be found in the system, we will try get the font from the pdf document and use it
		"fontName": "Arial",
		// int - default 20
		"fontSize": 14,
		// bool - default false
		"fontBold": true,
		// int - default 1 - the page number on which to insert; if 0 is specified, the insert will be placed on each page
		"pageNumber": 1,
		// int - default 10 - distance from left page side in the per cent
		"left": 50,
		// int - default 10 - distance from top page side in the per cent
		"top": 50,
		// int - default 0 - the angle at which the insert will be roated counterclockwise
		"angle": 0,
		// string - default 'left' - available values: 'left', 'center', 'right' - text alignment in the rectangle frame
		"align": "center",
		// int - default 0 - indent text above the rectangle line
		"topPadding": 1,
		// int - default 0 - indent text to the left the rectangle line
		"leftPadding": 2,
		// int - default 0 - indent text to the right the rectangle line
		"rightPadding": 3,
		// int - default 0 - indent text below the rectangle line
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