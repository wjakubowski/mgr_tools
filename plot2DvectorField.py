import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import numpy as np
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
	data=data[nx*ny*z:nx*ny*(z+1)]
	for y in range(ny):
		yLinexy2DsliceXdatadata = []
		yLinexy2DsliceYdatadata = []
		for x in range(nx):
			yLinexy2DsliceXdatadata.append(data[nx*y+x][0])
			yLinexy2DsliceYdatadata.append(data[nx*y+x][1])
		xy2DsliceXdata.append(yLinexy2DsliceXdatadata)
		xy2DsliceYdata.append(yLinexy2DsliceYdatadata)
	return [xy2DsliceXdata, xy2DsliceYdata]	
	
############################################################################################################

def drow2DvectorField(fig, ax, xy2DsliceXdata, xy2DsliceYdata, dataInfo):
	X, Y = np.meshgrid(np.arange(float(dataInfo["xmin"]), float(dataInfo["xmax"]), float(dataInfo["xstepsize"])), np.arange(float(dataInfo["xmin"]), float(dataInfo["xmax"]), float(dataInfo["xstepsize"])))
	q=ax.quiver(X, Y, xy2DsliceXdata, xy2DsliceYdata)
	ax.legend()
	plt.title("{}\nsimulation time: {}".format(dataInfo["Title"], dataInfo["Stage simulation time"]))
	# valuelabels = dataInfo["valuelabels"].split()
	# valueunits = dataInfo["valueunits"].split()
	plt.xlabel("{} [{}]".format("x", dataInfo["meshunit"]))
	plt.ylabel("{} [{}]".format("y", dataInfo["meshunit"]))
	xmin, xmax = float(dataInfo["xmin"]), float(dataInfo["xmax"])
	ymin, ymax = float(dataInfo["ymin"]), float(dataInfo["ymax"])
	plt.axis(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, style="sci")

def drowAllMatched2DvectorFields(dataFileMatcher, z, outputDir):
	dataFiles = glob.glob(dataFileMatcher)
	fig, ax = plt.subplots()
	for dataFile in dataFiles:
		data = read3DdataFromFile(dataFile)
		dataInfo = readInfoDataFromFile(dataFile)
		[xy2DsliceXdata, xy2DsliceYdata ] = getXYsliceFrom3Ddata(int(dataInfo["xnodes"]), int(dataInfo["ynodes"]), z, data)
		drow2DvectorField(fig, ax, xy2DsliceXdata, xy2DsliceYdata, dataInfo)
		file = os.path.basename(dataFile)
		file = file[:-4]
		plt.savefig(outputDir+"/"+file+".png")
		plt.close()
	
def animate2DvectorField(i, z, dataFiles, ax, fig):
	ax.clear()
	data = read3DdataFromFile(dataFiles[i])
	dataInfo = readInfoDataFromFile(dataFiles[i])
	[xy2DsliceXdata, xy2DsliceYdata ] = getXYsliceFrom3Ddata(int(dataInfo["xnodes"]), int(dataInfo["ynodes"]), z, data)
	drow2DvectorField(fig, ax, xy2DsliceXdata, xy2DsliceYdata, dataInfo)
	
def makeAnimation(dataFileMatcher, z, outputFile):
	fig, ax = plt.subplots()
	dataFiles = glob.glob(dataFileMatcher)
	dataFiles.sort()
	ani = animation.FuncAnimation(fig, animate2DvectorField, interval=300, fargs=(z, dataFiles, ax, fig))
	ani.save(outputFile)
	plt.close()
	
	
if __name__ == "__main__":
	z=1
	##################
	print readInfoDataFromFile("example_vector_output.omf")
	##################
	dataFiles = glob.glob("./example_vector_output.omf");
	data = read3DdataFromFile(dataFiles[0])	
	dataInfo = readInfoDataFromFile(dataFiles[0])
	[xy2DsliceXdata, xy2DsliceYdata] = getXYsliceFrom3Ddata(int(dataInfo["xnodes"]), int(dataInfo["ynodes"]), z, data)
	fig, ax = plt.subplots()
	drow2DvectorField(fig, ax, xy2DsliceXdata, xy2DsliceYdata, dataInfo)
	plt.savefig("zdzisek.png")
	##################
	makeAnimation("/net/archive/groups/plggspinsym/WJ/jednaBariera/myfree_0.5000_mxfree_0.8660_mxtop_1_VProfileType_6_Voltage_0.1500_/*.omf", z, "marian.mp4")
	##################
	drowAllMatched2DvectorFields("/net/archive/groups/plggspinsym/WJ/jednaBariera/myfree_0.5000_mxfree_0.8660_mxtop_1_VProfileType_6_Voltage_0.1500_/*.omf", z, "./xxx")