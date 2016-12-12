#pragma once
#include <iostream>
#include <vector>
#include "Exceptions.h"

namespace MatrixLib {
	template <class T>
	class Matrix
	{
	public:
		typedef std::vector<T> values_holder;
		typedef std::shared_ptr<values_holder> values_ptr;
	protected:
		long m_n, m_m;
		values_ptr m_values;
	public:
		Matrix(){
			m_values = values_ptr();
			m_n = m_m = 0;
		}

		Matrix(long n, long m){
			m_n = n;
			m_m = m;

			m_values = values_ptr(new values_holder());
			values_holder * data_vector = m_values.get();
			data_vector->resize(m_n * m_m);
		}

		Matrix(istream & input){
			input >> m_n >> m_m;

			if (m_m <= 0 || m_n <= 0)
				throw Exceptions::MatrixSyntaxException();

			m_values = values_ptr(new values_holder());
			values_holder * data_vector = m_values.get();
			data_vector->resize(m_n * m_m);

			T temp;

			for (int ni = 0; ni < m_n; ni++)
				for (int mi = 0; mi < m_m; mi++) {
					input >> temp;
					data_vector->at(ni * m_m + mi) = temp;
				}

		}

		~Matrix(){}


		const long getN() const { return m_n; }
		const long getM() const { return m_m; }

		virtual T const& operator[](long index) const
		{
			if (m_m == 0 || m_n == 0 || m_m * m_n <= index)
				throw std::out_of_range("Index out of range");

			return m_values.get()->at(index);
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
		MutableMatrix() : Matrix<T> {}

		MutableMatrix(long n, long m) : Matrix<T>(n, m){}

		MutableMatrix(istream & input) : Matrix<T>(input){}

		MutableMatrix(const Matrix<T> & const input) : Matrix<T>(input){
			// Copy matrix
			if (m_values != nullptr){
				values_holder * src = m_values.get();
				values_holder * new_holder = new values_holder(*src);
				m_values = values_ptr(new_holder);
			}
		}

		virtual T & operator[](long index)
		{
			if (m_m == 0 || m_n == 0 || m_m * m_n <= index)
				throw std::out_of_range("Index out of range");

			return m_values.get()->at(index);
		}

		friend istream &operator>>(istream  &input, MutableMatrix<T> &matrix)
		{
			matrix = MutableMatrix(input);
			return input;
		}
	};
	
	namespace Operations {

		template <class T>
		static Matrix<T> multiple(const Matrix<T> * const a, const Matrix<T> * const b, bool use_open_mp = true){
			if (a->getM() != b->getN())
				throw Exceptions::MatrixSizeMismatchException();


			if (a->getM() == 0 || a->getN() == 0 || b->getN() == 0 || b->getM() == 0)
				throw Exceptions::MatrixSizeMismatchException();

			long n = a->getN(), m = b->getM(), r = a->getM();
			MutableMatrix<T> result_matrix = MutableMatrix<T>(n, m);


			long i, j, k;
			long long ijk;

			if (use_open_mp){
				#pragma omp parallel for schedule(static)
				for (long long ijk = 0; ijk < n * m * r; ijk++)
				{
					long i = ijk / (m * r);
					long j = (ijk / r) % m;
					long k = ijk % r;

					result_matrix[i * m + j] = result_matrix[i * m + j] + a->operator[](i * r + k) * b->operator[](k * r + j);
				}
			}
			else {
				for (i = 0; i < n; i++)
				{
					for (j = 0; j < m; j++)
					{
						for (k = 0; k < r; k++)
						{
							result_matrix[i * m + j] = result_matrix[i * m + j] + a->operator[](i * r + k) * b->operator[](k * r + j);
						}
					}
				}
			}

			return result_matrix;
		}

	}
}
