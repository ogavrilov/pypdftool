import io
import os
import sys
import json
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib import colors
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas

def prepareTextMod(optionsData):
	# get input pdf
	input_pdf = PdfFileReader(open(optionsData.get('inputFile'), "rb"))
	# prepare new pdf
	outputFile = optionsData.get('outputFile')
	if outputFile is None:
		outputFile = optionsData.get('inputFile')
	output = PdfFileWriter()
	# for each page
	pageInd = 0
	mod = optionsData.get('mod')
	pageNumber = mod.get('pageNumber', -1)
	for pageInd in range(input_pdf.getNumPages()):
		curPage = input_pdf.getPage(pageInd)
		if pageNumber == 0 or pageNumber == pageInd + 1:
			pageHeight = curPage.mediaBox.getHeight()
			pageWidth = curPage.mediaBox.getWidth()
			# draw
			packet = io.BytesIO()
			can = canvas.Canvas(packet)
			d = Drawing(pageHeight, pageWidth)
			lab = Label()
			lab.boxAnchor = 'ne'
			lab.angle = mod.get('angle', 0)
			lab.x = mod.get('left', 0)
			lab.y = mod.get('top', 0)
			lab.boxStrokeColor = colors.HexColor(mod.get('borderColor', '#000000'))
			lab.boxStrokeWidth = mod.get('borderWidth', 0)
			lab.fontName = mod.get('fontName', 'Courier')
			if mod.get('Bold', True):
				lab.fontName = lab.fontName + '-Bold'
			lab.fontSize = mod.get('fontSize', 20)
			lab.fillColor = colors.HexColor(mod.get('textColor', '#000000'))
			textS = ''
			for curLine in mod.get('text', []):
				if len(textS) > 0:
					textS += '\n'
				textS += curLine
			lab.setText(textS)
			d.add(lab)
			#renderPDF.drawToFile(d, mod.get('type') + '_.pdf', '')
			renderPDF.draw(d, can, 0, 0)
			can.save()
			packet.seek(0)
			new_pdf = PdfFileReader(packet)
			curPage.mergePage(new_pdf.getPage(0))
		output.addPage(curPage)
	outputStream = open(outputFile, "wb")
	output.write(outputStream)
	outputStream.close()

def prepareImgMod(curMod):
	a = 1
	
if __name__ == '__main__':
	# check arg
	if len(sys.argv) == 1:
		print('Can not find path to options file')
	else:
		# get arg
		optionsFile = sys.argv[1]
		# read options file
		with open (optionsFile, "r") as fileH:
			optionsJSON = fileH.read()
		# get options data from JSON
		optionsData = json.loads(optionsJSON)
		# check input file
		inputFile = optionsData.get('inputFile')
		if inputFile is None or not os.path.exists(inputFile):
			print('Can not find input type')
		else:
			# add to mods merge files
			mod = optionsData.get('mod')
			if mod is None:
				print('Can not find mod in options file')
			else:
				ModType = mod.get('type')
				if not ModType is None and ModType == "addText":
					prepareTextMod(optionsData)
				elif not ModType is None and ModType == "addImg":
					prepareImgMod(optionsData)