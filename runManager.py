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
symulationDirectory = "./"+symulationName

oommfPath = "/net/scratch/people/plgwojciechjak/OOMMF-SWAG/oommf.tcl"
thisScritDirPath = os.getcwd()

config_file = symulationName + ".json"
config_file_str = open(config_file).read()
config_file_json = json.loads(config_file_str)

verbousParams = []
silentParams = []

for paramName, paramProperties in config_file_json.iteritems():
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

"""
silentParams.append(("scheduleStep", max(1, int(stoppingTime/timeStep/numberOfPoints) ) ) )
silentParams.append(("magnetizationScheduleStep", max(1, int(stoppingTime/timeStep/numberOfMagMaps) ) ) )"""

mifFilePath = "./{}.mif".format(symulationName)
scriptFilePath = "./skrypt.txt"
##################################################################################################

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
		parametersPathElement += "{}_{}_".format(verbousParams[i][0], format(parameters[i], '.{}f'.format(verbousParams[i][2])))
		mifParametersStr += "{} {} ".format(verbousParams[i][0],parameters[i])
	currentWorkDir = "{}/{}".format(symulationDirectory, parametersPathElement)
	outputOdtFilePath = "{}/{}".format(currentWorkDir, symulationName)
	mifParametersStr += "{} {} ".format("output_file", outputOdtFilePath)
	
	for i in range(len(silentParams)):
		mifParametersStr += "{} {} ".format(silentParams[i][0], silentParams[i][1])

	try:
		os.mkdir(currentWorkDir)
	except:
		pass

	scriptPath = '{}/skrypt.sh'.format(currentWorkDir, mifFilePath, outputOdtFilePath, mifParametersStr)
	with open(scriptPath,'w') as f:
		f.write(scriptStr.format(parametersPathElement, currentWorkDir, currentWorkDir, mifFilePath, outputOdtFilePath, \
			mifParametersStr, oommfPath, thisScritDirPath, parametersPathElement, symulationName))
	
	shutil.copy(mifFilePath, "{}/{}".format(currentWorkDir, symulationName+".mif"))
	shutil.copy(config_file, "{}/{}".format(currentWorkDir, symulationName+".json"))
			
	command = "sbatch {} ".format(scriptPath)
	print "\nTerminal command:\n", command , '\n'

	os.system(command)
	
	
	
	
	
	
	
	
