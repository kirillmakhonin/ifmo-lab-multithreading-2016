#pragma once
#include <iostream>
#include <vector>
#include "Exceptions.h"
#include <omp.h>


namespace MatrixLib {
	template <class T>
	class Matrix
	{
	public:
		typedef T* values_holder;
	protected:
		long m_n, m_m;
		values_holder m_values;
	public:
		Matrix(){
			m_values = nullptr;
			m_n = m_m = 0;
		}

		Matrix(long n, long m){
			m_n = n;
			m_m = m;

			m_values = (T*)calloc(n * m, sizeof(T));
		}

		Matrix(istream & input){
			input >> m_n >> m_m;

			if (m_m <= 0 || m_n <= 0)
				throw Exceptions::MatrixSyntaxException();

			m_values = (T*)calloc(m_n * m_m, sizeof(T));

			T temp;

			for (int ni = 0; ni < m_n; ni++)
				for (int mi = 0; mi < m_m; mi++) {
					input >> temp;
					m_values[ni * m_m + mi] = temp;
				}

		}

		Matrix(const Matrix<T> & const input){
			long count_of_elements = input.getM() * input.getN();
			void * new_holder = (T*)calloc(count_of_elements, sizeof(T));
			memcpy(new_holder, input.m_values, sizeof(T) * count_of_elements);
			m_values = (T*)new_holder;
			m_m = input.m_m;
			m_n = input.m_n;
		}

		~Matrix(){
			if (m_values != nullptr)
				free((void*)m_values);
		}


		const long getN() const { return m_n; }
		const long getM() const { return m_m; }

		T const& operator[](long index) const
		{
			return m_values[index];
		}

		T const& at(long index) const
		{
			return m_values[index];
		}
		
		friend ostream &operator<<(ostream &out, const Matrix<T> & matrix)
		{
			long n = matrix.getN(), m = matrix.getM();

			out << n << " " << m << std::endl;
			if (n > 0 && m > 0){
				for (int ni = 0; ni < n; ni++){
					for (int mi = 0; mi < m; mi++) {
						out << matrix[ni * m + mi];
						if (mi != m - 1)
							out << " ";
					}
					out << std::endl;
				}
			}

			return out;
		}

		friend istream &operator>>(istream  &input, Matrix<T> &matrix)
		{
			matrix = Matrix(input);
			return input;
		}

		Matrix<T> operator* (const Matrix<T> & const b)
		{
			return Operations::multiple(this, &b, true);
		}
	};

	template <class T>
	class MutableMatrix : public Matrix<T>
	{
	public:
		MutableMatrix() : Matrix<T> {
		}

		MutableMatrix(long n, long m) : Matrix<T>(n, m){
		}

		MutableMatrix(istream & input) : Matrix<T>(input){
		}

		MutableMatrix(const Matrix<T> & const input) : Matrix<T>(input){
			// Copy matrix
			if (m_values != nullptr){
				long count_of_elements = input.getM() * input.getN();
				void * new_holder = (T*)calloc(count_of_elements, sizeof(T));
				memcpy(new_holder, m_values, sizeof(T) * count_of_elements);
				m_values = (T*)new_holder;
			}
		}

		T & at(long index){
			return m_values[index];
		}

		T & operator[](long index)
		{
			return m_values[index];
		}

		friend istream &operator>>(istream  &input, MutableMatrix<T> &matrix)
		{
			matrix = MutableMatrix(input);
			return input;
		}
	};
	
	namespace Operations {

		enum MULTIPLE_CALCULATION_MODE {
			NONE,
			DEFAULT,
			STATIC,
			STATIC_10,
			STATIC_100,
			STATIC_1000,
			GUIDED_10,
			GUIDED_100,
			GUIDED_1000,
			DYNAMIC_10,
			DYNAMIC_100
		};

		std::vector<std::string> MULTIPLE_CALCULATION_MODE_NAME = {
			"None", 
			"Default",
			"Static",
			"Static 10",
			"Static 100",
			"Static 1000",
			"Guided 10",
			"Guided 100",
			"Guided 1000",
			"Dynamic 10",
			"Dynamic 100"
		};


		template <class T>
		inline void calculate_multiple_one_line(MutableMatrix<T> & result_matrix, const Matrix<T> * const a, const Matrix<T> * const b, long long & ijk, long long & m, long long &r){
			int i = ijk / (m * r);
			int j = (ijk / r) % m;
			int k = ijk % r;

			result_matrix[i * m + j] = result_matrix[i * m + j] + a->at(i * r + k) * b->at(k * r + j);
		}

		template <class T>
		static MutableMatrix<T> multiple(const Matrix<T> * const a, const Matrix<T> * const b, MULTIPLE_CALCULATION_MODE mode, double & time){
			if (a->getM() != b->getN())
				throw Exceptions::MatrixSizeMismatchException();


			if (a->getM() == 0 || a->getN() == 0 || b->getN() == 0 || b->getM() == 0)
				throw Exceptions::MatrixSizeMismatchException();

			long long n = a->getN(), m = b->getM(), r = a->getM();
			MutableMatrix<T> result_matrix = MutableMatrix<T>(n, m);


			long long i, j, k;
			long long ijk;
			long long ijk_max = n * m * r;

			double start, end;
			start = omp_get_wtime();
			if (mode == DEFAULT){
				#pragma omp parallel for
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == STATIC){
				#pragma omp parallel for schedule(static)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == STATIC_10){
				#pragma omp parallel for schedule(static, 10)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == STATIC_100){
				#pragma omp parallel for schedule(static, 100)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == STATIC_1000){
				#pragma omp parallel for schedule(static, 1000)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == GUIDED_10){
				#pragma omp parallel for schedule(guided, 10)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == GUIDED_100){
				#pragma omp parallel for schedule(guided, 100)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == GUIDED_1000){
				#pragma omp parallel for schedule(guided, 1000)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == DYNAMIC_10){
				#pragma omp parallel for schedule(dynamic, 10)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == DYNAMIC_100){
				#pragma omp parallel for schedule(dynamic, 100)
				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else if (mode == NONE) {

				for (long long ijk = 0; ijk < ijk_max; ijk++)
				{
					calculate_multiple_one_line(result_matrix, a, b, ijk, m, r);
				}
			}
			else
				throw std::exception("Invalid argument for mode");
			end = omp_get_wtime();
			time = end - start;

			return result_matrix;
		}

	}
}
