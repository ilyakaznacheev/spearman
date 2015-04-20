import sys
import pycuda.autoinit
import pycuda.driver as drv
from pycuda.compiler import SourceModule
import numpy as np
import lib


class Spearman(object):
    """docstring for Spearman"""
    WINDOW = 10
    FILE_NAME = "input.txt"
    CUDA_SOURSE = "sas.cu"

    def __init__(self, file_name=FILE_NAME):
        try:
            self.file_data = file(file_name)
        except IOError:
            sys.exit(lib.errors[2].format(file_name))

    def calculate(self, number, window=WINDOW):
        exit = False
        try:
            while not exit:
                index = 0
                # create list of lists for input data storege
                val_list = [[] for x in xrange(number)]

                while index < window:
                    line = self.file_data.readline()
                    if not line:
                        exit = True
                        break
                    # read data from line and save as columns
                    for n, val in enumerate(line.split()):
                        val_list[n].append(float(val))

                    index += 1

                sorted_list = self.run_sorting(val_list)
                index_list = self.run_comparing(sorted_list)
                print(index_list)

        except KeyboardInterrupt:
            sys.exit(lib.errors[1])

    def run_sorting(self, val_list):
        sorted_list = list()
        for item in val_list:
            sorted_list.append(
                [i[0] for i in sorted(enumerate(item), key=lambda x:x[1])]
                )

        return sorted_list

    def run_comparing(self, sorted_list):
        result = dict()
        index = 1
        while index < len(sorted_list):
            for num, item in enumerate(sorted_list[index:]):
                korr_list = self.run_gpu(sorted_list[index-1], item)
                result[(index, num+index)] = self.calculate_spearman_index(
                    korr_list
                    )
            index += 1

        return result

    def run_gpu(self, list_one, list_two):
        list_one_float = np.array(list_one).astype(np.float32)
        list_two_float = np.array(list_two).astype(np.float32)
        dest = np.zeros_like(list_one_float)

        sourse = open(self.CUDA_SOURSE).read()
        module = SourceModule(sourse)
        subtract_and_square = module.get_function("subtract_and_square")

        subtract_and_square(
            drv.Out(dest),
            drv.In(list_one_float),
            drv.In(list_two_float),
            block=(len(dest), 1, 1),
            grid=(1, 1)
            )

        # print('*'*20)
        # print(list_one_float.tolist())
        # print(list_two_float.tolist())
        # print(dest.tolist())
        # print([(x[0]-x[1])**2 for x in zip(list_one, list_two)])  # STUB!!!
        # print('*'*20)

        return dest.tolist()

    def calculate_spearman_index(self, korr_list):
        length = len(korr_list)
        return 1 - (6*sum(korr_list))/float(length*(length**2-1))


def main():
    prog = Spearman()
    prog.calculate(3)


if __name__ == '__main__':
    main()
