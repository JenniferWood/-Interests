package jean.nlp.fe.method;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import jean.nlp.fe.main.Documents.Document;

public class TextRank {
	static int K = 3;//窗口大小
	static double p = 0.85;//阻尼系数
	static double min_delta = 0.0001;//收敛系数
	
	ArrayList<String> wordDict;
	ArrayList<Integer> keyWords;
	Map<Integer,List<Double>> map = new HashMap<Integer,List<Double>>();
	int[] sumw;
	double[] tr;
	int[][] weight;
	public TextRank(Document document){
		wordDict = document.docWordsDict;
		keyWords = document.docKeyWords;
		sumw = new int[wordDict.size()];
		tr = new double[wordDict.size()];
		weight = new int[wordDict.size()][wordDict.size()];
		
		for(int i=0;i<=keyWords.size()-K;i++){
			int indexi = keyWords.get(i);
			tr[indexi] = 1.0;
			for(int j=i+1;j<i+K;j++){
				int indexj = keyWords.get(j);
				if(indexj==indexi) continue;
				weight[indexi][indexj]++;
				weight[indexj][indexi]++;
				sumw[indexi]++;
				sumw[indexj]++;
			}
		}
	}
	
	private void Map(){
		map = new HashMap<Integer,List<Double>>();
		for(int i=0;i<sumw.length;i++){
			for(int j=0;j<sumw.length;j++){
				if(weight[i][j]>0){
					if(!map.containsKey(j)){
						List<Double> l = new ArrayList<Double>();
						map.put(j, l);
					}
					map.get(j).add((double)weight[i][j]/sumw[i]*tr[i]);
				}
			}
		}
	}
	
	private boolean Reduce(){
		double change = 0.0;
		for(int i=0;i<sumw.length;i++){
			double sum = 0.0;
			if(map.containsKey(i)){
				for(Double d:map.get(i)){
					sum+=d;
				}
			}
			change += tr[i]-(1-p)-p*sum;
			tr[i] = (1-p)+p*sum;
		}
		change = Math.abs(change);
		//System.out.println("----change "+String.valueOf(change));
		if(change<=min_delta){
			return true;
		}
		return false;
	}
	
	public void inference(int max_iterations,int num){
		for(int i=0;i<max_iterations;i++){
			//System.out.println("Iteration "+i);
			Map();
			if(Reduce()){
				//System.out.println("已收敛");
				break;
			}
		}
		Map<Integer,Double> trmap = new HashMap<Integer,Double>();
		int i = 0;
		for(double tri:tr){
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
		int[] concur = new int[keyWords.size()];
		for(i=0;i<num;i++){
			int index = infoIds.get(i).getKey();
			System.out.print(wordDict.get(index)+"  ");
			
			int j=0;
			for(int word: keyWords){
				if(word==index)
					concur[j] = 1;
				j++;
			}
		}
		System.out.println();
		System.out.print("----关键短语：");
		
		List<String> output = new ArrayList<String>();
		
		for(i=0;i<concur.length-1;i++){
			StringBuilder sb = new StringBuilder();
			if(concur[i]==1){
				sb.append(wordDict.get(keyWords.get(i)));
				int j=i+1;
				for(;j<i+2 && concur[j]==1;j++){//每个短语最多2个词
					sb.append(wordDict.get(keyWords.get(j)));
				}
				if(!output.contains(sb.toString())) output.add(sb.toString());
				i=j+1;
			}
		}
		for(String word:output){
			System.out.print(word+" ");
		}
		System.out.println();
	}
}
