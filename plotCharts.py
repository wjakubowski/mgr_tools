import os, re, sys
import numpy as np
import json

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

from plot2DvectorField import makeAnimation as makeAnimation
from plot2DvectorField import drowAllMatched2DvectorFields as drowAllMatched2DvectorFields
from plot2DvectorField import loadLayerMeansOFVectorField as loadLayerMeansOFVectorField

matplotlib.rcParams.update({'font.size': 12})

class Plotter():

	def __init__(self, odtSources, plottingConfig):
		self.plottingConfig = plottingConfig
		self.headersMap = self.plottingConfig["headersMap"]
		self.odtFiles = {}
		for	legendLabel, odtPath in odtSources.items():
			self.odtFiles[legendLabel] = self.readOdtFile(odtPath)

	def readOdtFile(self, odtFileName):
		odtColumnsDict = {}
		with open(odtFileName) as odtFile:
			headersLine = None
			unitsLine = None
			for line in odtFile:
				splitedLine = line.split()
				if splitedLine[0] == '#' and splitedLine[1] == 'Columns:':
					headersLine = re.sub("# Columns: ", "", line)
					break
					
			for line in odtFile:
				splitedLine = line.split()
				if splitedLine[0] == '#' and splitedLine[1] == 'Units:':
					unitsLine = re.sub("# Units: ", "", line)
					break
					
			allHeaders = re.findall("(\{[a-zA-Z0-9\ :-_\/]+\}|[a-zA-Z0-9:-_\/]+)", headersLine)
			allUnits = re.findall("(\{[a-zA-Z0-9\/\ ]*\}|[a-zA-Z0-9\/]+)", unitsLine)
			
			for i in range(len(allHeaders)):
				odtColumnsDict[allHeaders[i]] = {"unit":allUnits[i], "data":[]}

			for line in odtFile:
				if not line[0] == '#':
					splitedLine = line.split()
					for headerInd in range(len(allHeaders)):
						odtColumnsDict[allHeaders[headerInd]]["data"].append(float(splitedLine[headerInd]))
						
		return odtColumnsDict
		
	def replaceHeader(self, headerName):
		if headerName in self.headersMap:
			return self.headersMap[headerName]
		else: 
			return headerName
							
	def drowSinglePlot(self, plotConfig, odtData, legendLabel = ""):
		variableNameX = plotConfig["variableNameX"]
		variableNameY = plotConfig["variableNameY"]
		
		xDict = odtData[variableNameX]
		yDict = odtData[variableNameY]
		
		x = xDict["data"]
		xLabel = self.replaceHeader(variableNameX)
		xUnit = self.replaceHeader(xDict["unit"])

		y = yDict["data"]
		yLabel = self.replaceHeader(variableNameY)
		yUnit = self.replaceHeader(yDict["unit"])
		
		if "scalingFunction" in plotConfig:
			scalingFunction = eval(plotConfig["scalingFunction"])
			y = [scalingFunction(f) for f in y]
		
		plt.plot(x, y, label = legendLabel)
		plt.xlabel("{} [{}]".format(xLabel,xUnit))
		plt.ylabel("{} [{}]".format(yLabel,yUnit))
							
	def drowFunctionForAllOdts(self, plotConfig, outputFile):
		plt.figure().clf()
		for legendLabel, odtData in sorted(self.odtFiles.items()):
			self.drowSinglePlot(plotConfig, odtData, legendLabel)
		plt.legend()
	
		plt.tight_layout()
		plt.savefig(outputFile)
		plt.close()

	"""def animate(self, i, x, y, z, ax, fig):
		ax.clear()
		ax.plot(x[:i], y[:i], z[:i])
		ax.legend()
		plt.xlabel("{} [1]".format("mx"))
		plt.ylabel("{} [1]".format("my"))
		ax.set_zlabel("{} [1]".format("mz"))"""

	def drowFunctionForVariableSet(self, variableSet, outputFile):
		odtSource = variableSet["odtSource"]
		label = variableSet["label"]
		commonConfig = variableSet["commonConfig"]
		variables = variableSet["variables"]
		plotConfigs = {}
		for variableLabel, variableDict in variables.items():
			plotConfigs[variableLabel] = dict(commonConfig, **variableDict)
			
		plt.figure().clf()
		for legendLabel, plotConfig in sorted(plotConfigs.items()):
			self.drowSinglePlot(plotConfig, self.odtFiles[odtSource], legendLabel)
		plt.legend()
		
		plt.ylabel(label)
		plt.tight_layout()
		plt.savefig(outputFile)
		plt.close()

	def drowAvgMagOfSpecificLayerInTime(self, layerAvgConfigs, matcher, outputFile):
		Ms = layerAvgConfigs["Ms"]
		vectorComponent = layerAvgConfigs["vectorComponent"]
		layerLabelDict = layerAvgConfigs["layerLabelDict"]
		stepOverFrames = layerAvgConfigs["stepOverFrames"]
		label = layerAvgConfigs["label"]

		data = loadLayerMeansOFVectorField(matcher, Ms, stepOverFrames)
			
		plt.figure().clf()
		
		for layer, layerLabel in layerLabelDict.items():
			layer = int(layer)
			plt.plot(data[layer]["t"], data[layer][vectorComponent], label=layerLabel)

		plt.legend()
				
		plt.xlabel("t [s]")
		plt.ylabel(label)

		plt.tight_layout()
		plt.savefig(outputFile)
		plt.close()

	def drowSingleTrajcetory(self, ax, plotConfig, odtData, legendLabel):
		variableNameX = plotConfig["variableNameX"]
		variableNameY = plotConfig["variableNameY"]
		variableNameZ = plotConfig["variableNameZ"]
		parameterName = "{Oxs_TimeDriver::Simulation time}"
		
		xDict = self.odtFiles[legendLabel][variableNameX]
		yDict = self.odtFiles[legendLabel][variableNameY]
		zDict = self.odtFiles[legendLabel][variableNameZ]
		tDict = self.odtFiles[legendLabel][parameterName]
		
		x = xDict["data"]
		xLabel = self.replaceHeader(variableNameX)
		xUnit = self.replaceHeader(xDict["unit"])

		y = yDict["data"]
		yLabel = self.replaceHeader(variableNameY)
		yUnit = self.replaceHeader(yDict["unit"])
		
		z = zDict["data"]
		zLabel = self.replaceHeader(variableNameZ)
		zUnit = self.replaceHeader(zDict["unit"])

		t = tDict["data"]
		tLabel = self.replaceHeader(parameterName)
		tUnit = self.replaceHeader(tDict["unit"])
		
		if "scalingFunction" in plotConfig:
			scalingFunction = eval(plotConfig["scalingFunction"])
			x = [scalingFunction(f) for f in x]
			y = [scalingFunction(f) for f in y]
			z = [scalingFunction(f) for f in z]

		ax.plot(x, y, z, label=legendLabel)
		plt.xlabel("{} [{}]".format(xLabel,xUnit))
		plt.ylabel("{} [{}]".format(yLabel,yUnit))
		ax.set_zlabel("{} [{}]".format(zLabel,zUnit))
			
	def drowTrajectoryForAllOdts(self, plotConfig, outputFile):
		fig = plt.figure()
		fig.clf()
		ax = fig.gca(projection='3d')
		ax.clear()
		for legendLabel, odtData in sorted(self.odtFiles.items()):
			self.drowSingleTrajcetory(ax, plotConfig, odtData, legendLabel)
		plt.legend()

		plt.tight_layout()
		plt.savefig(outputFile)
		plt.close()
		
		"""fig = plt.figure()
		ax = fig.gca(projection='3d')
		ani = animation.FuncAnimation(fig, animate , frames = len(x), fargs = (x, y, z, ax, fig))
		ani.save(outputFile+".mp4", fps=int(self.plottingConfig["framesPerSecond"]))
		plt.close()"""

