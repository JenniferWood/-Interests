from math import tanh
import sqlite3

class mlp:
    def __init__(self,dbname):
	self.con = sqlite3.connect(dbname)
    def __del__(self):
	self.con.close()
    def dbcommit(self):
	self.con.commit()

    def createtable(self):
	self.con.execute('create table hiddennodes(node_name)')
	self.con.execute('create table wordhidden(fromid,toid,weight)')
	self.con.execute('create table hiddenurl(fromid,toid,weight)')
	self.dbcommit()

    def getweight(self,fromid,toid,layer):
	if layer==0: table = 'wordhidden'
        else: table = 'hiddenurl'

	res = self.con.execute('select weight from %s where fromid=%d and toid=%d' % (table,fromid,toid)).fetchone()
	if res == None:
	    if layer==0: return -0.2
	    else: return 0.0
	else: return res[0]

    def setweight(self,fromid,toid,layer,weight):
	if layer==0: table = 'wordhidden'
	else: table = 'hiddenurl'

	res = self.con.execute('select weight from %s where fromid=%d and toid=%d' % (table,fromid,toid)).fetchone()
	if res==None:
	    self.con.execute('insert into %s(fromid,toid,weight) values(%d,%d,%f)' % (table,fromid,toid,weight))
	else:
	    self.con.execute('update %s set weight=%f where fromid=%d and toid=%d' % (table,weight,fromid,toid))
	self.dbcommit()
    
    def generatehiddenlayer(self,wordids,urlids):
	nodename = '_'.join(sorted([str(wi) for wi in wordids]))
	res = self.con.execute("select rowid from hiddennodes where node_name='%s'" % nodename).fetchone()
	if res==None:
	    cur = self.con.execute("insert into hiddennodes(node_name) values('%s')" % nodename)
	    hiddenid = cur.lastrowid

       	    for word in wordids:
	        self.con.execute('insert into wordhidden(fromid,toid,weight) values(%d,%d,%f)' % (word,hiddenid,1.0/len(wordids)))
	    for url in urlids:
	        self.con.execute('insert into hiddenurl(fromid,toid,weight) values(%d,%d,%f)' % (hiddenid,url,0.1))
	    self.dbcommit()

    def getallhiddennodes(self,wordids,urlids):
        nodes = {}
        for word in wordids:
	    tonode = self.con.execute('select toid from wordhidden where fromid=%d' % word).fetchone()
	    if tonode!=None: nodes[tonode[0]]=1
        for url in urlids:
            fromnode = self.con.execute('select fromid from hiddenurl where toid=%d' % url).fetchone()
            if fromnode!=None: nodes[fromnode[0]]=1
	return nodes.keys()

    def setupnetwork(self,wordids,urlids):
        self.hiddennodes = self.getallhiddennodes(wordids,urlids)
	self.urlids = urlids
	self.wordids = wordids

        self.ai = [1.0] * len(wordids)
        self.ah = [1.0] * len(self.hiddennodes)
        self.ao = [1.0] * len(urlids)

        self.wih = [[self.getweight(word,hnode,0) for hnode in self.hiddennodes] for word in wordids]
        self.who = [[self.getweight(hnode,url,1) for url in urlids] for hnode in self.hiddennodes]

    def feedforward(self):
	self.ai = [1.0] * len(self.wordids)

	for i in range(len(self.hiddennodes)):
	    sum = 0.0
	    for j in range(len(self.wordids)):
		sum += self.ai[j]*self.wih[j][i]
	    self.ah[i] = tanh(sum)

	for i in range(len(self.urlids)):
	    sum = 0.0
            for j in range(len(self.hiddennodes)):
                sum += self.ah[j]*self.who[j][i]
            self.ao[i] = tanh(sum)
	return self.ao
    
    def getresult(self,wordids,urlids):
	self.setupnetwork(wordids,urlids)
	if len(self.hiddennodes)==0: return [1.0] * len(urlids)	
        return self.feedforward()

    def dtanh(self,x):
	result = 1 - tanh(x)*tanh(x)
	return result

    def backpropagation(self,targets,N=0.5):
	output_delta = [0.0] * len(self.ao)
	hidden_delta = [0.0] * len(self.ah)

	for i in range(len(self.ao)):
	    output_delta[i] = (targets[i] - self.ao[i]) * self.dtanh(self.ao[i])

	for i in range(len(self.ah)):
	    sum = 0.0
	    for j in range(len(self.ao)):
		sum += output_delta[j]*self.who[i][j]
	    hidden_delta[i] = sum * self.dtanh(self.ah[i])

	for i in range(len(self.ah)):
	    for j in range(len(self.ao)):
		self.who[i][j] += N*output_delta[j]*self.ah[i]

	for i in range(len(self.ai)):
	    for j in range(len(self.ah)):
		self.wih[i][j] += N*hidden_delta[j]*self.ai[i]

    def updatedatabase(self):
	for i in range(len(self.ai)):
	    for j in range(len(self.ah)):
		self.con.execute('update wordhidden set weight = %f where fromid=%d and toid=%d' % (self.wih[i][j],self.wordids[i],self.hiddennodes[j]))

	for i in range(len(self.ah)):
	    for j in range(len(self.ao)):
                self.con.execute('update hiddenurl set weight = %f where fromid=%d and toid=%d' % (self.who[i][j],self.hiddennodes[i],self.urlids[j]))
	self.dbcommit()
 
    def trainnet(self,wordids,urlids,selectedurl):
	self.generatehiddenlayer(wordids,urlids)
	self.setupnetwork(wordids,urlids)
	self.feedforward()
	
	targets = [0.0] * len(urlids)
	targets[urlids.index(selectedurl)] = 1.0

	self.backpropagation(targets)
	self.updatedatabase()
