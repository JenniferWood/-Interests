package jean.nlp.fe.method;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import jean.nlp.fe.main.Documents;
import jean.nlp.fe.main.Documents.Document;

public class TFIDF {

	Documents docs;
	//int[] cwD, Dw;
	private ArrayList<String> wordDict;

	public TFIDF(Documents docs) {
		this.docs = docs;
		this.wordDict = docs.wordDict;
		// getCwDAndDw();
	}

	private int[] getCwDAndDw(String word) {
		int[] result = new int[2];
		
		for (Document d : docs.docs) {
			if (d.docWordsDict.contains(word)) {
				result[1]++;
				int docIndex = d.docWordsDict.indexOf(word);
				for (int docword : d.docKeyWords) {
					if (docword == docIndex)
						result[0]++;
				}
			}
		}
		return result;
	}

	public void Compute(Document d) {
		int[] cwd = new int[d.docWordsDict.size()];
		double[] tfidf = new double[d.docWordsDict.size()];
		int[] CwDandDw;
		
		for (int i = 0; i < d.docWordsDict.size(); i++) {
			CwDandDw = getCwDAndDw(d.docWordsDict.get(i));
			for (int docword : d.docKeyWords) {
				if (docword == i)
					cwd[i]++;
			}
			tfidf[i] = (float) cwd[i] / CwDandDw[0]
					* Math.log((double) docs.docs.size() / CwDandDw[1]);
		}
		printOutput(tfidf,d);
	}
	
	private void printOutput(double[] tfidf,Document d) {
		// TODO Auto-generated method stub
		
		int num = 5;
		Map<Integer,Double> trmap = new HashMap<Integer,Double>();
		int i = 0;
		for(double tri:tfidf){
			trmap.put(i++, tri);
		}
		List<Map.Entry<Integer, Double>> infoIds =
			    new ArrayList<Map.Entry<Integer, Double>>(trmap.entrySet());
		//排序
		Collections.sort(infoIds, new Comparator<Map.Entry<Integer, Double>>() {   
		    public int compare(Map.Entry<Integer, Double> o1, Map.Entry<Integer, Double> o2) {      
		        //return (o2.getValue() - o1.getValue()); 
		        return (-1)*(o1.getValue()).compareTo(o2.getValue());
		    }
		}); 
		
		System.out.print(num+"个关键词：");
		for(i=0;i<num;i++){
			int index = infoIds.get(i).getKey();
			System.out.print(d.docWordsDict.get(index)+"  ");
		}
		System.out.println();
	}
}
