#!/usr/bin/env python
import sys
import random
import time
import lib


class FileGenerator(object):
    SLEEP_TIME = 1000

    def __init__(self, filename):
        try:
            self.man_file = open(filename, 'w')
        except IOError:
            sys.exit(lib.errors[2].format(filename))

    def run(self, number):
        while True:
            try:
                string = self.generate(number)
                self.man_file.write(string)
                time.sleep(self.SLEEP_TIME/1000)
            except KeyboardInterrupt:
                sys.exit(lib.errors[1])

    def generate(self, number):
        line = [str(random.random()) for x in range(int(number))]
        return ' '.join(line) + '\n'


if __name__ == '__main__':
    arg_parser = lib.ArgParser(sys.argv[1:])
    arg_parser._initiate_params_file_gen()
    if len(sys.argv) == 1:
        arg_parser.print_help()
        sys.exit()

    arguments = arg_parser.parse_args(sys.argv[1:])

    gen = FileGenerator(arguments.filename)
    gen.run(arguments.number)
