#include <iostream>
#include "test.h"
#include "testmodule/test.hpp"
#include "testmodule/anothertest.h"

int main() {
	std::cout<<"Hello from test.cpp, calling test()\n";
	test();
	std::cout<<"Calling testmoduletest().\n";
	testmoduletest();
	std::cout<<"Calling anothertest().\n";
	anothertest();
}
