#!/usr/bin/env python
import sys
import math

__version__ = "0.4.1"
__author__ = "Ilya Kaznacheev"

"""
Check if Python library for CUDA
is installed, if not - enable emulation mode
"""
try:
    import pycuda.autoinit
except ImportError:
    EMULATE_MOD = True
else:
    import pycuda.driver as drv
    from pycuda.compiler import SourceModule
    import numpy as np
    EMULATE_MOD = False

import lib
import datamanagers as dm


class Model(object):
    """ Manage calculation processes """
    WINDOW = 10
    LOCALHOST = "127.0.0.1"
    MODE_NET = "net"
    MODE_FILE = "file"

    def __init__(self):
        self.core = Spearman()

        global EMULATE_MOD
        if EMULATE_MOD:
            self.cuda_manager = CUDAEmulator()
        else:
            self.cuda_manager = CUDAManager()

    def start_spearman(self, mode, **kwargs):
        self.core.set_global(int(kwargs["entry_frame"]))

        if mode == self.MODE_NET:
            self.reader = dm.AsyncReader()
        elif mode == self.MODE_FILE:
            self.reader = dm.FileReader()

        status = self.reader.start(**kwargs)

        return status

    def calculate_loop(self):
        raw_data, discr = self.reader.get()
        if raw_data:
            sorted_list = self.core.make_full_list(raw_data)
            full_dict = self._cuda_processing(sorted_list)
            return full_dict, discr
        else:
            return None, discr

    def stop_spearman(self):
        self.reader.stop()

    def _cuda_processing(self, sorted_list):
        precomp_tuple = self.core.precomparing(sorted_list)
        comp_list = self.cuda_manager.run_gpu(
            *precomp_tuple[:3], window=self.core.window
            )
        index_list = self.core.postcomparing(comp_list, precomp_tuple[3])

        full_dict = {
            "keys": precomp_tuple[3],
            "kfs": index_list
        }

        return full_dict


class CUDAManager(object):
    """ CUDA processing manager """
    CUDA_SOURSE = "sas.cu"
    MAX_THREADS = 512

    def __init__(self, file_name=CUDA_SOURSE):
        sourse = open(file_name).read()
        module = SourceModule(sourse)
        # *************************************************
        # self.context = None
        # self.device = pycuda.autoinit.device
        # self.computecc = self.device.compute_capability()
        # self.module = drv.module_from_file("sas.cubin")
        # self.module = drv.module_from_buffer("sas.ptx")
        # *************************************************
        self.cuda_exec_func = module.get_function("subtract_and_square")

        device = pycuda.tools.get_default_device()
        self.capability = device.compute_capability()

    def run_gpu(self, list_one, list_two, dimension, window):
        """ run CUDA GPU computing """
        sys.stdout.flush()
        list_one_float = np.array(list_one).astype(np.float32)
        list_two_float = np.array(list_two).astype(np.float32)
        dest = np.zeros_like(list_one_float)

        xdim = self.MAX_THREADS * self.capability[0]
        ydim = 1
        zdim = 1
        array_len = np.asarray(np.int32(len(dest)))

        blocks_per_grid = int(math.ceil(len(dest)/float(xdim)))

        self.cuda_exec_func(
            drv.Out(dest),
            drv.In(list_one_float),
            drv.In(list_two_float),
            drv.In(array_len),
            block=(xdim, ydim, zdim),
            grid=(blocks_per_grid, 1)
            )

        return dest.tolist()


class CUDAEmulator(object):
    """ emulate gpu logic
        if cuda toolkit is not instaled.
        may takes very long time """

    def __init__(self):
        lib.Debugger.deb(
            """\nWARNING: CUDA Toolkit is not installed on device!\n"""
            """         All GPU calculations will be emulated on CPU\n\n"""
            """         To prevent this in future please check\n"""
            """         your GPU device to CUDA compatibility\n"""
            """         and install CUDA Toolkit on your computer\n"""
            )

    def run_gpu(self, list_one, list_two, dimension, window):
        dest = list()

        for a, b, in zip(list_one, list_two):
            dest.append((a-b)**2)

        return dest


class Spearman(object):
    """ Computing Spearman korellation index
        based on cuda parallel computing """
    FILE_NAME = "input.txt"

    def __init__(self, file_name=FILE_NAME):
        pass

    def set_global(self, window):
        """ set global variables """
        """ set processing block size """
        self.window = window
        """ precalculate correlation denominator """
        self.denominator = float(self.window*(self.window**2-1))

    def make_full_list(self, raw_list):
        """ transponate input arrays """
        val_list = list()
        map(lambda x: val_list.append([]), xrange(len(raw_list[0])))

        for line in raw_list:
            for n, val in enumerate(line):
                val_list[n].append(float(val))

        return self.run_sorting(val_list)

    def run_sorting(self, val_list):
        """ calculate sorting indexes """
        sorted_list = list()
        for item in val_list:
            sorted_list.append(
                [i[0] for i in sorted(enumerate(item), key=lambda x:x[1])]
                )

        return sorted_list

    def precomparing(self, sorted_list):
        """ compare all list pairs """
        list_one = list()
        list_two = list()
        index = 1
        dim = 0
        length = len(sorted_list)
        while index < length:
            for num, two in enumerate(sorted_list[index:]):
                one = sorted_list[index-1]

                list_one.extend(one)
                if len(one) < self.window:
                    list_one.extend(
                        [0]*(self.window-len(one))
                        )

                list_two.extend(two)
                if len(two) < self.window:
                    list_two.extend(
                        [0]*(self.window-len(two))
                        )

                dim += 1
            index += 1

        return (list_one, list_two, dim, length)

    def postcomparing(self, korr_list, length):
        """ calculate korellation indexes """
        """ split returned list """
        splited_result = self.chunks(korr_list, self.window)
        calc_list = (self.calculate_spearman_index(x) for x in splited_result)
        """ make keys """
        named_dict = self.preset_numbers(calc_list, length)

        return named_dict

    def chunks(self, l, n):
        """ slice list to N parts """
        for i in xrange(0, len(l), n):
            yield l[i:i+n]

    def preset_numbers(self, array, number):
        """ make keys """
        number_list = range(number)
        result = dict()
        for x in number_list:
            for y in number_list[x+1:]:
                result[(x, y)] = array.next()

        return result

    def calculate_spearman_index(self, korr_list):
        coefficient = abs(1 - (6*sum(korr_list))/self.denominator)
        return coefficient


def main():
    prog = Model()
    prog.start_spearman("file", 20, entry_file="../input.txt")
    while True:
        result = prog.calculate_loop()
        if result:
            print result
        else:
            break
    prog.stop_spearman()

if __name__ == '__main__':
    main()
