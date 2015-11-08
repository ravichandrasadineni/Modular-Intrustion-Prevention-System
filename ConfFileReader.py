__author__ = 'raghuar'

import re

class ConfFileReader:
    def __init__(self, filename):
        self.filename = filename
        self.patterns = {}

    def get_patterns_from_file(self):
        fd = open(self.filename,'r')
        for line in fd:
            if line[0] != '#':
                line_split = re.split(',', line.strip())
                self.patterns[line_split[0]] = [line_split[1], line_split[2]]
        fd.close()

    def get_patterns(self):
        return self.patterns

    def print_patterns(self):
        for f in self.patterns.keys():
            print "[", f, ":", self.patterns[f], "]"

    def run(self):
        print "[confFileReader] Starting"
        self.get_patterns_from_file()

# if __name__ == "__main__":
#     cfile = ConfFileReader('config/Applications.conf')
#     cfile.get_patterns()
#     cfile.print_patterns()