import sys
import json
from collections import Counter
import time
import pymongo
	
def inter(a,b):
    return list(set(a)&set(b))
		
def same_path(path0,path):
	if inter(path0["top"],list(path["top"]))!=[] and (((inter(path0["end1"],list(path["end1"]))!=[]) and (inter(path0["end2"],list(path["end2"]))!=[])) or ((inter(path0["end1"],path["end2"])!=[]) and (inter(path0["end2"],path["end1"])!=[]))):
		return True
	else:
		return False

def l1_norm(v):
	s=0
	for i in v:
		s+=abs(i)
	return s

def l1_sim(v1,v2):
	d=[]
	for i in range(len(v1)):
		d.append(v1[i]-v2[i])
	return 1-l1_norm(d)/(l1_norm(v1)+l1_norm(v2))
	
def textsim(token_list):
	ST=0
	for tl in token_list:
		word_list=[]
		v1=[]
		v2=[]
		for w in tl[0]:
			if (w in word_list) == False:
				word_list.append(w)
				v1.append(1)
				v2.append(0)
			else:
				i=word_list.index(w)
				v1[i]+=1
		for j in range(len(tl[1])):
			w=t1[1][j]
			if (w in word_list) == False:
				word_list.append(w)
				v1.append(0)
				v2.append(t1[2][j])
			else:
				i=word_list.index(w)
				v2[i]+=t1[2][j]		
		ST_path=l1_sim(v1,v2)
		ST+=(tl[3]*ST_path)
	return ST
	
def Jsimilarity(path0,pathnum0,pathtk0,record):
	n=0
	d=0
	max=10
	token_list=[]
	path=list(record.keys())
	for i in range(len(record)):
		k=path[i]
		same=0
		for j in range(len(path0)):
			if path0[j]==k and abs(pathnum0[j]-record[k][0])<max:
				same=1
				w=(max-abs(pathnum0[j]-record[k][0]))/max
				n+=w
				d+=(2-w)
				token_list.append([pathtk0[j],record[k][1],record[k][2],w])
				del path0[j]
				del pathnum0[j]
				del pathtk0[j]
				break
		if same==0:
			d+=1
	d+=len(path0)
	jsim=n/d
	for t in token_list:
		t[2]/=n
	return jsim, token_list
				
if __name__ == '__main__':
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	db=myclient["codetrans"]
	tb=db[sys.argv[1]]
	tb_tl=tb[sys.argv[2]]
	
	f1=open("./node/path.json","r")
	f2=open("./node/pathnmn.json","r")
	f3=open("./node/pathtokenn.json","r")
	path_list0=json.load(f1)
	pathnum_list0=json.load(f2)
	pathtoken_list0=eval(f3.read())
	f1.close()
	f2.close()
	f3.close()
	
	path_idx=json.load(open("./pbi_index/pbi"+t_lang+"_"+s_lang+".json","w"))
	
	pathtype_list=json.load(open("./pathtype/"+t_lang+"_"+s_lang+".json","r"))
	all_path=pathtype_list["path"]
	for i in range(len(all_path)):
		for j in range(len(path_list0)):
			if same_path(path_list0[j],all_path[i]):
				path_list0[j]=pathtype_list["name"][i]
	
	tmp=db["temp"]
	for x in tb_tl.find():
		x.pop("_id")
		tmp.insert_one(x)
	for i in range(len(path_list0)):	
		pt=path_list0[i]
		pt_num=pathnum_list0[i]
		pbi=path_idx[pt]
		for j in range(len(pbi)):
			if pt_num < pbi[j]:
				pt_idx= j-1
				break
		tmp1=db["temp1"]
		for x in tmp.find({pt: pt_idx}):
			x.pop("_id")
			tmp1.insert_one(x)
		tmp.drop()
		tmp=tmp1
		tmp1.drop()
		
	for prog in tmp.find():
		record=prog["feature"]
		jsim, token_list=Jsimilarity(path_list0,pathnum_list0,pathtoken_list0,record)
		ST=textsim(token_list)
		if jsim>0.08:
			finalsim=jsim*0.75+ST*0.25
		else:
			finalsim=0
		
		f5=open("./max.txt","r")
		candidate=f5.readlines()
		if candidate != []:
			if finalsim > float(candidate[1]):
				f5.close()
				f5=open("./max.txt","w")
				f5.write(prog["file"]+"\n"+str(finalsim))
		else:
			f5.close()
			f5=open("./max.txt","w")
			f5.write(prog["file"]+"\n"+str(finalsim))
		f5.close()
