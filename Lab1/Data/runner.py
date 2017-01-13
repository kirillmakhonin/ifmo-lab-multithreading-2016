import os
import argparse
import subprocess
import sys

modes = ("None", "Default",
         "Static", "Static 10", "Static 100", "Static 1000",
         "Guided 10", "Guided 100", "Guided 1000", "Dynamic 10",
         "Dynamic 100")

files = (('512x512', 'mat1_512.in', 'mat2_512.in'),
         ('2000x2000', 'mat1_2000.in', 'mat2_2000.in'))


def get_arguments() -> dict():
    default_prog_bin = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Bin', 'Lab1.exe'))
    parser = argparse.ArgumentParser(description='Start tests')
    parser.add_argument('--prog', type=str, default=default_prog_bin)
    parser.add_argument('--datasets', type=str, default=os.path.dirname(os.path.abspath(__file__)))

    return parser.parse_args()


def act():
    args = get_arguments()

    print("%15s" % '---', end='\t')
    for mode in modes:
        print("%15s" % mode, end='\t')
    for name, f1, f2 in files:
        print("\n%15s" % name, end='\t')
        for i, mode in enumerate(modes):
            prog = os.path.abspath(args.prog)
            f1_path = os.path.abspath(os.path.join(args.datasets, f1))
            f2_path = os.path.abspath(os.path.join(args.datasets, f2))
            res = subprocess.check_output([prog, f1_path, f2_path, str(i)], shell=True)
            res = float(res.decode("utf-8"))
            print('%15.3f' % res, end='\t')
            sys.stdout.flush()


if __name__ == '__main__':
    act()
