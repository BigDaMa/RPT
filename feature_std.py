from threading import Timer
import time,os
import sys
import json
from collections import Counter
import pymongo
import unicodedata

class creat_node:
	def __init__(self, pair, token_pair, pos, value, parent):
		self.pair=pair
		self.token_pair=token_pair
		self.pos=pos
		self.value=value
		self.parent=parent
		self.child=[]

def build_tree(cur_parent,cur_parent_class):
	#print(cur_parent,"\n",cur_parent_class,"\n", eval(cur_parent))
	global node_num,n1,terminal_node
	i=cur_parent_class.pos+1
	while i<list_len:
		if node_list[i]=="(":
			if node_list[i+1]=="(":
				cur_parent_class.token_pair=1
				i+=1
				continue
			elif node_list[i+1][0].isalnum() == False:
				i+=2
				cur_parent_class.token_pair=1
				continue
			else:
				cur_parent_class.pair=1
				i+=1
				node_num+=1 #num of nodes that has been processed so far
				exec("global "+"n"+str(node_num)+";"+"n"+str(node_num)+"=creat_node(0,0,i,node_list[i],cur_parent)")
				#print("n"+str(node_num)+"=creat_node(0,0,i,node_list[i],cur_parent)")
				cur_parent_temp="n"+str(node_num)
				cur_parent_class.child.append(cur_parent_temp)
				i=build_tree(cur_parent_temp,eval(cur_parent_temp))
		elif node_list[i]==")":
			if cur_parent_class.token_pair ==1:
				cur_parent_class.token_pair=0
			else:
				return i
		elif node_list[i][0].isalnum() == False:
			i+=1
			continue
		else:
			node_num+=1
			exec("global "+"n"+str(node_num)+";"+"n"+str(node_num)+"=creat_node(0,0,i,node_list[i],cur_parent)")
			cur_parent_class.child.append("n"+str(node_num))
			terminal_node.append("n"+str(node_num))	
		i+=1
	return i

def check_exist(path, list):
	for p in list:
		if p["top"]==path["top"] and ((p["end1"]==path["end1"] and p["end2"]==path["end2"]) or (p["end1"]==path["end2"] and p["end2"]==path["end1"])):
			return p
	return False

def check_literal(node):
	if ("iteral" in node) or (node == "number") or (node == "string"):
		return True
	else:
		return False
		
def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		pass
	try:
		unicodedata.numeric(s)
		return True
	except (TypeError, ValueError):
		pass
	return False
	
def tokenize(token):
	new_token=""
	for i in range(len(token)):
		if token[i].isupper():
			new_token=new_token+" "+token[i]
		elif token[i] in ["_", "/", ",","?","!","<",">","[","]","{","}","@","#","$","|","-","^","*","&"]:
			new_token=new_token+" "
		elif token[i]==".":
			if (i!=0 and i!=len(token)-1 and is_number(token[i-1]) and is_number(token[i+1])) == False:
				new_token=new_token+" "
		else:
			new_token=new_token+token[i]
	return new_token.split()
	
def path_abstract(topv,end1v,end2v):
	abs_path={"top":[topv.value],"end1":[end1v.value],"end2":[end2v.value]}
	return abs_path

def is_exsit(path):
	if len(path["top"])!=0 and len(path["end1"])!=0 and len(path["end2"])!=0:
		return True
	else:
		return False
		
def token_sta(token_list):
	token=[]
	token_num=[]
	for t in token_list:
		if t in token:
			token_num[token.index(t)]+=1
		else:
			token.append(t)
			token_num.append(1)
	return token,token_num

