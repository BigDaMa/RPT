source ~/.bash_profile
for f in ` ls $1 `
do
        f=$1"/"$f
        file=$f
        if [ "${file##*.}"x = "js"x ];then
                grun JavaScript program -tree $file > testjs.txt
                s="JavaScript"
        elif [ "${file##*.}"x = "java"x ];then
                grun Java8 compilationUnit -tree $file > testj8.txt
                s="Java8"
        elif [ "${file##*.}"x = "py"x ];then
                grun Python3 file_input -tree $file > testp3.txt
                s="Python3"
        elif [ "${file##*.}"x = "cpp"x ];then
                grun CPP14 translationunit -tree $file > testc14.txt
                s="CPP14"
        fi
        python3 feature_std.py $f $s
done
