SRC = main.cpp
CXX = g++
CXXFLAGS = -O3 -std=c++14 -Ienv utils.cpp
LIBFLAGS = --target=x86_64-apple-darwin -Wno-return-type-c-linkage -shared -fpic -o
EXE = $(SRC:.cpp=.x)

.SUFFIXES:
SUFFIXES =

.SUFFIXES: .cpp .x

VPATH = env

all: $(EXE) libkite.so


.PHONY: all

%.x: %.cpp

	$(CXX) $< -o $@ $(CXXFLAGS)

libkite.so: libkite.cpp
			$(CXX) $(LIBFLAGS) $@ $< $(CXXFLAGS)


clean:
		rm -f $(EXE) *~
		rm libkite.so

.PHONY: clean

main.x: kite.hpp constants.hpp vect.hpp utils.cpp wind.hpp

libkite.so: kite.hpp constants.hpp vect.hpp utils.cpp wind.hpp
