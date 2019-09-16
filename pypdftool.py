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

def readPDFLine(stream, streamSize):
    buff = b''
    while True:
        try:
            anotherByte = stream.read(1)
        except:
            return False
        if anotherByte == b'\r' or stream.tell() >= streamSize:
            break
        buff += anotherByte
    return buff

def reconstructPDF(fileName, newFileName):
    try:
        sourceFileSize = os.path.getsize(fileName)
        newFile = open(newFileName, 'wb')
        with open(fileName, 'rb') as sourceFile:
            sourceFile.seek(0)
            while True:
                line = readPDFLine(sourceFile, sourceFileSize)
                newFile.write(line + b'\r')
                if (line == b'xref' or line == b'\nxref') and sourceFile.tell() < sourceFileSize:
                    line = readPDFLine(sourceFile, sourceFileSize)
                    if line[0:1] == b'\n':
                        if line[2:3] != b'0':
                            line = b'\n0' + line[2:]
                    elif line[0:1] != b'0':
                        line = b'0' + line[1:]
                    newFile.write(line + b'\r')
                if sourceFile.tell() == sourceFileSize:
                    break
        newFile.close()
        return ''
    except Exception as errorObject:
        return str(errorObject)

def regFont(fontName, fontBold=False):
	result = ''
	# try to reg font fontName'-Bold'
	if fontBold == True:
		try:
			pdfmetrics.registerFont(TTFont(fontName + '-Bold', fontName + '-Bold.ttf'))
			result = fontName + '-Bold'
		except:
			result = ''
	# try to reg font fontName'Bd'
	if fontBold == True and result == '':
		try:
			pdfmetrics.registerFont(TTFont(fontName + 'Bd', fontName + 'Bd.ttf'))
			result = fontName + 'Bd'
		except:
			result = ''
	# try to reg font fontName without bold
	if result == '':
		try:
			pdfmetrics.registerFont(TTFont(fontName, fontName + '.ttf'))
			result = fontName
		except:
			result = ''
	# default: get first font
	if result == '':
		result = pdfmetrics.getRegisteredFontNames()[0]
		print('Warning: can not register font "' + fontName + '", use standart "' + result + '", check text encoding!')
	return result

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

def getPDFPacket(mod, pageHeight = 400, pageWidth = 400, rotatePage = None):
	packet = io.BytesIO()
	if rotatePage == None or rotatePage == 0 or rotatePage == 180:
		can = canvas.Canvas(packet, (pageWidth, pageHeight))
		d = Drawing(pageWidth, pageHeight)
	else:
		can = canvas.Canvas(packet, (pageHeight, pageWidth))
		d = Drawing(pageHeight, pageWidth)
	lab = Label()
	lab.boxAnchor = 'ne'
	if rotatePage == None or rotatePage == 0:
		lab.angle = mod.get('angle', 0)
		lab.x = int(pageWidth * mod.get('left', 10) / 100)
		lab.y = int(pageHeight - pageHeight * mod.get('top', 10) / 100)
	elif rotatePage == 90:
		lab.angle = mod.get('angle', 0) + 90
		lab.x = int(pageWidth * mod.get('left', 10) / 100)
		lab.y = int(pageHeight * mod.get('top', 10) / 100)
	elif rotatePage == 180:
		lab.angle = mod.get('angle', 0) + 180
		lab.x = int(pageWidth - pageWidth * mod.get('left', 10) / 100)
		lab.y = int(pageHeight * mod.get('top', 10) / 100)
	elif rotatePage == 270:
		lab.angle = mod.get('angle', 0) + 270
		lab.x = int(pageWidth - pageWidth * mod.get('left', 10) / 100)
		lab.y = int(pageHeight - pageHeight * mod.get('top', 10) / 100)
	lab.boxStrokeColor = colors.HexColor(mod.get('borderColor', '#000000'))
	lab.boxStrokeWidth = mod.get('borderWidth', 0)
	lab.topPadding = mod.get('topPadding', 0)
	lab.leftPadding = mod.get('leftPadding', 0)
	lab.rightPadding = mod.get('rightPadding', 0)
	lab.bottomPadding = mod.get('bottomPadding', 0)
	fontName = mod.get('fontName', 'Verdana')
	if fontName == '':
		fontName = 'Verdana'
	fontName = regFont(fontName, mod.get('fontBold', True))
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

