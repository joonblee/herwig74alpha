# -*- Makefile -*- (for emacs)

#
# This Makefile is intended for compiling Herwig++ plugins
# You can find plugins here: INSERT URL
#
# This Makefile received very little testing, 
# any bug reports are very welcome!
#

# location of include files
THEPEGINCLUDE=-I/home/joonblee/WD/herwig74test/include
GSLINCLUDE=-I/home/joonblee/WD/herwig74test/include
HERWIGINCLUDE=-I/home/joonblee/WD/herwig74test/include/
INCLUDE = $(THEPEGINCLUDE) $(GSLINCLUDE) $(HERWIGINCLUDE)
#
# C++ flags
# 
CXX=g++ -std=c++14 
CXXFLAGS=-O2 -DBOOST_UBLAS_NDEBUG -Wno-deprecated-declarations -Wno-deprecated-copy 
LDFLAGS= 
SHARED_FLAG=-shared  

ALLCCFILES=$(shell echo *.cc)

default : HwShowerVeto.so

%.o : %.cc %.h
	$(CXX) -fPIC $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) -c -shared $< -o $@  

HwShowerVeto.so: NonBShowerVeto.o
	$(CXX) -fPIC $(CPPFLAGS) $(INCLUDE) $(CXXFLAGS) \
		NonBShowerVeto.o $(SHARED_FLAG) $(LDFLAGS)  -o HwShowerVeto.so

clean:
	rm -f $(ALLCCFILES:.cc=.o) HwShowerVeto.so
