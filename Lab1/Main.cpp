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

		int mode = (argc > 3) ? atoi(argv[3]) : 0;
		if (mode < 0 || mode >= MatrixLib::Operations::MULTIPLE_CALCULATION_MODE_NAME.size())
			throw std::exception("Invalid argument mode");

		

		double time;
		MatrixLib::Matrix<int> out = MatrixLib::Operations::multiple<int>(&a, &b, (MatrixLib::Operations::MULTIPLE_CALCULATION_MODE)mode, time);

		std::cout << time << std::endl;

	}
	catch (std::exception &e){
		std::cerr << "ERROR: " << e.what() << std::endl;
		return 1;
	}
	return 0;
}