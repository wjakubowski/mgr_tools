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

class Plotter():

	def __init__(self, odtFileName, plottingConfig):
		self.odtFileName = odtFileName
		self.plottingConfig = plottingConfig
		self.headersMap = self.plottingConfig["headersMap"]
		self.odtFiles = {}
		if self.plottingConfig["multiPlotMode"]:
			for	legendLabel, odtPath in plottingConfig["odtSources"].items():
				self.odtFiles[odtPath] = self.readOdtFile(odtPath)
		else:
			self.odtFiles[odtFileName] = self.readOdtFile(self.odtFileName)

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
							
	def drowSinglePlot(self, plotConfig, odtFileName, legendLabel = ""):
		variableNameX = plotConfig["variableNameX"]
		variableNameY = plotConfig["variableNameY"]
		
		xDict = self.odtFiles[odtFileName][variableNameX]
		yDict = self.odtFiles[odtFileName][variableNameY]
		
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
							
	def drowFunctionOfVariables(self, plotConfig, outputFile):
		plt.figure().clf()
		if plottingConfig["multiPlotMode"]:
			for legendLabel, odtPath in plottingConfig["odtSources"].items():
				self.drowSinglePlot(plotConfig, odtPath, legendLabel)
			plt.legend()
		else:
			self.drowSinglePlot(plotConfig, self.odtFileName)
	
		plt.savefig(outputFile)
		plt.close()

	"""def animate(self, i, x, y, z, ax, fig):
		ax.clear()
		ax.plot(x[:i], y[:i], z[:i])
		ax.legend()
		plt.xlabel("{} [1]".format("mx"))
		plt.ylabel("{} [1]".format("my"))
		ax.set_zlabel("{} [1]".format("mz"))"""

	def drowSingleTrajcetory(self, ax, plotConfig, odtFileName, legendLabel = ""):
		variableNameX = plotConfig["variableNameX"]
		variableNameY = plotConfig["variableNameY"]
		variableNameZ = plotConfig["variableNameZ"]
		
		xDict = self.odtFiles[odtFileName][variableNameX]
		yDict = self.odtFiles[odtFileName][variableNameY]
		zDict = self.odtFiles[odtFileName][variableNameZ]
		tDict = self.odtFiles[odtFileName]["{Oxs_TimeDriver::Simulation time}"]
		
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
		tLabel = "{Oxs_TimeDriver::Simulation time}"
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
			
	def drowTrajectory(self, plotConfig, outputFile):
		fig = plt.figure()
		fig.clf()
		ax = fig.gca(projection='3d')
		ax.clear()
		if plottingConfig["multiPlotMode"]:
			for legendLabel, odtPath in sorted(plottingConfig["odtSources"].items()):
				self.drowSingleTrajcetory(ax, plotConfig, odtPath, legendLabel)
			plt.legend()
		else:
			self.drowSingleTrajcetory(ax, plotConfig, self.odtFileName)
		plt.savefig(outputFile)
		plt.close()
		
		"""fig = plt.figure()
		ax = fig.gca(projection='3d')
		ani = animation.FuncAnimation(fig, animate , frames = len(x), fargs = (x, y, z, ax, fig))
		ani.save(outputFile+".mp4", fps=int(self.plottingConfig["framesPerSecond"]))
		plt.close()"""

thisScritDirPath = os.getcwd()
symulationName = sys.argv[1]
parametersPathElement = sys.argv[2]
outputDataDirPath = thisScritDirPath+"/"+symulationName+"/"+parametersPathElement
outputPlotsDirPath = thisScritDirPath+"/plots_tmp/"+symulationName+"/"+parametersPathElement
outputDataOdtFilePath = outputDataDirPath+"/"+symulationName+".odt"

try:
	os.makedirs(outputPlotsDirPath)
except:
	pass
	
configFile = symulationName + ".json"
configFileStr = open(configFile).read()
configFileJson = json.loads(configFileStr)

plottingConfig = configFileJson["plot"]
"""z=int(plottingConfig["zSlice"])"""
odtPlots=plottingConfig["odtPlots"]

plotter = Plotter(outputDataOdtFilePath, plottingConfig)

for plotName, plotConfig in odtPlots.items():
	if plotConfig["dim"] == "2D":
		plotter.drowFunctionOfVariables(plotConfig , plotConfig["outputFile"].format(outputPlotsDirPath))
	elif plotConfig["dim"] == "3D":
		plotter.drowTrajectory(plotConfig , plotConfig["outputFile"].format(outputPlotsDirPath))


"""if plottingConfig["drawSingleFrames"]:
	try:
		os.makedirs(outputPlotsDirPath+"/magnetization")
	except:
		pass
	drowAllMatched2DvectorFields(outputDataDirPath+"/*.ovf", z, outputPlotsDirPath+"/spin_torque")
	try:
		os.makedirs(outputPlotsDirPath+"/spin_torque")
	except:
		pass
	drowAllMatched2DvectorFields(outputDataDirPath+"/*.omf", z, outputPlotsDirPath+"/magnetization")"""

"""try:
	makeAnimation(outputDataDirPath+"/*.omf", z, outputPlotsDirPath+"/magnetization.mp4")
except IndexError:
	pass
try:
	makeAnimation(outputDataDirPath+"/*.ovf", z, outputPlotsDirPath+"/spin_torque.mp4")
except IndexError:
	pass"""
	