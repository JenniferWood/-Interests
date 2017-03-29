import urllib2,sqlite3,re,socket,time,sys,nn
from bs4 import *
from urlparse import urljoin
from math import log
sys.setrecursionlimit(10000)
mynet = nn.mlp('nn.db')

#stopwords = ['the','a','an','the','of','in','at','is','it']
stopwords=["hasn","havn","wasn","wern","shouldn","won","dosn","don","couldn","arn","a","able","about","above","according","accordingly","across","actually","after","afterwards","again","against","all","allow","allows","almost","alone","along","already","also","although","always","am","among","amongst","an","and","another","any","anybody","anyhow","anyone","anything","anyway","anyways","anywhere","apart","appear","appreciate","are","around","as","aside","asking","associated","at","available","away","awfully","b","be","became","because","become","becomes","becoming","been","before","beforehand","behind","being","believe","below","beside","besides","best","better","between","beyond","both","brief","but","by","came","can","cannot","cant","cause","causes","certain","certainly","changes","clearly","co","com","come","comes","concerning","consequently","consider","considering","contain","containing","contains","corresponding","could","course","currently","d","definitely","described","despite","did","different","do","does","doing","done","down","downwards","during","e","each","edu","eg","eight","either","else","elsewhere","enough","entirely","especially","et","etc","even","ever","every","everybody","everyone","everything","everywhere","ex","exactly","example","except","f","far","few","fifth","first","five","followed","following","follows","for","former","formerly","forth","four","from","further","furthermore","g","get","gets","getting","given","gives","go","goes","going","gone","got","gotten","greetings","h","had","happens","hardly","has","have","having","he","hello","help","hence","her","here","hereafter","hereby","herein","hereupon","hers","herself","hi","him","himself","his","hither","hopefully","how","howbeit","however","i","ie","if","ignored","immediate","in","inasmuch","inc","indeed","indicate","indicated","indicates","inner","insofar","instead","into","inward","is","it","its","itself","j","just","k","keep","keeps","kept","know","knows","known","l","last","lately","later","latter","latterly","least","less","lest","let","like","liked","likely","little","look","looking","looks","ltd","m","mainly","many","may","maybe","me","mean","meanwhile","merely","might","more","moreover","most","mostly","much","must","my","myself","n","name","namely","nd","near","nearly","necessary","need","needs","neither","never","nevertheless","new","next","nine","no","nobody","non","none","noone","nor","normally","not","nothing","novel","now","nowhere","o","obviously","of","off","often","oh","ok","okay","old","on","once","one","ones","only","onto","or","other","others","otherwise","ought","our","ours","ourselves","out","outside","over","overall","own","p","particular","particularly","per","perhaps","placed","please","plus","possible","presumably","probably","provides","q","que","quite","qv","r","rather","rd","re","really","reasonably","regarding","regardless","regards","relatively","respectively","right","s","said","same","saw","say","saying","says","second","secondly","see","seeing","seem","seemed","seeming","seems","seen","self","selves","sensible","sent","serious","seriously","seven","several","shall","she","should","since","six","so","some","somebody","somehow","someone","something","sometime","sometimes","somewhat","somewhere","soon","sorry","specified","specify","specifying","still","sub","such","sup","sure","t","take","taken","tell","tends","th","than","thank","thanks","thanx","that","thats","the","their","theirs","them","themselves","then","thence","there","thereafter","thereby","therefore","therein","theres","thereupon","these","they","think","third","this","thorough","thoroughly","those","though","three","through","throughout","thru","thus","to","together","too","took","toward","towards","tried","tries","truly","try","trying","twice","two","u","un","under","unfortunately","unless","unlikely","until","unto","up","upon","us","use","used","useful","uses","using","usually","uucp","v","value","various","very","via","viz","vs","w","want","wants","was","way","we","welcome","well","went","were","what","whatever","when","whence","whenever","where","whereafter","whereas","whereby","wherein","whereupon","wherever","whether","which","while","whither","who","whoever","whole","whom","whose","why","will","willing","wish","with","within","without","wonder","would","would","x","y","yes","yet","you","your","yours","yourself","yourselves","z",""," "]

