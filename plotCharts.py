import os, re, sys
from copy import copy
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
		self.odtFileNames = [self.odtFileName]
		self.odtFiles = {}
		for odtFileName in self.odtFileNames:
			self.odtFiles[odtFileName] = self.readOdtFile(odtFileName)
		
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
							
	def drowFunctionOfVariables(self, variableNameX, variableNameY, outputFile):
		with open(self.odtFileName) as odtFile:
		
			xDict = self.odtFiles[self.odtFileName][variableNameX]
			yDict = self.odtFiles[self.odtFileName][variableNameY]
		
			x = xDict["data"]
			xLabel = self.replaceHeader(variableNameX)
			xUnit = self.replaceHeader(xDict["unit"])

			y = yDict["data"]
			yLabel = self.replaceHeader(variableNameY)
			yUnit = self.replaceHeader(yDict["unit"])
			
			plt.plot(x, y)
			plt.xlabel("{} [{}]".format(xLabel,xUnit))
			plt.ylabel("{} [{}]".format(yLabel,yUnit))
			plt.savefig(outputFile)
			plt.close()

	def animate(self, i, x, y, z, ax, fig):
		ax.clear()
		ax.plot(x[:i], y[:i], z[:i])
		ax.legend()
		plt.xlabel("{} [1]".format("mx"))
		plt.ylabel("{} [1]".format("my"))
		ax.set_zlabel("{} [1]".format("mz"))

			
	def drowTrajectory(self, variableNameX, variableNameY, variableNameZ, outputFile, framesPerSecond):
		with open(self.odtFileName) as odtFile:
			xDict = self.odtFiles[self.odtFileName][variableNameX]
			yDict = self.odtFiles[self.odtFileName][variableNameY]
			zDict = self.odtFiles[self.odtFileName][variableNameZ]
			tDict = self.odtFiles[self.odtFileName]["{Oxs_TimeDriver::Simulation time}"]
		
			x = xDict["data"]
			xLabel = variableNameX
			xUnit = xDict["unit"]

			y = yDict["data"]
			yLabel = variableNameY
			yUnit = yDict["unit"]
			
			z = zDict["data"]
			zLabel = variableNameZ
			zUnit = zDict["unit"]

			t = tDict["data"]
			tLabel = "{Oxs_TimeDriver::Simulation time}"
			tUnit = tDict["unit"]
			
			fig = plt.figure()
			ax = fig.gca(projection='3d')
			ax.clear()
			ax.plot(x, y, z)
			ax.legend()
			plt.xlabel("{} [{}]".format(xLabel,xUnit))
			plt.ylabel("{} [{}]".format(yLabel,yUnit))
			ax.set_zlabel("{} [{}]".format(zLabel,zUnit))
			plt.savefig(outputFile)
			plt.close()
		
			"""fig = plt.figure()
			ax = fig.gca(projection='3d')
			ani = animation.FuncAnimation(fig, animate , frames = len(x), fargs = (x, y, z, ax, fig))
			ani.save(outputFile+".mp4", fps=framesPerSecond)
			plt.close()"""

thisScritDirPath = os.getcwd()
parametersPathElement = sys.argv[1]
symulationName = sys.argv[2]
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
z=int(plottingConfig["zSlice"])
framesPerSecond=int(plottingConfig["framesPerSecond"])
odtPlots=plottingConfig["odtPlots"]

plotter = Plotter(outputDataOdtFilePath, plottingConfig)

for plotName, plotConfig in odtPlots.items():
	if plotConfig["dim"] == "2D":
		plotter.drowFunctionOfVariables(plotConfig["variableNameX"], plotConfig["variableNameY"] , plotConfig["outputFile"].format(outputPlotsDirPath))
	elif plotConfig["dim"] == "3D":
		plotter.drowTrajectory(plotConfig["variableNameX"], plotConfig["variableNameY"], plotConfig["variableNameZ"] , plotConfig["outputFile"].format(outputPlotsDirPath), framesPerSecond)


if plottingConfig["drawSingleFrames"]:
	try:
		os.makedirs(outputPlotsDirPath+"/magnetization")
	except:
		pass
	drowAllMatched2DvectorFields(outputDataDirPath+"/*.ovf", z, outputPlotsDirPath+"/spin_torque")
	try:
		os.makedirs(outputPlotsDirPath+"/spin_torque")
	except:
		pass
	drowAllMatched2DvectorFields(outputDataDirPath+"/*.omf", z, outputPlotsDirPath+"/magnetization")

"""try:
	makeAnimation(outputDataDirPath+"/*.omf", z, outputPlotsDirPath+"/magnetization.mp4")
except IndexError:
	pass
try:
	makeAnimation(outputDataDirPath+"/*.ovf", z, outputPlotsDirPath+"/spin_torque.mp4")
except IndexError:
	pass"""
	