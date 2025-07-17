#!/bin/bash
# script to put the HERWIG and THEPEG paths into the simple makefiles,
# for everything else the user is on their own!
# loop over all the files

OPENLOOPSPREFIX="/home/joonblee/WD/herwig74test/opt/OpenLoops-2.1.2"
THEPEGINCLUDE="-I/home/joonblee/WD/herwig74test/include"
GSLINCLUDE="-I/home/joonblee/WD/herwig74test/include"
FASTJETINCLUDE="-I/home/joonblee/WD/herwig74test/include"
HERWIGINCLUDE=-I/home/joonblee/WD/herwig74test/include/
HERWIGINSTALL="/home/joonblee/WD/herwig74test"
FC="gfortran"
FCLIBS=" -L/usr/lib/gcc/x86_64-linux-gnu/9 -L/usr/lib/gcc/x86_64-linux-gnu/9/../../../x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/9/../../../../lib -L/lib/x86_64-linux-gnu -L/lib/../lib -L/usr/lib/x86_64-linux-gnu -L/usr/lib/../lib -L/usr/lib/gcc/x86_64-linux-gnu/9/../../.. -lgfortran -lm -lquadmath"
CXX="g++ -std=c++14"
CXXFLAGS="-O2 -DBOOST_UBLAS_NDEBUG -Wno-deprecated-declarations -Wno-deprecated-copy"
LDFLAGS="" 
SHARED_FLAG="-shared " 

for i in *
do
# if a directory
  if [ -d $i ]; then
# check input files exists
      file=$i/Makefile.in
      if [ -e $file ]; then
	  file2=`echo $file | sed s!\.in!!`
	  echo 'Making ' $file2
	  sed "s!THEPEGINCLUDE *\=!THEPEGINCLUDE=$THEPEGINCLUDE!" < $file | \
	  sed "s!OPENLOOPSPREFIX *\=!OPENLOOPSPREFIX=$OPENLOOPSPREFIX!" | \
	  sed "s!FC *\=!FC=$FC!" | \
	  sed "s!FCLIBS *\=!FCLIBS=$FCLIBS!" | \
          sed "s!CXX *\=!CXX=$CXX!" | \
          sed "s!SHARED_FLAG *\=!SHARED_FLAG=$SHARED_FLAG!" | \
          sed "s!LDFLAGS *\=!LDFLAGS=$LDFLAGS!" | \
          sed "s!CXXFLAGS *\=!CXXFLAGS=$CXXFLAGS!" | \
	  sed "s!HERWIGINCLUDE *\=!HERWIGINCLUDE=$HERWIGINCLUDE!" | \
          sed "s!HERWIGINSTALL *\=!HERWIGINSTALL=$HERWIGINSTALL!" | \
	  sed "s!GSLINCLUDE *\=!GSLINCLUDE=$GSLINCLUDE!" | \
	  sed "s!FASTJETINCLUDE *\=!FASTJETINCLUDE=$FASTJETINCLUDE!" > $file2
      fi
  fi
done
