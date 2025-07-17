# -*- Makefile -*- (for emacs)

#
# This Makefile is intended for compiling Herwig++ plugins
#
# This Makefile received very little testing, 
# any bug reports are very welcome!
#

# location of include files
THEPEGINCLUDE=-I/home/joonblee/WD/herwig74test/include
HERWIGINCLUDE=-I/home/joonblee/WD/herwig74test/include/
HERWIGINSTALL=/home/joonblee/WD/herwig74test
GSLINCLUDE=-I/home/joonblee/WD/herwig74test/include 
LDFLAGS= 
SHARED_FLAG=-shared  
INCLUDE = $(THEPEGINCLUDE) $(HERWIGINCLUDE) $(GSLINCLUDE)
#
# C++ flags
# 
CXX=g++ -std=c++14
CXXFLAGS=-O2 -DBOOST_UBLAS_NDEBUG -Wno-deprecated-declarations -Wno-deprecated-copy
FC=gfortran
FCFLAGS =
FCLIBS= -L/usr/lib/gcc/x86_64-linux-gnu/9 -L/usr/lib/gcc/x86_64-linux-gnu/9/../../../x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/9/../../../../lib -L/lib/x86_64-linux-gnu -L/lib/../lib -L/usr/lib/x86_64-linux-gnu -L/usr/lib/../lib -L/usr/lib/gcc/x86_64-linux-gnu/9/../../.. -lgfortran -lm -lquadmath

default : MEHiggsPair.so

%.o : %.cc %.h
	$(CXX) -fPIC $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) -c $< -o $@  

%.o : %.f
	$(FC) -fPIC $(CPPFLAGS) $(INCLUDE) $(FCFLAGS) -c $< -o $@  

MEHiggsPair.so : MEHiggsPair.o scalint.o
	$(CXX) -fPIC $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) $(SHARED_FLAG) $(LDFLAGS) \
	$(FCLIBS) $^ -o $@

clean:
	rm -f MEHiggsPair.so MEHiggsPair.o scalint.o

install:
	cp *.so $(HERWIGINSTALL)/lib/Herwig
        
        
        
        