def addDataToPDF(optionsData, inputFile):
    try:
        mod = optionsData.get('mod')
        ModType = mod.get('type')
        if ModType == 'addText':
            # mod to input pdf
            if inputFile == '%newpdf%':
                outputFile = optionsData.get('outputFile')
                mod = optionsData.get('mod')
                # draw
                if ModType == 'addText':
                    packet = getPDFPacket(mod)
                new_pdf = PdfFileReader(packet)
                output = PdfFileWriter()
                output.addPage(new_pdf.getPage(0))
                outputStream = open(outputFile, "wb")
                output.write(outputStream)
                outputStream.close()
            else:
                # get input pdf
                input_pdf = PdfFileReader(open(inputFile, "rb"))
                # prepare new pdf
                outputFile = optionsData.get('outputFile')
                if outputFile is None:
                    outputFile = inputFile
                output = PdfFileWriter()
                # for each page
                pageNumber = mod.get('pageNumber', -1)
                for pageInd in range(input_pdf.getNumPages()):
                    curPage = input_pdf.getPage(pageInd)
                    if pageNumber == 0 or pageNumber == pageInd + 1:
                        pageHeight = curPage.mediaBox.getHeight()
                        pageWidth = curPage.mediaBox.getWidth()
                        # draw
                        if ModType == 'addText':
                            packet = getPDFPacket(mod, pageHeight, pageWidth, curPage.get('/Rotate'))
                            new_pdf = PdfFileReader(packet)
                            curPage.mergePage(new_pdf.getPage(0))
                    output.addPage(curPage)
                outputStream = open(outputFile, "wb")
                output.write(outputStream)
                outputStream.close()
            return ''
        elif ModType == 'print':
            input_pdf = PdfFileReader(open(inputFile, "rb"))
            output = PdfFileWriter()
            pageNumber = mod.get('pageNumber', 0)
            for pageInd in range(input_pdf.getNumPages()):
                if pageNumber == 0 or pageNumber == pageInd + 1:
                    output.addPage(input_pdf.getPage(pageInd))
            jsCode = '''
            var checkp;
            if (checkp != 1) {this.print({bUI:true,bSilent:false,bShrinkToFit:true}); checkp = 1;}
            '''
            output.addJS(jsCode)
            outputFile = optionsData.get('outputFile')
            outputStream = open(outputFile, "wb")
            output.write(outputStream)
            outputStream.close()
            return ''
        elif ModType == 'rotate':
            input_pdf = PdfFileReader(open(inputFile, "rb"))
            output = PdfFileWriter()
            pageNumber = mod.get('pageNumber', 0)
            angle = mod.get('angle', 0)
            for pageInd in range(input_pdf.getNumPages()):
                if pageNumber == 0 or pageNumber == pageInd + 1:
                    if angle > 0:
                        output.addPage(input_pdf.getPage(pageInd).rotateClockwise(angle))
                    else:
                        output.addPage(input_pdf.getPage(pageInd).rotateCounterClockwise(-angle))
                else:
                    output.addPage(input_pdf.getPage(pageInd))
            outputFile = optionsData.get('outputFile')
            outputStream = open(outputFile, "wb")
            output.write(outputStream)
            outputStream.close()
            return ''
    except Exception as errorObject:
        return str(errorObject)

if __name__ == '__main__':
    resultInfo = {}
    resultInfo['result'] = False
    resultInfo['errorText'] = 'Unknown error'
    # check arg
    if len(sys.argv) == 1:
        resultInfo['errorText'] = 'First argument not found (options file name)'
    else:
        optionsFile = sys.argv[1]
        # check exist
        if os.path.exists(optionsFile) == False:
            resultInfo['errorText'] = 'Options file not found ("' + str(optionsFile) + '")'
        else:
            # read options file
            try:
                with open (optionsFile, "r", encoding='utf-8') as optionsFileHandle:
                    optionsData = json.load(optionsFileHandle)
            except Exception as errorObject:
                optionsData = None
                resultInfo['errorText'] = 'Error reading options file JSON ("' + str(optionsFile) + '"):\n\r' + str(errorObject)
            if optionsData != None:
                # check input file
                inputFile = optionsData.get('inputFile', '%newpdf%')
                if inputFile == '':
                    inputFile = '%newpdf%'
                if inputFile != '%newpdf%' and not os.path.exists(inputFile):
                    resultInfo['errorText'] = 'Input file not found ("' + str(inputFile) + '")'
                elif inputFile == '%newpdf%' and optionsData.get('outputFile', '') == '':
                    resultInfo['errorText'] = 'When input file field not specified (need new file), you need specified output field!'
                else:
                    # check mod
                    mod = optionsData.get('mod')
                    if mod is None:
                        resultInfo['errorText'] = 'Not found "mod" node in options file'
                    else:
                        addResult = addDataToPDF(optionsData, inputFile)
                        if addResult != '':
                            if optionsData.get('reconstructPDF', False):
                                newInputFile = 'reconstruct_input_file.pdf'
                                if inputFile == newInputFile:
                                    newInputFile = 'reconstruct_input_file_.pdf'
                                outputFile = optionsData.get('outputFile')
                                if outputFile == newInputFile:
                                    newInputFile = 'reconstruct_input_file__.pdf'
                                reconstructPDFResult = reconstructPDF(inputFile, newInputFile)
                                if reconstructPDFResult == '':
                                    resultInfo['errorText'] = addDataToPDF(optionsData, newInputFile)
                                else:
                                    resultInfo['errorText'] = reconstructPDFResult
                            else:
                                resultInfo['errorText'] = addResult
                        else:
                            resultInfo['errorText'] = addResult
            else:
                resultInfo['errorText'] = 'Empty options file ("' + str(optionsFile) + '")'
    if resultInfo['errorText'] == '':
        resultInfo['result'] = True
    try:
        resultLogFileName = optionsData.get('resultLog', 'result.log')
    except:
        resultLogFileName = 'result.log'
    with open(resultLogFileName, 'w') as resultLogFile:
        json.dump(resultInfo, resultLogFile)