thisScritDirPath = os.getcwd()
workMode = sys.argv[1]
symulationName = sys.argv[2]
configFile = sys.argv[3]
parametersPathElement = sys.argv[4]

outputDataDirPath = thisScritDirPath+"/"+symulationName+"/"+parametersPathElement
outputPlotsDirPath = thisScritDirPath+"/plots_tmp/"+symulationName+"/"+parametersPathElement
outputDataOdtFilePath = outputDataDirPath+"/"+symulationName+".odt"

try:
	os.makedirs(outputPlotsDirPath)
except:
	pass

configFileStr = open(configFile).read()
configFileJson = json.loads(configFileStr)

plottingConfig = configFileJson["plot"]
odtPlots=plottingConfig["odtPlots"]
odtSources=plottingConfig["odtSources"]

plotter = None
if workMode == "usePathOdt":
	plotter = Plotter({"":outputDataOdtFilePath}, plottingConfig)
else:
	plotter = Plotter(odtSources, plottingConfig)

for plotConfig in odtPlots:
	if plotConfig["dim"] == "2D":
		plotter.drowFunctionForAllOdts(plotConfig , plotConfig["outputFile"].format(outputPlotsDirPath))
	elif plotConfig["dim"] == "3D":
		plotter.drowTrajectoryForAllOdts(plotConfig , plotConfig["outputFile"].format(outputPlotsDirPath))

variableSets = plottingConfig["variableSets"]
for variableSet in variableSets:
	if workMode == "usePathOdt":
		variableSet["odtSource"] = ""
	plotter.drowFunctionForVariableSet(variableSet, variableSet["outputFile"].format(outputPlotsDirPath))
	
if plottingConfig["plotLayersAvg"]:
	layerAvgConfigs = plottingConfig["layerAvgConfigs"]
	for layerAvgConfig in layerAvgConfigs:
		plotter.drowAvgMagOfSpecificLayerInTime(layerAvgConfig, outputDataDirPath+"/*.omf", layerAvgConfig["outputFile"].format(outputPlotsDirPath))

zSlices=plottingConfig["zSlices"]
makeAnimations=plottingConfig["makeAnimations"]
stepOverFrames=plottingConfig["stepOverFrames"]

for z in zSlices:
	if makeAnimations:
		makeAnimation(outputDataDirPath+"/*.omf", z, outputPlotsDirPath+"/magnetization{}.mp4".format(z), stepOverFrames)
		makeAnimation(outputDataDirPath+"/*.ovf", z, outputPlotsDirPath+"/spin_torque{}.mp4".format(z), stepOverFrames)
	
	if plottingConfig["drawSingleFrames"]:
		magnetizationDir = outputPlotsDirPath+"/magnetization{}".format(z)
		try:
			os.makedirs(magnetizationDir)
			drowAllMatched2DvectorFields(outputDataDirPath+"/*.omf", z, magnetizationDir)
		except:
			print "Can't create magnetization frames!"
		
		spinTorqueDir = outputPlotsDirPath+"/spin_torque{}".format(z)
		try:
			os.makedirs(spinTorqueDir)
			drowAllMatched2DvectorFields(outputDataDirPath+"/*.ovf", z, spinTorqueDir)
		except:
			print "Can't create spin_torque frames!"


	