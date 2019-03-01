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

	def __init__(self, odtFileName):
		self.odtFileName = odtFileName

	def getColumnWithHeader(self, header):
		with open(self.odtFileName) as odtFile:
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
				allHeaders[i] = re.sub("\{|\}" ,"", allHeaders[i])
				if len(re.findall(header, allHeaders[i])):
					return i, allHeaders[i], allUnits[i]
							
	def drowFunctionOfVariables(self, variableNameX, variableNameY, outputFile):
		with open(self.odtFileName) as odtFile:
			x = []
			y = []
			xIndex, xLabel, xUnit = self.getColumnWithHeader(variableNameX)
			yIndex, yLabel, yUnit = self.getColumnWithHeader(variableNameY)
			for line in odtFile:
				if not line[0] == '#':
					splitedLine = line.split()
					x.append(float(splitedLine[xIndex]))
					y.append(float(splitedLine[yIndex]))
			
			plt.plot(x, y)
			plt.xlabel("{} [{}]".format(variableNameX,xUnit))
			plt.ylabel("{} [{}]".format(variableNameY,yUnit))
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
			x = []
			y = []
			z = []
			t = []
			xIndex, xLabel, xUnit = self.getColumnWithHeader(variableNameX)
			yIndex, yLabel, yUnit = self.getColumnWithHeader(variableNameY)
			zIndex, zLabel, zUnit = self.getColumnWithHeader(variableNameZ)
			tIndex, tLabel, tUnit = self.getColumnWithHeader("Simulation time")
			for line in odtFile:
				if not line[0] == '#':
					splitedLine = line.split()
					x.append(float(splitedLine[xIndex]))
					y.append(float(splitedLine[yIndex]))
					z.append(float(splitedLine[zIndex]))
					t.append(float(splitedLine[tIndex]))
			fig = plt.figure()
			ax = fig.gca(projection='3d')
			ax.clear()
			ax.plot(x, y, z)
			ax.legend()
			plt.xlabel("{} [{}]".format(xLabel,xUnit))
			plt.ylabel("{} [{}]".format(yLabel,yUnit))
			ax.set_zlabel("{} [{}]".format(zLabel,zUnit))
			plt.savefig(outputFile+".png")
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

plotter = Plotter(outputDataOdtFilePath)

#for plotName, plotConfig in odtPlots.items():
#	plotter.drowFunctionOfVariables(plotConfig["variableNameX"], plotConfig["variableNameY"] , plotConfig["outputFile"].format(outputPlotsDirPath))

plotter.drowTrajectory("mx", "my", "mz", "{}/trajektoria_m".format(outputPlotsDirPath), framesPerSecond)


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
	