class crawler:
    def __init__(self,dbname):
	self.con = sqlite3.connect(dbname)
    def __del__(self):
	self.con.close()
    def dbcommit(self):
	self.con.commit()

    def getentryid(self,table,field,value,createnew=True):
	cur = self.con.execute("select rowid from %s where %s='%s'" % (table,field,value))
	res = cur.fetchone()

	if res==None:
	    #insert
	    cur = self.con.execute("insert into %s(%s) values('%s')" % (table,field,value))
	    result = cur.lastrowid
	    if table=='urllist':
		cur = self.con.execute("insert into pagerank(urlid,score) values(%d,1.0)"%result)
	    return result
	else:
	    return res[0] 

    def addtoindex(self,url,soup):
	if self.isindexed(url): return
	print 'Indexing %s' % url
		
	text = self.gettextonly(soup)
	if text == None: return
	words = self.separatewords(text)
	
	urlid = self.getentryid('urllist','url',url)
	for i in range(len(words)):
	    word = words[i]
	    #if word in stopwords: continue
	    wordid = self.getentryid('wordlist','word',word)
	    self.con.execute('insert into wordlocation(urlid,wordid,wordlocation) values(%d,%d,%d)' % (urlid,wordid,i))
	
    def gettextonly(self,soup):
	v = soup.string
	if v==None:
	    try:
	    	c=soup.contents
	    except:
		return None
	    resulttext=''
	    for t in c:
		subtext = self.gettextonly(t)
		resulttext += subtext+'\n'
	    return resulttext
	else:
	    return v.strip()

    def separatewords(self,text):
	words = re.compile('\\W+').split(text)
	#p = re.compile('(Ph\.D|[CcGg]\+\+)|(\$\d+(\.\d+)?)|(\d+(\.\d+)?[%])|(\w+(-\w+)*)')
	#wl = p.findall(text)
	#wordlist = []
	'''
	for wunit in wl:
	    if wunit[5]!='': 
		if wunit[3] not in stopwords: wordlist.append(wunit[5].lower())
	    elif wunit[0]!='': wordlist.append(wunit[0].lower())
	return wordlist
	'''
	return [word.lower() for word in words if word!=''] 

    def isindexed(self,url):
	cur = self.con.execute("select rowid from urllist where url='%s'" % url).fetchone()
	if cur != None:
	    v = self.con.execute("select * from wordlocation where urlid = %s" % cur[0]).fetchone()
	    if v != None: return True
	return False

    def addlinkref(self,urlFrom,urlTo,linkText):
	fromid = self.getentryid('urllist','url',urlFrom)
	toid = self.getentryid('urllist','url',urlTo)
	cur = self.con.execute("insert into link(fromid,toid) values(%d,%d)" %(fromid,toid))
	linkid = cur.lastrowid
	
	linkwords = self.separatewords(linkText)
	for word in linkwords:
	    wordid = self.getentryid('wordlist','word',word)
	    self.con.execute("insert into linkword(wordid,linkid) values(%d,%d)" % (wordid,linkid))

    def crawl(self,pages,depth=2):
	for i in range(depth):
	    newpages=set()
	    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
	    for page in pages:
		try:
		    req = urllib2.Request(url=page,headers=headers)
		    c=urllib2.urlopen(req,timeout=20)
		except:
		    print "Could Not Open %s" % page
		    continue
		soup=BeautifulSoup(c.read(),'lxml')
		self.addtoindex(page,soup)
		
		links = soup('a')
		for link in links:
		    if('href' in dict(link.attrs)):
			url = urljoin(page,link['href'])
			if url.find("'")!=-1: continue
			if url.find("wikipedia.org/wiki"):
			    if url.find("en.wiki")==-1: continue

			url=url.split('#')[0]
			if url.endswith(('jpg','jpeg','svg','png','gif','bmp')): continue

			if url[0:4]=='http' and not self.isindexed(url):
			    newpages.add(url)
			linkText=self.gettextonly(link)
			self.addlinkref(page,url,linkText)
		
		self.dbcommit()
		time.sleep(0.5)
	    pages = newpages

	self.calculatepagerank()

    def calculatepagerank(self,iterations=100,min_delta=0.0001):
	'''
	self.con.execute('drop table if exists pagerank')
	self.con.execute('create table pagerank(urlid primary key,score)')
	self.con.execute('insert into pagerank select rowid,1.0 from urllist')

	self.dbcommit()
	
	for i in range(iterations):
	    print 'PageRanking',i
	    for (url,) in self.con.execute('select urlid from pagerank'):
		pr = 0.15
		for (furl,) in self.con.execute('select distinct fromid from link where toid=%d' % url):
		    lpr = self.con.execute('select score from pagerank where urlid=%d' % furl).fetchone()[0]
		    lnum = self.con.execute('select count(*) from link where fromid=%d' % furl).fetchone()[0]
		    pr += 0.85*lpr/lnum
		self.con.execute('update pagerank set score=%f where urlid=%d' % (pr,url))
	    self.dbcommit()   	
	'''
	urls = self.con.execute('select urlid from pagerank').fetchall()
	pr = [1.0]*len(urls)
	neighbors = {}

	for i in range(iterations):
	    print 'PageRanking',i
	    mr = {}
	    for j in range(len(urls)):
		url = urls[j][0]
		if url not in neighbors:
		    neighbors[url] = self.con.execute("select distinct toid from link where fromid=%d" % url).fetchall()
	        on = len(neighbors[url])
		for (neibornodes,) in neighbors[url]:
		    if neibornodes not in mr:
			mr[neibornodes] = []
		    mr[neibornodes].append(pr[j]/on)
	    newpr = [0.15+0.85*sum(mapping) for mapping in mr.values()]
	    #print newpr[0:10]
	    change = sum([pr[k]-newpr[k] for k in range(len(pr))])
	    print "Change",change
	    if change <= min_delta:break
	    pr = newpr
	
	#update db
	print 'Updating PageRank in DataBase'
	for i in range(len(pr)):
	    self.con.execute('update pagerank set score=%f where urlid=%d' %(pr[i],urls[i][0]))
	self.dbcommit()

    def createindextables(self):
	self.con.execute('create table link(fromid,toid)')
	self.con.execute('create table urllist(url)')
	self.con.execute('create table wordlocation(urlid,wordid,wordlocation)')
	self.con.execute('create table wordlist(word)')
	self.con.execute('create table linkword(linkid,wordid)')
	self.con.execute('create index urlidx on urllist(url)')
	self.con.execute('create index wordidx on wordlist(word)')
	self.con.execute('create index wordurlx on wordlocation(wordid)')
	self.con.execute('create index urltoidx on link(toid)')
	self.con.execute('create index urlfromidx on link(fromid)')
	
	self.dbcommit()