def add_record(node_list,t_lang,abs_path_list,pathnum_list,pathtoken_list,pathtype,pathtypefile):	
	record={}
	path_list=[]
	for p in abs_path_list:
		p1={"top":[],"end1":[],"end2":[]}
		for i in p["top"]:
			if (i in node_list) and (t_lang in node_list[i]):
				p1["top"]=list(set(p1["top"]+node_list[i][t_lang]))
		for i in p["end1"]:
			if (i in node_list) and (t_lang in node_list[i]):
				p1["end1"]=list(set(p1["end1"]+node_list[i][t_lang]))		
		for i in p["end2"]:
			if (i in node_list) and (t_lang in node_list[i]):
				p1["end2"]=list(set(p1["end2"]+node_list[i][t_lang]))
		path_list.append(p1)
					
	ll=len(abs_path_list)
	for i in range(ll):
		cur_path=path_list[i]
		if is_exsit(cur_path):
			path={"top":cur_path["top"][0],"end1":cur_path["end1"][0],"end2":cur_path["end2"][0]}
			path1={"top":cur_path["top"][0],"end1":cur_path["end2"][0],"end2":cur_path["end1"][0]}
			if path in pathtype["path"]:
				path_name=pathtype["name"][pathtype["path"].index(path)]
			elif path1 in pathtype["path"]:
				path_name=pathtype["name"][pathtype["path"].index(path1)]
			else:
				path_name="p"+str(pathtype["amount"])
				pathtype["path"].append(path)
				pathtype["name"].append(path_name)
				pathtype["amount"]+=1
				#print(pathtype)
				f=open(pathtypefile,"w")
				json.dump(pathtype,f)
				f.close()
			token,token_num=token_sta(pathtoken_list[i])
			record[path_name]=[pathnum_list[i],token,token_num]
	
	print("Path abstracted...")
	return record

def initTime():
	global TIME
	timer1=Timer(TIME, closeProcess)
	timer1.start()
	return timer1

def closeProcess():
	print("close ")
	os._exit(0)

def proc_string(s):
	i=0
	while i<len(s):
		if s[i]=='"':
			a=i
			if s[i+1]=='"' and s[i+2]=='"':
				for j in range(i+3, len(s)):
					if s[j]=='"' and s[j+1]=='"' and s[j+2]=='"':
						b=j+3
						s=s[:a]+" thisisnote "+s[b:]
						i=a+11
						break
			else:
				st=""
				for j in range(i+1, len(s)):
					st+=s[j]
					if s[j]=='"':
						st=st[0:-1].replace("'","_").replace("(","_").replace(")","_").replace(" ","_")
						st=" "+st+" "
						b=j+1
						s=s[:a]+st+s[b:]
						i=a+len(st)-1
						break
		elif s[i]=="'":
			a=i
			if s[i+1]=="'" and s[i+2]=="'":
				for j in range(i+3, len(s)):
					if s[j]=="'" and s[j+1]=="'" and s[j+2]=="'":
						b=j+3
						s=s[:a]+" thisisnote "+s[b:]
						i=a+11
						break
			else:
				st=""
				for j in range(i+1, len(s)):
					st+=s[j]
					if s[j]=="'":
						st=st[0:-1].replace("'","_").replace("(","_").replace(")","_").replace(" ","_")
						st=" "+st+" "
						b=j+1
						s=s[:a]+st+s[b:]
						i=a+len(st)-1
						break
		i+=1
	return s

