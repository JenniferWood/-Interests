import math,random

data = []
ga = 0.001
tho = 0.0001

for line in file("bezdekIris.data"):
	line = line.strip().split(',')[:-1]
	line = [float(e) for e in line]
	data.append(line+[1.0]);

print data[0]
print data[50]

def getLb(k,beta):
	lb = 0
	for i in range(50):
		if i-5*k>=0 and i-5*k<5: continue
		bxp = sum([beta[n]*data[i][n] for n in range(5)])
		bxn = sum([beta[n]*data[50+i][n] for n in range(5)])
		lb = -bxp + math.log(1+math.pow(math.e,bxp))+math.log(1+math.pow(math.e,bxn))
	return lb

def getLbO(k,beta):
	lb = 0
	for i in range(100):
		if i==k: continue
		bx = sum([beta[n]*data[i][n] for n in range(5)])
		lb += math.log(1+math.pow(math.e,bx))
		if lb<50: lb -=bx
	return lb

def getC(beta,i):
	ly = sum([beta[n]*data[i][n] for n in range(5)])
	print i,ly

	if ly>0: return 1
	return 0

def ten():
	error = [0]*10
	for k in range(10):
		print "-------%dth----------" % k
		beta = [random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1.0]
		
		lb = getLb(k,beta)

		it = 1
		while True:
			print "iter %d" %it
			it+=1

			grad = [0.0]*5
			for i in range(50):
				if i-5*k>=0 and i-5*k<5: continue
				bxp = sum([beta[n]*data[i][n] for n in range(5)])
				g = 1.0/(1+math.pow(math.e,-bxp))-1
				grad = [grad[n]+g*data[i][n] for n in range(5)]

				bxn = sum([beta[n]*data[50+i][n] for n in range(5)])
				g = 1.0/(1+math.pow(math.e,-bxn))
				grad = [grad[n]+g*data[50+i][n] for n in range(5)]

			beta = [beta[n]-ga*grad[n] for n in range(5)]
			nlb = getLb(k,beta)

			if nlb>lb or abs(nlb-lb)<tho: break
			lb = nlb 

		print "beta",beta
		#test
		for i in range(5*k,5*k+5):
			if getC(beta,i)==0 : error[k]+=1
			if getC(beta,50+i)==1 : error[k]+=1

	print "error",error

def leftone():
	error = 0
	for k in range(100):
		print "-------%dth----------" % k
		beta = [random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),random.uniform(0,1),1.0]
		lb = getLbO(k,beta)

		it = 1
		while True:
			print "iter %d" %it
			it+=1

			grad = [0.0]*5
			for i in range(100):
				if i==k: continue
				bx = sum([beta[n]*data[i][n] for n in range(5)])
				if i<50:
					g = 1.0/(1+math.pow(math.e,-bx))-1
				else:
					g = 1.0/(1+math.pow(math.e,-bx))

				grad = [grad[n]+g*data[i][n] for n in range(5)]

			beta = [beta[n]-ga*grad[n] for n in range(5)]
			nlb = getLbO(k,beta)

			if nlb>lb or abs(nlb-lb)<tho: break
			lb = nlb 

		print "beta",beta
		#test
		if k<50 and getC(beta,k)==0 : error+=1
		if k>=50 and getC(beta,k)==1 : error+=1
	print "error",error
	print data[0],data[99]

ten()
#leftone()