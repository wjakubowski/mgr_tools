import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import numpy as np
from numpy import mean as mean
import glob, os

def readInfoDataFromFile(fileName):
	dataInfo = {}
	with open(fileName) as file:
		for line in file:
			if line[2:8] == "Desc: ":
				line = line[:2] + line[9:]
			if line[0] == "#":
				separatorPos = line.find(":")
				if separatorPos != -1:
					key, val = line[:separatorPos], line[separatorPos:]
					key = key[2:]
					val = val[2:-1]
					dataInfo[key] = val
				else:
					pass
			else:
				break
	return dataInfo

def read3DdataFromFile(fileName):
	data = []
	with open(fileName) as file:
		for line in file:
			if line[0] != "#":
				splitedLine = line.split()
				splitedLine = [float(i) for i in splitedLine]
				data.append(splitedLine)
				
	return data
	
def getXYsliceFrom3Ddata(nx, ny, z, data):
	xy2DsliceXdata=[]
	xy2DsliceYdata=[]
	xy2DsliceZdata=[]
	data=data[nx*ny*z:nx*ny*(z+1)]
	for y in range(ny):
		yLinexy2DsliceXdatadata = []
		yLinexy2DsliceYdatadata = []
		yLinexy2DsliceZdatadata = []
		for x in range(nx):
			yLinexy2DsliceXdatadata.append(data[nx*y+x][0])
			yLinexy2DsliceYdatadata.append(data[nx*y+x][1])
			yLinexy2DsliceZdatadata.append(data[nx*y+x][2])
		xy2DsliceXdata.append(yLinexy2DsliceXdatadata)
		xy2DsliceYdata.append(yLinexy2DsliceYdatadata)
		xy2DsliceZdata.append(yLinexy2DsliceZdatadata)
	return [xy2DsliceXdata, xy2DsliceYdata, xy2DsliceZdata]	
	
############################################################################################################

def drow2DvectorField(fig, ax, xy2DsliceXdata, xy2DsliceYdata, dataInfo, headersMap):
	X, Y = np.meshgrid(np.arange(float(dataInfo["xmin"]), float(dataInfo["xmax"]), float(dataInfo["xstepsize"])), np.arange(float(dataInfo["xmin"]), float(dataInfo["xmax"]), float(dataInfo["xstepsize"])))
	ax.quiver(X, Y, xy2DsliceXdata, xy2DsliceYdata)
	ax.legend()
	plt.title("{}\nczas: {}".format(headersMap[dataInfo["Title"]], dataInfo["Stage simulation time"]))
	plt.xlabel("{} [{}]".format("x", dataInfo["meshunit"]))
	plt.ylabel("{} [{}]".format("y", dataInfo["meshunit"]))
	xmin, xmax = float(dataInfo["xmin"]), float(dataInfo["xmax"])
	ymin, ymax = float(dataInfo["ymin"]), float(dataInfo["ymax"])
	plt.axis(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, style="sci")

def drowAllMatched2DvectorFields(dataFileMatcher, z, outputDir, headersMap):
	dataFiles = glob.glob(dataFileMatcher)
	for dataFile in dataFiles:
		fig, ax = plt.subplots()
		data = read3DdataFromFile(dataFile)
		dataInfo = readInfoDataFromFile(dataFile)
		[xy2DsliceXdata, xy2DsliceYdata, xy2DsliceZdata] = getXYsliceFrom3Ddata(int(dataInfo["xnodes"]), int(dataInfo["ynodes"]), z, data)
		drow2DvectorField(fig, ax, xy2DsliceXdata, xy2DsliceYdata, dataInfo, headersMap)
		file = os.path.basename(dataFile)
		file = file[:-4]
		plt.savefig(outputDir+"/"+file+".pdf")
		plt.close()
		
def loadLayerMeansOFVectorField(dataFileMatcher, Ms = 1,stepOverFrames=1):
	dataFiles = sorted(glob.glob(dataFileMatcher))
	dataInfo0 = readInfoDataFromFile(dataFiles[0])
	outputDict = dataInfo0
	outputDict["matcher"] = dataFileMatcher
	znodes = int(dataInfo0["znodes"])
	for z in range(znodes):
		outputDict[z] = {"t":[],"x":[],"y":[],"z":[]}
	for i in range(len(dataFiles)/stepOverFrames):
		data = read3DdataFromFile(dataFiles[i*stepOverFrames])
		dataInfo = readInfoDataFromFile(dataFiles[i*stepOverFrames])
		for z in range(znodes):
			[xy2DsliceXdata, xy2DsliceYdata, xy2DsliceZdata ] = getXYsliceFrom3Ddata(int(dataInfo["xnodes"]), int(dataInfo["ynodes"]), z, data)
			outputDict[z]["t"].append(float(dataInfo["Total simulation time"][:-2]))
			outputDict[z]["x"].append(mean(xy2DsliceXdata)/Ms)
			outputDict[z]["y"].append(mean(xy2DsliceYdata)/Ms)
			outputDict[z]["z"].append(mean(xy2DsliceZdata)/Ms)
		
	return outputDict
	
def animate2DvectorField(i, z, dataFiles, stepOverFrames, ax, fig, headersMap):
	ax.clear()
	data = read3DdataFromFile(dataFiles[i*stepOverFrames])
	dataInfo = readInfoDataFromFile(dataFiles[i*stepOverFrames])
	[xy2DsliceXdata, xy2DsliceYdata, xy2DsliceZdata] = getXYsliceFrom3Ddata(int(dataInfo["xnodes"]), int(dataInfo["ynodes"]), z, data)
	drow2DvectorField(fig, ax, xy2DsliceXdata, xy2DsliceYdata, dataInfo, headersMap)
	
def makeAnimation(dataFileMatcher, z, outputFile, headersMap, stepOverFrames = 1):
	fig, ax = plt.subplots()
	dataFiles = glob.glob(dataFileMatcher)
	dataFiles.sort()
	ani = animation.FuncAnimation(fig, animate2DvectorField, interval=300, frames = len(dataFiles)/stepOverFrames, fargs=(z, dataFiles, stepOverFrames, ax, fig, headersMap))
	ani.save(outputFile)
	plt.close()
