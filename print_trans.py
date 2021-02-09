f=open("./max.txt","r")
candidate=f.readlines()
print("Translation Candidate: ", candidate[0].strip(), " Similarity: ", candidate[1])
f.close()
