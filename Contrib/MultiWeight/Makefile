# -*- Makefile -*- (for emacs)
#
# This Makefile is intended for compiling Herwig++ plugins
#
# This Makefile received very little testing, 
# any bug reports are very welcome!
#
# Location of include files
THEPEGINCLUDE=-I/home/joonblee/WD/herwig74test/include
HERWIGINCLUDE=-I/home/joonblee/WD/herwig74test/include/
GSLINCLUDE=-I/home/joonblee/WD/herwig74test/include 
#RIVETINCLUDE = -I$(shell rivet-config --includedir --cppflags)
# Messy hack, not guaranteed to work:
FASTJETLIB = `echo $(FASTJETINCLUDE) | sed "s/-I//" | sed "s/ //"`/../lib/
#LDFLAGS= -L$(FASTJETLIB) -lfastjet $(HEPMCLIB) 
#LDFLAGS +=  $(shell rivet-config --ldflags --libs)
LDFLAGS=
SHARED_FLAG=-shared  
INCLUDE = $(THEPEGINCLUDE) $(HERWIGINCLUDE) $(GSLINCLUDE) $(FASTJETINCLUDE) $(RIVETINCLUDE) $(HEPMCINCLUDE)
# C++ flags
CXX=g++ -std=c++14
CXXFLAGS=-O2 -DBOOST_UBLAS_NDEBUG -Wno-deprecated-declarations -Wno-deprecated-copy

ALLCCFILES=$(shell echo *.cc)

default : MultiWeight.so 

%.o : %.cc %.h
	$(CXX) -fPIC $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) -c -shared $< -o $@

MultiWeight.so: 
	$(CXX) $(INCLUDE) -fPIC MultiWeight.cc $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) $(SHARED_FLAG) $(LDFLAGS) -shared -o MultiWeight.so

clean:
	rm -f $(ALLCCFILES:.cc=.o) \
	MultiWeight.so 
