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

def getColumnWithHeader(odtFileName, header):
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
			allHeaders[i] = re.sub("\{|\}" ,"", allHeaders[i])
			if len(re.findall(header, allHeaders[i])):
				return i, allHeaders[i], allUnits[i]
						
def drowFunctionOfVariables(odtFileName, variableNameX, variableNameY, outputFile):
	with open(odtFileName) as odtFile:
		x = []
		y = []
		xIndex, xLabel, xUnit = getColumnWithHeader(odtFileName, variableNameX)
		yIndex, yLabel, yUnit = getColumnWithHeader(odtFileName, variableNameY)
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

def animate(i, x, y, z, ax, fig):
	ax.clear()
	ax.plot(x[:i], y[:i], z[:i])
	ax.legend()
	plt.xlabel("{} [1]".format("mx"))
	plt.ylabel("{} [1]".format("my"))
	ax.set_zlabel("{} [1]".format("mz"))

		
def drowTrajectory(odtFileName, outputFile, framesPerSecond):
	with open(odtFileName) as odtFile:
		x = []
		y = []
		z = []
		xIndex, xLabel, xUnit = getColumnWithHeader(odtFileName, "mx")
		yIndex, yLabel, yUnit = getColumnWithHeader(odtFileName, "my")
		zIndex, zLabel, zUnit = getColumnWithHeader(odtFileName, "mz")
		for line in odtFile:
			if not line[0] == '#':
				splitedLine = line.split()
				x.append(float(splitedLine[xIndex]))
				y.append(float(splitedLine[yIndex]))
				z.append(float(splitedLine[zIndex]))
		numberOfFrames = len(x)
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
	
		fig = plt.figure()
		ax = fig.gca(projection='3d')
		ani = animation.FuncAnimation(fig, animate , frames = len(x), fargs = (x, y, z, ax, fig))
		ani.save(outputFile+".mp4", fps=framesPerSecond)
		plt.close()

thisScritDirPath = os.getcwd()
parametersPathElement = sys.argv[1]
symulationName = sys.argv[2]
plotsFileNameSufix = symulationName
outputDataDirPath = thisScritDirPath+"/"+symulationName+"/"+parametersPathElement
outputPlotsDirPath = thisScritDirPath+"/plots/"+symulationName+"/"+parametersPathElement
outputDataOdtFilePath = outputDataDirPath+"/"+symulationName+".odt"

try:
	os.makedirs(outputPlotsDirPath)
except:
	pass
	
configFile = symulationName + ".json"
configFileStr = open(configFile).read()
configFileJson = json.loads(configFileStr)

plotConfig = configFileJson["plot"]
z=int(plotConfig["zSlice"])
framesPerSecond=int(plotConfig["framesPerSecond"])

drowFunctionOfVariables(outputDataOdtFilePath, "Simulation time", "Signal" , "{}/napiecie_{}.png".format(outputPlotsDirPath, plotsFileNameSufix))
drowFunctionOfVariables(outputDataOdtFilePath, "Simulation time", "total resistance" , "{}/opor_{}.png".format(outputPlotsDirPath, plotsFileNameSufix))
drowFunctionOfVariables(outputDataOdtFilePath, "Simulation time", "mx" , "{}/magnetyzacja_mx_{}.png".format(outputPlotsDirPath, plotsFileNameSufix))
drowTrajectory(outputDataOdtFilePath, "{}/trajektoria_m_{}".format(outputPlotsDirPath, plotsFileNameSufix), framesPerSecond)
drowFunctionOfVariables(outputDataOdtFilePath, "Signal", "total resistance" , "{}/opor_napiecie_{}.png".format(outputPlotsDirPath, plotsFileNameSufix))

if plotConfig["drawSingleFrames"]:
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

try:
	makeAnimation(outputDataDirPath+"/*.omf", z, outputPlotsDirPath+"/magnetization.mp4")
except IndexError:
	pass
try:
	makeAnimation(outputDataDirPath+"/*.ovf", z, outputPlotsDirPath+"/spin_torque.mp4")
except IndexError:
	pass
	