class searcher:
    def __init__(self,dbname):
	self.con = sqlite3.connect(dbname)
    def __del__(self):
	self.con.close()

    def getmatchrows(self,q):
	fieldlist = 'w0.urlid'
	valuelist = ''
	tablelist = ''
	wordids = []

	q = q.lower()
	words = q.split(' ')
	tbno = 0

	for i in range(len(words)):
	    cur = self.con.execute("select rowid from wordlist where word='%s'" % words[i]).fetchone()
	    if cur != None:
		wid = cur[0]
		wordids.append(wid)
		if tbno>0 :
		    tablelist += ','
		    valuelist += ' and w%d.urlid = w%d.urlid and ' % (tbno-1,tbno)
		fieldlist += ',w%d.wordlocation' % tbno
		valuelist += 'w%d.wordid=%d' % (tbno,wid)
		tablelist += 'wordlocation w%d' % tbno
		tbno+=1
	
	if len(wordids) > 0:
	    sqlstr = "select %s from %s where %s" % (fieldlist,tablelist,valuelist)
	    print sqlstr
	    res = self.con.execute(sqlstr)
	    rows = [row for row in res]
	    print "get matched rows"
	    return rows,wordids
	else:
	    return [],[]

    def getscores(self,rows,wordid):
	totalscores = dict([(row[0],0) for row in rows])
	#weights = [(1.0,self.frequencyscore(rows)),(1.0,self.locationscore(rows)),(1.1,self.wordsdistance(rows)),(1.0,self.pagerankscore(rows)),(1.0,self.linktextscore(rows,wordid)),(0.5,self.nnscore(rows,wordid))]
	weights = [(1.0,self.tfidfscore(rows,wordid)),(1.0,self.locationscore(rows)),
(1.1,self.wordsdistance(rows)),(0.8,self.linktextscore(rows,wordid)),(0.5,self.nnscore(rows,wordid))]
	
	for (weight,scores) in weights:
	    for url in totalscores:
		totalscores[url] += weight*scores[url]
	return totalscores

    def geturlname(self,id):
	return self.con.execute("select url from urllist where rowid=%d" % id).fetchone()[0]

    def combinedict(self,dicta,dictb,times):
	w = 1.0 - times*0.2 #set weights
	if w <= 0: w=0.1
	for key in dictb:
	    if key in dicta:
		dicta[key] += w*dictb[key]
	    else: dicta[key] = dictb[key]
	return dicta

    def query(self,q):
	qs = re.compile(r' OR ').split(q)
	scores = {}
	allwordids = []
	times = 0
	for oneq in qs:	
	    rows,wordids = self.getmatchrows(oneq)
	    allwordids.extend(wordids)
	    allwordids.append(9889)
	    if rows == []:
	        continue
	    ones = self.getscores(rows,wordids)
	    scores = self.combinedict(scores,ones,times)
	    times += 1
	if len(scores)==0:
	    print "Sorry. No Result!"
	    return
	allwordids.pop()
	rankedscores = sorted([(score,url) for (url,score) in scores.items()],reverse=1)
	showlen = 10+5*(len(qs)-1)
	index = 1
	for (score,urlid) in rankedscores[0:showlen]:
	    print '%d\t%f\t%s' % (index,score,self.geturlname(urlid))
	    index += 1
	
	urlids = [r[1] for r in rankedscores[0:showlen]]
	mynet.generatehiddenlayer(wordids,urlids)
	
	click = raw_input('click:')
	if click!=None and click!='0':
	    mynet.trainnet(allwordids,urlids,urlids[int(click)-1])
	    
	#return wordids,[r[1] for r in rankedscores[0:10]]

    def normalizescores(self,scores,smallerBetter=False):
	vsmall = 0.00001
	if smallerBetter:
	    minscore = min(scores.values())
	    return dict([(u,float(minscore)/max(vsmall,l)) for (u,l) in scores.items()])
	else:
	    maxscore = max(scores.values())
	    if maxscore==0: maxscore=vsmall
	    return dict([(u,float(c)/maxscore) for (u,c) in scores.items()])

    #Traditional Method 1 Based on Content
    def frequencyscore(self,rows):
	counts = dict([(row[0],0) for row in rows])
	for row in rows:
	    counts[row[0]]+=1
	return self.normalizescores(counts)

    #Traditional Method 2 Based on Content
    def locationscore(self,rows):
	print "*****LOCATION SCORE*******"
	locations = dict([(row[0],1000000) for row in rows])
	for row in rows:
	    loc = sum(row[1:])
	    if loc < locations[row[0]]: locations[row[0]]=loc
	return self.normalizescores(locations,smallerBetter=True)

    #Traditional Method 3 Based on Content
    def wordsdistance(self,rows):
	print "*****WORD DISTANCE*******"
	if len(rows[0]) <= 2:
	    return dict([(row[0],1.0) for row in rows])

	distances = dict([(row[0],1000000) for row in rows])
	for row in rows:
	    dist = sum([abs(row[i]-row[i-1]) for i in range(2,len(row))])
	    if dist < distances[row[0]]: distances[row[0]]=dist
	return self.normalizescores(distances,smallerBetter=True)
    
    #modified TF-IDF
    def tfidfscore(self,rows,wordids):
	print "*****TFIDF*******"
	nd = self.con.execute('select count(*) from urllist').fetchone()[0]
	scores = dict([(row[0],0.0) for row in rows])
	prscores = self.pagerankscore(rows,neednorm=False)
	for url in scores:
	    tfidf = 0.0
	    for word in wordids:
		cur = self.con.execute('select * from wordlocation where wordid=%d' % word).fetchall()
		cwD = len(cur)
		cwd = sum([1 for tuple in cur if tuple[0]==url and tuple[1]==word])
		nwD = len(set([tuple[0] for tuple in cur]))
		tfidf += float(cwd)/cwD * log(nd/nwD,2)
	    scores[url] = tfidf*prscores[url]	
	return self.normalizescores(scores)
	
    #PageRank
    def pagerankscore(self,rows,neednorm = True):
	print "*****PAGERANK*******"
	prs = dict([(row[0],self.con.execute('select score from pagerank where urlid=%d' % row[0]).fetchone()[0]) for row in rows])
	if neednorm: return self.normalizescores(prs)
	else: return prs

    #Using Link Text
    def linktextscore(self,rows,wordids):
	print "*****LINK SCORE*******"
	scores = dict([(row[0],0) for row in rows])
	for wordid in wordids:
	    for (fromid,toid) in self.con.execute('select link.fromid,link.toid from link,linkword where wordid=%d and link.rowid=linkword.linkid' % wordid):
		if toid in scores:
		    scores[toid] += self.con.execute('select score from pagerank where urlid=%d' % fromid).fetchone()[0]
	return self.normalizescores(scores)

    #MLP
    def nnscore(self,rows,wordids):
	print "*****NN*******"
	urlids = [urlid for urlid in set([row[0] for row in rows])]
	nnres = mynet.getresult(wordids,urlids)
	scores = dict([(urlids[i],nnres[i]) for i in range(len(nnres))])
	return self.normalizescores(scores)
