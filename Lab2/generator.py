import random
import argparse
import numpy as np


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Lab3 data generator')
    parser.add_argument('n', type=int)
    parser.add_argument('coefficients', type=str)
    parser.add_argument('init', type=str)
    parser.add_argument('expected', type=str)

    return parser.parse_args()


def generate_matrix(n: int, x: np.ndarray) -> np.ndarray:
    result = np.random.random_integers(-50, 100, (n, n+1))
    for i in range(n):
        result[i, n] = sum(a * x[j] for j, a in enumerate(result[i]) if j != n)
    return result


def work() -> None:
    args = get_arguments()
    x = np.random.random_integers(-10000, 10000, (args.n,)) / 100
    result = generate_matrix(args.n, x)

    np.savetxt(args.coefficients, result, fmt='%d')
    np.savetxt(args.expected, x, fmt='%.8f')
    np.savetxt(args.init, x + 2, fmt='%.1f')

    pass

if __name__ == '__main__':
    work()