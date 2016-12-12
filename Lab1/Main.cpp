#include <iostream>
#include <string>
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <omp.h>
#include "Exceptions.h"
#include "Matrix.hpp"


template <class T>
MatrixLib::Matrix<T>  query_matrix(const char * cmd_argument){
	if (cmd_argument == nullptr)
		return MatrixLib::Matrix<T>(std::cin);

	std::ifstream infile(cmd_argument);
	std::istream & stream = infile;
	if (infile.good())
		return MatrixLib::Matrix<T>(infile);

	std::cerr << "File " << cmd_argument << " isn't exist. Please provide matrix from console" << std::endl;
	return MatrixLib::Matrix<T>(std::cin); 
}



int main(const int argc, const char * argv[]){
	try {
		MatrixLib::Matrix<int> 
			a = query_matrix<int>(argc > 1 ? argv[1] : nullptr),
			b = query_matrix<int>(argc > 2 ? argv[2] : nullptr);

		double start, end;
		std::cout << "Start of calculation" << std::endl;
		
		start = omp_get_wtime();
		a * b;
		end = omp_get_wtime();

		std::cout << "Single thread: " << (end - start) << std::endl;

		start = omp_get_wtime();
		MatrixLib::Operations::multiple<int>(&a, &b, false);
		end = omp_get_wtime();

		std::cout << "Multi-thread: " << (end - start) << std::endl;
	}
	catch (std::exception &e){
		std::cerr << "ERROR: " << e.what() << std::endl;
		return 1;
	}
	return 0;
}