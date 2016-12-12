#pragma once
#include <exception>

using namespace std;

namespace MatrixLib {
	namespace Exceptions {
		class MatrixSizeMismatchException : public exception
		{
		public:
			MatrixSizeMismatchException() : exception() {}
			virtual const char* what() const throw()
			{
				return "Operation requires matrices with specific size";
			}
		};

		class MatrixSyntaxException : public exception
		{
		public:
			MatrixSyntaxException() : exception() {}
			virtual const char* what() const throw()
			{
				return "Invalid matrix syntax";
			}
		};
	}
}