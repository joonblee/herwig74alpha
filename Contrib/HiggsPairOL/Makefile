# -*- Makefile -*- (for emacs)

#
# This Makefile is intended for compiling Herwig++ plugins
#
# This Makefile received very little testing, 
# any bug reports are very welcome!
#

# location of include files

OPENLOOPSPREFIX=/home/joonblee/WD/herwig74test/opt/OpenLoops-2.1.2
THEPEGINCLUDE=-I/home/joonblee/WD/herwig74test/include
HERWIGINCLUDE=-I/home/joonblee/WD/herwig74test/include/
HERWIGINSTALL=/home/joonblee/WD/herwig74test
GSLINCLUDE=-I/home/joonblee/WD/herwig74test/include 
FASTJETINCLUDE=-I/home/joonblee/WD/herwig74test/include
LDFLAGS= 
SHARED_FLAG=-shared  
FASTJETLIB = `echo $(FASTJETINCLUDE) | sed "s/-I//" | sed "s/ //"`/../lib/
LDFLAGS= -L$(FASTJETLIB) -lfastjet 
INCLUDE = $(THEPEGINCLUDE) $(HERWIGINCLUDE) $(GSLINCLUDE) $(FASTJETINCLUDE)
OPENLOOPSLIB=$(OPENLOOPSPREFIX)/lib
OPENLOOPSPROCLIB=$(OPENLOOPSPREFIX)/proclib
OL = -L$(OPENLOOPSLIB) -lopenloops -L$(OPENLOOBSPROCLIB) -lopenloops
#
# C++ flags
# 
CXX=g++ -std=c++14
CXXFLAGS=-O2 -DBOOST_UBLAS_NDEBUG -Wno-deprecated-declarations -Wno-deprecated-copy
FC=gfortran
FCFLAGS =
FCLIBS= -L/usr/lib/gcc/x86_64-linux-gnu/9 -L/usr/lib/gcc/x86_64-linux-gnu/9/../../../x86_64-linux-gnu -L/usr/lib/gcc/x86_64-linux-gnu/9/../../../../lib -L/lib/x86_64-linux-gnu -L/lib/../lib -L/usr/lib/x86_64-linux-gnu -L/usr/lib/../lib -L/usr/lib/gcc/x86_64-linux-gnu/9/../../.. -lgfortran -lm -lquadmath

default : HiggsPair.so AlpGenHandlerOL.so

%.o : %.cc %.h
	$(CXX) -fPIC $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) -c $< -o $@  

%.o : %.f
	$(FC) -fPIC $(CPPFLAGS) $(INCLUDE) $(FCFLAGS) -c $< -o $@  

HiggsPair.so : HiggsPair.o MEHiggsPairOL.o MEHiggsPairJet.o scalint.o 
	$(CXX) -fPIC $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) $(SHARED_FLAG) $(OL) $(LDFLAGS)\
	$(FCLIBS) $^ -o $@

AlpGenHandlerOL.so : AlpGenHandlerOL.o
	$(CXX) -fPIC $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) $(SHARED_FLAG) $(LDFLAGS) \
	-Wl,-undefined -Wl,dynamic_lookup \
	AlpGenHandlerOL.o -o AlpGenHandlerOL.so

clean:
	rm -f HiggsPair.so MEHiggsPairJet.o MEHiggsPairOL.o scalint.o AlpGenHandlerOL.o
	
install: 
	cp *.so $(HERWIGINSTALL)/lib/Herwig
