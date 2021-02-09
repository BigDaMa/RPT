source ~/.bash_profile
if [ -f "./max.txt" ];then
	rm max.txt
fi
touch max.txt
file=$1
#generate CST for input
if [ "${file##*.}"x = "js"x ];then
	grun JavaScript program -tree $file > test.txt
	s="JavaScript"
elif [ "${file##*.}"x = "java"x ];then
	grun Java8 compilationUnit -tree $file > test.txt
	s="Java8"
elif [ "${file##*.}"x = "py"x ];then
	grun Python3 file_input -tree $file > test.txt
	s="Python3"
elif [ "${file##*.}"x = "cpp"x ];then
	grun CPP14 translationunit -tree $file > test.txt
	s="CPP14"
fi
python3 representation.py $s $2
if [ $2 = "Java8" ];then
        ft="java"
elif [ $2 = "JavaScript" ];then
        ft="js"
elif [ $2 = "Python3" ];then
        ft="py"
elif [ $2 = "CPP14" ];then
        ft="cpp"
fi

python3 retrieval.py $s $2
python3 print_trans.py
