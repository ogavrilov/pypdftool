import os
import tempfile
import shutil
import json
import requests

def prepareTestData(scriptPath, testOptionsData):
	dir_path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
	# create result
	result = []
	resultData = {}
	resultData['result'] = False
	resultData['errorText'] = ''
	resultData['commentText'] = ''
	resultData['testLaunched'] = False
	resultData['fileSizeChange'] = 0
	resultData['testID'] = 0
	resultData['testTitle'] = 0
	resultData['resultFlag'] = False
	resultData['testTitlePostfix'] = ''
	# check args
	if scriptPath == '':
		resultData['commentText'] = 'Not specified script path'
		result.append(resultData)
		return result
	if testOptionsData is None:
		resultData['commentText'] = 'Not specified test options'
		result.append(resultData)
		return result
	# fill data result info
	resultData['testID'] = testOptionsData.get('testID', '')
	resultData['testTitle'] = testOptionsData.get('testTitle', '')
	resultData['resultFlag'] = testOptionsData.get('resultFlag', True)
	# check options file
	optionsFileName = dir_path + '/' + testOptionsData.get('optionsFile', '')
	if not os.path.exists(optionsFileName):
		resultData['commentText'] = 'Not specified options data file'
		result.append(resultData)
		return result
	# check input options
	inputFile = testOptionsData.get('inputFile')
	inputURL = testOptionsData.get('inputURL', [])
	if inputFile is None and len(inputURL) == 0:
		resultData['commentText'] = 'Input data not specified (node "inputFile" or node-array "inputURL" required)'
		result.append(resultData)
		return result
	# prepare options
	try:
		with open(optionsFileName, 'r') as optionsFileHandle:
			optionsData = json.load(optionsFileHandle)
	except Exception as errorObject:
		resultData['commentText'] = 'Options file can not be read: ' + str(errorObject)
		result.append(resultData)
		return result
	if optionsData is None:
		resultData['commentText'] = 'Empty options file'
		result.append(resultData)
		return result
	if inputFile != '' and not inputFile is None:
		optionsData['inputFile'] = 'input.pdf'
		if inputFile.find('/') < 0 and inputFile.find('\\') < 0:
			resultData['inputFile'] = dir_path + '/' + inputFile
		else:
			resultData['inputFile'] = inputFile
	# test
	if not inputFile is None:
		resultData['testLaunched'] = True
		resultData['optionsData'] = optionsData
		result.append(resultData)
	else:
		testNum = 0
		for inputFile in inputURL:
			testNum += 1
			testData = {}
			resultData['testTitlePostfix'] = ' (' + str(testNum) + ')'
			resultData['testLaunched'] = True
			resultData['testLaunched'] = True
			resultData['optionsData'] = {}
			for key, value in optionsData.items():
				resultData['optionsData'][key] = value
			resultData['optionsData']['inputFile'] = 'input.pdf'
			resultData['URL'] = inputFile
			for key, value in resultData.items():
				testData[key] = value
			result.append(testData)
	return result

