# -*- coding:gb2312 -*-
import math

def createData(path):
	dataset = []
	label = set()
	for line in file(path):
		line = line.strip().split(',')
		dataset.append(line[1:])
		label.add(line[-1])
	label = list(label)
	return dataset,label

def calculateIG(dataset,label,i):
	attrtype = []
	count =[]
	for data in dataset:
		if data[i] not in attrtype:
			attrtype.append(data[i])
			ctemp = [0]*len(label)
			ctemp[label.index(data[-1])] += 1
			count.append(ctemp)
		else:
			count[attrtype.index(data[i])][label.index(data[-1])] += 1

	l = len(dataset)
	ig = 0
	for datype in count:
		datypelen = sum(datype)
		ig -= sum(datype)*sum([float(c)/datypelen*math.log(float(c)/datypelen) for c in datype if c != 0])
	ig /= datypelen
	return ig,attrtype

def splitData(dataset,i,attrtype):
	newdataset = []
	for attype in attrtype:
		#print "atttype",attype
		datatype = []

		for data in dataset:
			#print "this data",data[i]
			if data[i] == attype:
				#dataset.remove(data)
				#print data[i]
				data.pop(i)
		#datatype = [data.remove(data[i]) for data in dataset if data[i] == attype]
				datatype.append(data)
		newdataset.append(datatype)
	return newdataset

def allOneType(dataset):
	labelSet = set()
	for data in dataset:
		labelSet.add(data[-1])
	if len(labelSet) > 1 : 
		return False
	else :
		return labelSet.pop()

def mostLabel(dataset):
	count = {}
	maxnum = 0

	for data in dataset:
		count.setdefault(data[-1],0)
		count[data[-1]] += 1
		if count[data[-1]] > maxnum:
			maxlabel = data[-1]
			maxnum = count[data[-1]]
	return maxlabel

def generateTree(dataset,label):
	#all p/n
	aot = allOneType(dataset)
	if aot != False:
		return aot
	if len(dataset[0]) <= 2:
		return mostLable(dataset)

	ig = 0
	attrtype = []
	select = 0
	dtree = {}
	for i in range(len(dataset[0])-1):
		igI,attrIType = calculateIG(dataset,label,i)
		if igI > ig:
			ig = igI
			attrtype = attrIType
			select = i

	dataset = splitData(dataset,select,attrtype)
	dtree[select] = []

	for i in range(len(dataset)):
		dtree[select].append(generateTree(dataset[i],label))
	#print dataset
	return dtree
	


dataset,label=createData('/Users/apple/Documents/GITHUB/Interests/Decision Tree/watermelon.data')
print generateTree(dataset,label)