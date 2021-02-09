import sys
import json
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db=myclient["codetrans"]
path_idx=json.load(open("./path_idx.json","r"))

bucket_size=json.load(open("./bucket_size.json","r"))

lang_collection=["Python3","Java8","CPP14","JavaScript"]
for s_lang in lang_collection:
	tb=db[s_lang]
	lang_collection_tmp=lang_collection.remove("s_lang")
	for t_lang in lang_collection_tmp:
		tb_tl=tb[t_lang]
		pathtype_list=json.load(open("./pathtype/"+t_lang+"_"+s_lang+".json","r"))
		pathtype_list=pathtype_list["name"]
		path_idx={}
		max_bucket_size=bucket_size[t_lang+"_"+s_lang]

		for pt in pathtype_list:
			sorted_tbl=tb_tl.find().sort(pt) 
			pbi=[1]
			ct=0
			idx_ct=0
			for prog in sorted_tbl:
				pt_num=prog[pt]
				prog_tmp=prog
				prog_tmp.pop("_id")
				prog_tmp[pt+"_idx"]=idx_ct
				tb_tl.insert_one(prog_tmp)
				tb_tl.delete_one({"_id":prog["_id"]})
				if pt_num!=0:
					if ct<=max_bucket_size:
						ct+=1
					else:
						pbi.append(pt_num+1)
						ct=0
						idx_ct+=1
			path_idx[pt]=pbi
			
		f=open("./pbi_index/pbi"+t_lang+"_"+s_lang+".json","w")
		json.dump(path_idx,f)
		f.close()	


