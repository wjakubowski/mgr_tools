#!/usr/bin/env python2
import os
import sys
import shutil
import copy
import json
import math

def frange(x, y, jump):
  while x <= y:
    yield float(x)
    x += jump
	
def extendParamSuits(paramSuits, parameterValues):
	extendedParamSuits = []
	for paramSuite in paramSuits:
		for paramValue in parameterValues:
			paramSuiteCopy = copy.copy(paramSuite)
			paramSuiteCopy.append(paramValue)
			extendedParamSuits.append(paramSuiteCopy)
	return extendedParamSuits
	
def createParamSuitsFromParamRanges(paramRanges):
	paramSuits = [[]]
	for paramValue in range(len(paramRanges)):
		paramSuits = extendParamSuits(paramSuits, paramRanges[paramValue][1])
	return paramSuits

symulationName = sys.argv[1]
configFile = sys.argv[2]
mifFilePath = sys.argv[3]
symulationDirectory = "./"+symulationName

thisScritDirPath = os.getcwd()

configFileStr = open(configFile).read()
configFileJson = json.loads(configFileStr)

symulationConfig = configFileJson["symulation"]
plotConfig = configFileJson["plot"]

doPloting = "true" if plotConfig["doPloting"]  else "false"

doSymulation = "true" if symulationConfig["doSymulation"] else "false"
oommfPath = symulationConfig["oommfPath"]
grant = symulationConfig["grant"]
partition = symulationConfig["partition"]
maxSimulationTime = symulationConfig["maxSimulationTime"]
symulationParameters = symulationConfig["mifParameters"]
verbousParams = []
silentParams = []

for paramName, paramProperties in symulationParameters.iteritems():
	#exec(paramName+" = "+str(paramProperties["value"]))
	if(paramProperties["verbous"]):
		if(paramProperties["type"] == "value"):
			verbousParams.append((paramName, [paramProperties["value"]], paramProperties["precision"]))
		elif(paramProperties["type"] == "script"):
			verbousParams.append((paramName, eval(paramProperties["value"]), paramProperties["precision"] ) )
	else:
		if(paramProperties["type"] == "value"):
			silentParams.append((paramName, paramProperties["value"]))
		elif(paramProperties["type"] == "script"):
			silentParams.append((paramName, eval(paramProperties["value"]) ) )

scriptFilePath = "./skrypt.txt"

#read template of shell script file
scriptStr = ""
with open(scriptFilePath, 'r') as f:
	for line in f:
		scriptStr += line

#create parameters grid from parameters range
symulParamGrid = createParamSuitsFromParamRanges(verbousParams)

#create main output dir
"""try:
	os.rmtree(symulationDirectory)
except:
	pass"""
try:
	os.mkdir(symulationDirectory)
except:
	pass
	
#process simulations with parameters grid nodes
for parameters in symulParamGrid:
	parametersPathElement = ""
	mifParametersStr = ""
	for i in range(len(verbousParams)):
		parametersPathElement += "{paramName}_{formatedParamValue}_".format(\
										paramName = verbousParams[i][0],\
										formatedParamValue = format(parameters[i], '.{paramPrecision}f'.format(paramPrecision = verbousParams[i][2])))
		mifParametersStr += "{paramName} {paramValue} ".format(paramName = verbousParams[i][0], paramValue = parameters[i])
	currentWorkDir = "{}/{}".format(symulationDirectory, parametersPathElement)
	outputOdtFilePath = "{}/{}".format(currentWorkDir, symulationName)
	mifParametersStr += "{} {} ".format("output_file", outputOdtFilePath)
	
	for i in range(len(silentParams)):
		mifParametersStr += "{} {} ".format(silentParams[i][0], silentParams[i][1])

	try:
		os.mkdir(currentWorkDir)
	except:
		pass

	scriptPath = '{}/skrypt.sh'.format(currentWorkDir)
	with open(scriptPath,'w') as f:
		f.write(scriptStr.format(parametersPathElement=parametersPathElement, currentWorkDir=currentWorkDir, mifFilePath=mifFilePath, outputOdtFilePath=outputOdtFilePath, \
			mifParametersStr = mifParametersStr, oommfPath=oommfPath, thisScritDirPath=thisScritDirPath, symulationName=symulationName, configFile=configFile, \
			doSymulation = doSymulation, doPloting = doPloting, grant = grant, partition = partition, maxSimulationTime = maxSimulationTime))
	
	shutil.copy(mifFilePath, "{}/{}".format(currentWorkDir, mifFilePath))
	shutil.copy(configFile, "{}/{}".format(currentWorkDir, configFile))
			
	command = "sbatch {} ".format(scriptPath)
	print "\nTerminal command:\n", command , '\n'

	os.system(command)
	
	
	
	
	
	
	
	