if __name__ == '__main__':
	TIME = 180
	timer1=initTime()
	#print(sys.argv[1])
	if sys.argv[2]=="JavaScript":
		fn="./testjs.txt"
	if sys.argv[2]=="Java8":
		fn="./testj8.txt"
	if sys.argv[2]=="Python3":
		fn="./testp3.txt"
	if sys.argv[2]=="CPP14":
		fn="./testc14.txt"
	f=open(fn,'r')
	lisp_tree = f.read()
	f.close()
	lisp_tree = lisp_tree.replace("("," ( ").replace(")"," ) ")
	lisp_tree=proc_string(lisp_tree)
	node_list = lisp_tree.split()[1:-1]
	list_len = len(node_list)
	node_num=1
	ROOT=creat_node(0,0,-1,"ROOT","")
	try:
		n1=creat_node(0,0,0,node_list[0],"ROOT")
	except IndexError:
		timer1.cancel()
	terminal_node=[]
	build_tree("n1",n1)
	print("Tree builded...")
	
	for x in terminal_node:
		tmp=eval(eval(x).parent)
		if len(tmp.child)>1 or eval(x).value=="thisisnote":
			terminal_node.remove(x)		
	
	abs_path_list=[]
	pathnum_list=[]
	pathtoken_list=[]
	print(len(terminal_node))
	if len(terminal_node)>800:
		os._exit(0)
	for p in range(len(terminal_node)-1):
		for q in range(p+1,len(terminal_node)):
			x=eval(terminal_node[p]).parent
			y=eval(terminal_node[q]).parent
			px=[x]
			py=[y]
			temp_list=[]
			while True:
				if x!="ROOT":
					x=eval(x).parent
					px.append(x)
				if x!="ROOT" and (x in temp_list):
					cur_abs_path=path_abstract(eval(x),eval(px[0]),eval(py[0]))
					cp=check_exist(cur_abs_path,abs_path_list)
					if cp:
						tmp=abs_path_list.index(cp)
						pathnum_list[tmp]+=1
						pathtoken_list[tmp].extend(tokenize(eval(eval(px[0]).child[0]).value))
						pathtoken_list[tmp].extend(tokenize(eval(eval(py[0]).child[0]).value))
					else:
						#print(cur_abs_path)
						abs_path_list.append(cur_abs_path)
						pathnum_list.append(1)
						tmp_token=[]
						tmp_token.extend(tokenize(eval(eval(px[0]).child[0]).value))	
						tmp_token.extend(tokenize(eval(eval(py[0]).child[0]).value))						
						pathtoken_list.append(tmp_token)
					break
				else:
					temp_list.append(x)
					if y!="ROOT":
						y=eval(y).parent
						py.append(y)
					if y!="ROOT" and (y in temp_list):
						cur_abs_path=path_abstract(eval(y),eval(px[0]),eval(py[0]))
						cp=check_exist(cur_abs_path,abs_path_list)
						if cp:
							tmp=abs_path_list.index(cp)
							pathnum_list[tmp]+=1
							pathtoken_list[tmp].extend(tokenize(eval(eval(px[0]).child[0]).value))
							pathtoken_list[tmp].extend(tokenize(eval(eval(py[0]).child[0]).value))
						else:
							#print(cur_abs_path)
							abs_path_list.append(cur_abs_path)
							pathnum_list.append(1)
							tmp_token=[]
							tmp_token.extend(tokenize(eval(eval(px[0]).child[0]).value))
							tmp_token.extend(tokenize(eval(eval(py[0]).child[0]).value))						
							pathtoken_list.append(tmp_token)												
						break
					else:
						temp_list.append(y)
	
	print("Path extracted...")
	s_lang=sys.argv[2]
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	db=myclient["codetrans"]
	lang_collection=["Python3","Java8","CPP14","JavaScript"]
	for sl in lang_collection:
		if s_lang==sl:
			tbl=db[s_lang]
			f=open("./node/"+s_lang+".json","r")
			node_match_list=json.load(f)
			lang_collection_tmp=lang_collection.remove("s_lang")
			for t_lang in lang_collection_tmp:
				tb1_tl=tb1[t_lang]
				f1=open("./pathtype/"+t_lang+"_"+s_lang+".json","r")
				pathtype=json.load(f1)
				f1.close()
				pathtypefile="./pathtype/"+t_lang+"_"+s_lang+".json"
				fp=add_record(node_match_list,t_lang,abs_path_list,pathnum_list,pathtoken_list,pathtype,pathtypefile)
				prog={"file":sys.argv[1],"feature":fp}
				for p in pathtype["name"]:
					if p in fp:
						prog[p]=fp[p][0]
					else:
						prog[p]=0
				tb1_tl.insert_one(prog)

	print("finished")
	timer1.cancel()
