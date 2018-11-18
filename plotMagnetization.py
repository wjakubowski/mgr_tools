import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import numpy as np
import glob, sys

def readInfoDataFromFile(fileName):
	dataInfo = {}
	with open(fileName) as file:
		for line in file:
			if line[0] == "#":
				splitedLine = line.split(":")
				if len(splitedLine) == 2:
					dataInfo[splitedLine[0][2:]] = splitedLine[1][1:-1]
				if len(splitedLine) > 2:
					dataInfo[splitedLine[0][2:]] = splitedLine[-1][:-1]
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
	for y in range(nx):
		yLinexy2DsliceXdatadata = []
		yLinexy2DsliceYdatadata = []
		for x in range(nx):
			yLinexy2DsliceXdatadata.append(data[nx*y+x][0])
			yLinexy2DsliceYdatadata.append(data[nx*y+x][1])
		xy2DsliceXdata.append(yLinexy2DsliceXdatadata)
		xy2DsliceYdata.append(yLinexy2DsliceYdatadata)
	return [xy2DsliceXdata, xy2DsliceYdata]	
	
def animate(i, z, dataFiles, ax, fig):
	ax.clear()
	data = read3DdataFromFile(dataFiles[i])
	dataInfo = readInfoDataFromFile(dataFiles[i])
	[xy2DsliceXdata, xy2DsliceYdata ] = getXYsliceFrom3Ddata(dataInfo["xnodes"], dataInfo["ynodes"], z, data)
	ax.quiver(xy2DsliceXdata, xy2DsliceYdata)
	ax.legend()
	plt.title("{}, iteracja: {}".format(dataInfo["Title"], i))
	plt.xlabel("{} [{}]".format("spin_torque_x", "1/s"))
	plt.ylabel("{} [{}]".format("spin_torque_y", "1/s"))
	
	"""	x_step = float(dataInfo["xstepsize"])
	x_nodes = int(dataInfo["xnodes"])
	plt.xticks([x_step * x_num for x_num in range(x_nodes)])
	plt.xlabel("{} [{}]".format("x", "m"))
	"""
	
def drow2DsliceOfVectorField(strRegExMatchingFiles, z):
	dataFiles = glob.glob(strRegExMatchingFiles);
	print len(dataFiles)
	for dataFile in dataFiles:
		data = read3DdataFromFile(dataFile)	
		[xy2DsliceXdata, xy2DsliceYdata ] = getXYsliceFrom3Ddata(z, data)
		fig, ax = plt.subplots()
		ax.quiver(xy2DsliceXdata, xy2DsliceYdata)
		file = dataFile[:-4]
		plt.savefig(file+".png")
		plt.close()
		
	fig, ax = plt.subplots()
	ani = animation.FuncAnimation(fig, animate, interval=1000, fargs=(z, dataFiles, ax, fig))
	ani.save("ABCD2.mp4")
	plt.close()
	
Z=2
#sys.argv[1]
drow2DsliceOfVectorField("/net/scratch/people/plgwojciechjak/jednaBariera/freeAniz_20000_myfree_0.5000_mxfree_0.8660_mxtop_1_VProfileType_6_Voltage_0.1500_/*.ovf", Z)

print readInfoDataFromFile("/net/scratch/people/plgwojciechjak/jednaBariera/freeAniz_20000_myfree_0.5000_mxfree_0.8660_mxtop_1_VProfileType_6_Voltage_0.1500_/"
	"jednaBariera-Oxs_TimeDriver-Magnetization-00-0000020.omf")
