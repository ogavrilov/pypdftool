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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def alignTextArray(textArray, alignValue, fontName, fontSize):
	# get lines from text
	linesArray = []
	for curLine in textArray:
		linesArray += curLine.split('\n')
	# align
	if alignValue == 'right' or alignValue == 'center':
		# get max len
		maxLen = 0
		for curLine in linesArray:
			if maxLen < pdfmetrics.stringWidth(curLine, fontName, fontSize):
				maxLen = pdfmetrics.stringWidth(curLine, fontName, fontSize)
		# copy text array and add empty
		result = []
		for curLine in linesArray:
			if len(curLine) == maxLen:
				result.append(curLine)
			elif alignValue == 'right':
				curLineNew = curLine
				while pdfmetrics.stringWidth(' ' + curLineNew, fontName, fontSize) <= maxLen:
					curLineNew = ' ' + curLineNew
				result.append(curLineNew)
			else:
				curLineNew = curLine
				while pdfmetrics.stringWidth(' ' + curLineNew + ' ', fontName, fontSize) <= maxLen:
					curLineNew = ' ' + curLineNew + ' '
				result.append(curLineNew)
		return result
	else:
		return linesArray

def get_pdf_packet(mod, pageHeight = 400, pageWidth = 400):
	packet = io.BytesIO()
	can = canvas.Canvas(packet)
	d = Drawing(pageHeight, pageWidth)
	lab = Label()
	lab.boxAnchor = 'ne'
	lab.angle = mod.get('angle', 0)
	lab.x = int(pageWidth * mod.get('left', 10) / 100)
	lab.y = int(pageHeight - pageHeight * mod.get('top', 10) / 100)
	lab.boxStrokeColor = colors.HexColor(mod.get('borderColor', '#000000'))
	lab.boxStrokeWidth = mod.get('borderWidth', 0)
	lab.topPadding = mod.get('topPadding', 0)
	lab.leftPadding = mod.get('leftPadding', 0)
	lab.rightPadding = mod.get('rightPadding', 0)
	lab.bottomPadding = mod.get('bottomPadding', 0)
	fontName = mod.get('fontName', 'Courier')
	if fontName == '':
		fontName = 'Courier'
	if mod.get('Bold', True):
		fontName = fontName + '-Bold'
	if fontName not in pdfmetrics.getRegisteredFontNames():
		try:
			pdfmetrics.registerFont(TTFont(fontName, fontName + '.ttf'))
		except:
			print('Warning: can not register font "' + fontName + '", use standart "Courier", check text encoding!')
			fontName = pdfmetrics.getRegisteredFontNames()[0]
	lab.fontName = fontName
	lab.fontSize = mod.get('fontSize', 20)
	lab.fillColor = colors.HexColor(mod.get('textColor', '#000000'))
	textS = ''
	textArray = alignTextArray(mod.get('text', []), mod.get('align', 'left'), lab.fontName, lab.fontSize)
	for curLine in textArray:
		if len(textS) > 0:
			textS += '\n'
		textS += curLine
	lab.setText(textS)
	d.add(lab)
	renderPDF.draw(d, can, 0, 0)
	can.save()
	packet.seek(0)
	return packet
	
if __name__ == '__main__':
	# check arg
	if len(sys.argv) == 1:
		print('Can not find path to options file')
	else:
		# get arg
		optionsFile = sys.argv[1]
		#optionsFile = 'options.json'
		# read options file
		with open (optionsFile, "r", encoding='utf-8') as fileH:
			optionsData = json.load(fileH)
		# check input file
		inputFile = optionsData.get('inputFile')
		if inputFile is None or (inputFile != '%newpdf%' and not os.path.exists(inputFile)):
			print('Can not find input type')
		else:
			# check mod
			mod = optionsData.get('mod')
			if mod is None:
				print('Can not find mod in options file')
			else:
				# mod to input pdf
				ModType = mod.get('type')
				input_pdf_name = optionsData.get('inputFile')
				if input_pdf_name == '%newpdf%':
					outputFile = optionsData.get('outputFile')
					mod = optionsData.get('mod')
					# draw
					if ModType == 'addText':
						packet = get_pdf_packet(mod)
					new_pdf = PdfFileReader(packet)
					output = PdfFileWriter()
					output.addPage(new_pdf.getPage(0))
					outputStream = open(outputFile, "wb")
					output.write(outputStream)
					outputStream.close()
				else:
					# get input pdf
					input_pdf = PdfFileReader(open(input_pdf_name, "rb"))
					# prepare new pdf
					outputFile = optionsData.get('outputFile')
					if outputFile is None:
						outputFile = input_pdf_name
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
							if ModType == 'addText':
								packet = get_pdf_packet(mod, pageHeight, pageWidth)
								new_pdf = PdfFileReader(packet)
								curPage.mergePage(new_pdf.getPage(0))
						output.addPage(curPage)
					outputStream = open(outputFile, "wb")
					output.write(outputStream)
					outputStream.close()