def executeTests(scriptPath, scenarioPath, resultFileName):
	dir_path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
	# check scenatioPath
	if not os.path.exists(dir_path + '/' + scenarioPath):
		with open(dir_path + '/' + resultFileName, 'w') as resultFileHandle:
			resultFileHandle.write('Scenario file path not specified')
		return
	else:
		# read scenarioData
		try:
			with open(dir_path + '/' + scenarioPath, 'r') as scenarioFileHandle:
				scenarioData = json.load(scenarioFileHandle)
		except Exception as errorObject:
			with open(dir_path + '/' + resultFileName, 'w') as resultFileHandle:
				resultFileHandle.write('Scenario file read error: ' + str(errorObject))
			return
		# prepare all tests
		testDataArray = []
		for scenarioDataElement in scenarioData:
			testDataForCurrentScenario = prepareTestData(scriptPath, scenarioDataElement)
			for testDataForCurrentScenarioElement in testDataForCurrentScenario:
				testDataArray.append(testDataForCurrentScenarioElement)
		# execute all tests
		NotStartedArray = []
		ErrorArray = []
		for testData in testDataArray:
			print('process test ' + testData['testID'] + testData['testTitlePostfix'] + ': ' + str(testData['testTitle']) + ')...')
			if testData['testLaunched']:
				with tempfile.TemporaryDirectory() as tempDirectoryPath:
					tempDirectory = tempDirectoryPath.replace('\\', '/')
					# copy input file
					inputFile = testData.get('inputFile')
					inputFileName = tempDirectory + '/input.pdf'
					if not inputFile is None and inputFile != '':
						shutil.copyfile(inputFile, inputFileName)
					elif not testData.get('URL') is None:
						requestAnswer = requests.get(testData.get('URL'))
						if requestAnswer.status_code != 200:
							testData['commentText'] = 'Problem at downloading test input file (' + testData.get('URL') + ')'
							testData['testLaunched'] = False
							testData['result'] = False
						else:
							with open(inputFileName, 'wb') as inputFileHandle:
								inputFileHandle.write(requestAnswer.content)
					# write options file
					if testData['testLaunched']:
						outpitFileName = tempDirectory + '/output.pdf'
						resultLogFileName = tempDirectory + '/result.log'
						if testData['optionsData'].get('outputFile', '') != '':
							testData['optionsData']['outputFile'] = outpitFileName
						if testData['optionsData'].get('inputFile', '') != '':
							testData['optionsData']['inputFile'] = inputFileName
						testData['optionsData']['resultLog'] = resultLogFileName
						with open(tempDirectory + '/options.json', 'w') as optionsFileHandle:
							json.dump(testData['optionsData'], optionsFileHandle)
						# execute test
						try:
							os.system('python ' + scriptPath + ' ' + tempDirectory + '/options.json')
							processLog = None
							with open(resultLogFileName, 'r') as resultLogFileHandle:
								processLog = json.load(resultLogFileHandle)
							processResult = processLog.get('result', False)
							if not processLog is None:
								testData['result'] = (processResult == testData['resultFlag'])
							if not processLog is None and processLog.get('errorText', '') != '':
								testData['errorText'] = processLog.get('errorText', '')
							if processResult and testData['optionsData'].get('inputFile', '') != '':
								startSize = os.path.getsize(tempDirectory + '/input.pdf')
								endSize = os.path.getsize(outpitFileName)
							else:
								startSize = 0
								endSize = 0
							testData['fileSizeChange'] = endSize - startSize
							testData['resultData'] = processLog
						except Exception as errorObject:
							testData['result'] = False
							testData['errorText'] = str(errorObject)
				if not testData['result']:
					ErrorArray.append(testData)
			else:
				NotStartedArray.append(testData)
		# write results
		with open(dir_path + '/results_all.json', 'w') as resultFileHandle:
			json.dump(testDataArray, resultFileHandle)
		with open(dir_path + '/results_not_started.json', 'w') as resultFileHandle:
			json.dump(NotStartedArray, resultFileHandle)
		with open(dir_path + '/results_all_errors.json', 'w') as resultFileHandle:
			json.dump(ErrorArray, resultFileHandle)
		# print results
		linesArray = []
		linesArray.append('All tests: ' + str(len(testDataArray)) + '\t results_all.json')
		linesArray.append('Correct: ' + str(len(testDataArray) - len(NotStartedArray) - len(ErrorArray)))
		linesArray.append('Not started: ' + str(len(NotStartedArray)) + '\t results_not_started.json')
		linesArray.append('Errors: ' + str(len(ErrorArray)) + '\t\t results_all_errors.json')
		with open(dir_path + '/test_results.log', 'w') as resultFileHandle:
			for curLine in linesArray:
				resultFileHandle.write(curLine + '\n')
				print(curLine)

if __name__ == '__main__':
	dir_path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
	lastSlash = dir_path.rfind('/')
	if lastSlash >= 0:
		dir_path = dir_path[0:lastSlash]
	scriptPath = dir_path + '/pypdftool.py'
	print(scriptPath)
	executeTests(scriptPath, 'scenario.json', 'test_results.json')