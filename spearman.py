#!/usr/bin/env python
import sys
import pycuda.autoinit
import pycuda.driver as drv
from pycuda.compiler import SourceModule
import numpy as np
import multiprocessing as mp
import lib


class ProcessManager(object):
    """docstring for ProcessManager"""
    def __init__(self):
        self.qmanager = QueueManager()
        self.core = Spearman()

    def run(self, window):
        self.core.set_global(window)

        try:
            self.start(window)
        except KeyboardInterrupt:
            sys.exit(lib.errors[1])

    def start(self, window):
        input_listener = mp.Process(
            target=self.core.input_listener,
            args=[
                self.qmanager.get_queue("input_LH")
                ]
            )
        input_handler = mp.Process(
            target=self.core.input_handler,
            args=[
                self.qmanager.get_queue("input_LH"),
                self.qmanager.get_queue("input_cuda"),
                window
                ]
            )
        cuda_handler = mp.Process(
            target=self.core.cuda_handler,
            args=[
                self.qmanager.get_queue("input_cuda"),
                self.qmanager.get_queue("cuda_output")
                ]
            )
        output_handler = mp.Process(
            target=self.core.output_handler,
            args=[
                self.qmanager.get_queue("cuda_output")
                ]
            )

        input_listener.start()
        input_handler.start()
        cuda_handler.start()
        output_handler.start()

        # self.core.cuda_handler(
        #     self.qmanager.get_queue("input_cuda"),
        #     self.qmanager.get_queue("cuda_output")
        #     )

        input_listener.join()
        input_handler.join()
        cuda_handler.join()
        output_handler.join()


class Spearman(object):
    """ Computing Spearman korellation index
        based on cuda parallel computing """
    WINDOW = 10
    FILE_NAME = "input.txt"
    CUDA_SOURSE = "sas.cu"

    def __init__(self, file_name=FILE_NAME):
        try:
            self.file_data = file(file_name)
        except IOError:
            sys.exit(lib.errors[2].format(file_name))
        self.init_cuda()

    def debug(self, message):
        print("DEBUG: {}".format(message))
        sys.stdout.flush()

    def set_global(self, window):
        # set processing block size
        self.window = window
        # precalculate korellation denominator
        self.denominator = float(self.window*(self.window**2-1))

    def input_listener(self, que_LH):
        while True:
            line = self.get_line()
            if line:
                que_LH.put(line)
            else:
                que_LH.put(None)
                return

    def input_handler(self, que_LH, que_cuda, window=WINDOW):
        # self.set_global(window)
        index = 0
        while True:
            index += 1
            line = que_LH.get()
            if not line:
                que_cuda.put(None)
                return

            if index == 1:
                val_list = [[] for x in xrange(len(line))]

            for n, val in enumerate(line):
                val_list[n].append(float(val))

            if index == window:
                sorted_list = self.run_sorting(val_list)
                que_cuda.put(sorted_list)
                index = 0

    def cuda_handler(self, que_handler, que_out):
        while True:
            sorted_list = que_handler.get()
            if not sorted_list:
                que_out.put(None)
                return
            index_list = self.run_comparing(sorted_list)
            que_out.put(index_list)

    def output_handler(self, que_cuda):
        while True:
            index_list = que_cuda.get()
            if not index_list:
                self.output_data("end of sequence")
                return

            self.output_data(index_list)

    def init_cuda(self):
        """ compile cuda sourse and
            get executable function object """
        sourse = open(self.CUDA_SOURSE).read()
        module = SourceModule(sourse)
        # *************************************************
        self.context = None
        self.device = pycuda.autoinit.device
        self.computecc = self.device.compute_capability()
        # module = drv.module_from_file("sas.cubin")
        # *************************************************
        self.cuda_exec_func = module.get_function("subtract_and_square")

    # def calculate(self, number=None, window=WINDOW):
    #     """ main function
    #         input parameters:
    #         number - number of comapred values (columns)
    #         window - size of processing block """
    #     # set processing block size
    #     self.window = window
    #     # precalculate korellation denominator
    #     self.denominator = float(self.window*(self.window**2-1))

    #     # only in case of file reading!
    #     if not number:
    #         number = self.get_column_count()

    #     exit = False
    #     try:
    #         while not exit:
    #             # create list of lists for input data storege
    #             val_list = [[] for x in xrange(number)]

    #             exit = self.get_line_block(val_list)

    #             sorted_list = self.run_sorting(val_list)
    #             index_list = self.run_comparing(sorted_list)
    #             self.output_data(index_list)

    #     except KeyboardInterrupt:
    #         sys.exit(lib.errors[1])

    # def get_column_count(self):
    #     """ quick count calculating """
    #     with open(self.FILE_NAME) as counter:
    #         return len(counter.readline().split())

    # def get_line_block(self, val_list):
    #     """ receive block of input dara """
    #     index = 0
    #     while index < self.window:
    #         line = self.get_line()
    #         if not line:
    #             return True
    #         # read data from line and save as columns
    #         for n, val in enumerate(line):
    #             val_list[n].append(float(val))
    #         index += 1
    #     return False

    def output_data(self, odata):
        """ outputing data """
        print(odata)
        sys.stdout.flush()
        # pipe/queue will be implemented

    def get_line(self):
        """ receive one frame of input data """
        raw_line = self.file_data.readline()
        # http will be implemented
        return raw_line.split()

    def run_sorting(self, val_list):
        """ calculate sorting indexes """
        sorted_list = list()
        for item in val_list:
            sorted_list.append(
                [i[0] for i in sorted(enumerate(item), key=lambda x:x[1])]
                )

        return sorted_list

    def run_comparing(self, sorted_list):
        """ compare all list pairs """
        list_one = list()
        list_two = list()
        index = 1
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
            index += 1

        # run cuda computing
        korr_list = self.run_gpu(list_one, list_two, length)
        # split returned list
        splited_result = self.chunks(korr_list, self.window)
        calc_list = (self.calculate_spearman_index(x) for x in splited_result)
        # make keys
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
                result[(x+1, y+1)] = array.next()

        return result

    def run_gpu(self, list_one, list_two, dimension):
        """ run cuda computing """
        self.debug(list_one)
        self.debug(list_two)
        sys.stdout.flush()
        list_one_float = np.array(list_one).astype(np.float32)
        list_two_float = np.array(list_two).astype(np.float32)
        dest = np.zeros_like(list_one_float)
        self.debug(dest.size)
        self.cuda_exec_func(
            drv.Out(dest),
            drv.In(list_one_float),
            drv.In(list_two_float),
            block=(len(dest), dimension, 1),  # TODO: add Y dimension
            grid=(1, 1),
            shared=dest.size
            )

        return dest.tolist()

    def calculate_spearman_index(self, korr_list):
        coefficient = abs(1 - (6*sum(korr_list))/self.denominator)
        return coefficient


class QueueManager(object):
    """docstring for QueueManager"""
    def __init__(self):
        self.queue_pull = dict()

    def get_queue(self, name):
        if name not in self.queue_pull:
            self.queue_pull[name] = mp.Queue()
        return self.queue_pull[name]


def main():
    prog = ProcessManager()
    prog.run(10)


if __name__ == '__main__':
    main()
