package jean.nlp.fe.main;

import jean.nlp.fe.conf.CommonConf;
import jean.nlp.fe.main.Documents.Document;
import jean.nlp.fe.method.TextRank;

public class IOMain {
	public static void main(String[] args){
		Documents docset = new Documents();
		docset.readDocs(CommonConf.ORIGIN_FILE_LOC);
		System.out.println("\nStep00: Getting All Text");
		System.out.println("共有"+docset.docs.size()+"个文件");
		int i = 1;
		TextRank tr;
		for(Document d:docset.docs){
			System.out.println("第"+i+"个文件包含关键词语"+d.docWordsDict.size()+"个");
			System.out.print("----");
			i++;
			tr = new TextRank(d);
			tr.inference(100, 6);
		}
		
		
	}
}
