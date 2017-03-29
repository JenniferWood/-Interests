package jean.nlp.fe.main;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

import jean.nlp.fe.assist.FileUtil;

public class Documents {
	
	ArrayList<Document> docs;
	ArrayList<String> wordDict;
	
	public Documents()
	{
		docs = new ArrayList<Document>();
		wordDict = new ArrayList<String>();
	}
	public void readDocs(String docsPath)
	{
		File[] a = new File(docsPath).listFiles();
		for(File docFile : new File(docsPath).listFiles())
		{
			if(docFile.getPath().indexOf("/.")!=-1) continue;
			Document doc = new Document(docFile.getAbsolutePath(), wordDict);
			//System.out.println("<doc>"+doc.printDoc(indexToTermMap));
			docs.add(doc);
		}
		//System.out.println("WordDict Size is "+wordDict.size()+", including "+nounDict.size()+" nouns and "+adjDict.size()+" adjectives");
	}
	
	public static class Document 
	{	
		//Sentence[] docSents;
		public ArrayList<String> docWordsDict = new ArrayList<String>();
		public ArrayList<Integer> docKeyWords = new ArrayList<Integer>();

		public Document(String docName, ArrayList<String> wordDict)
		{
			
			//Read file and initialize word index array
			ArrayList<String> docLines = new ArrayList<String>();
			ArrayList<String> words =  new ArrayList<String>();
			FileUtil.readLines(docName, docLines);
			
			for(String line : docLines)
			{
				FileUtil.tokenizeAndLowerCase(line, words);
			}
			for(String word:words){
				int index = docWordsDict.indexOf(word);
				if(index < 0){
					index = docWordsDict.size();
					docWordsDict.add(word);
				}
				docKeyWords.add(index);
			}
		}
		
		public int whichPOS(String s){//return 1-n/v/a 0-o
			String pos = s.substring(s.indexOf('/'));
			if(pos.indexOf('n')>=0 || pos.indexOf('v')>0 || pos.indexOf('a')>=0) return 1;
			else return 0;
		}
	}//Class Document
}//Class Documents
