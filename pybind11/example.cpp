#include <pybind11/pybind11.h>
#include <iostream>

namespace py = pybind11;
int add(int i, int j) {
    return i + j;
}

void hello(){
  std::cout<<"hello wolrd\n";
}

PYBIND11_MODULE(example, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("add", &add, "A function which adds two numbers");
  
    m.def("hello",&inadd,"hello world");
}
