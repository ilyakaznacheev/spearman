import argparse

errors = {
    1: "\nGeneration concluded by user\n",
    2: "\nError while open {}\n"
}


class ArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgParser, self).__init__(*args, **kwargs)
        # self._initiate_params()

    def _initiate_params_file_gen(self):
        """initiate default parameters"""
        self.add_argument(
            "-f", "--file-name",
            dest="filename", required=True,
            help="path to output file"
            )
        self.add_argument(
            "-n", "--number-of-values",
            dest="number", type=int, default=3,
            help="number of values in line"
            )

    def _initiate_params_reader(self):
        """initiate default parameters"""
        self.add_argument(
            "-f", "--file-name",
            dest="filename", required=True,
            help="path to output file"
            )
        self.add_argument(
            "-n", "--number-of-values",
            dest="number", type=int, default=3,
            help="number of values in line"
            )