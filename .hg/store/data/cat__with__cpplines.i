         E   D      ���������tZ��0M�zg,n%��f�|            u#! /bin/bash
for i in "$@"
do
	echo "#line 1 \"$i\""
	cat "$i"
done
