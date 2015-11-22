__author__ = 'raghuar'

import re

class ConfFileReader:
    def __init__(self, filename, cred_file, apache_conf):
        self.filename = filename
        self.cred_file = cred_file
        self.apache_conf = apache_conf
        self.patterns = []
        self.apache_patterns = []
        self.cred = {}

    def get_patterns_from_apache_conf_file(self):
        fd = open(self.apache_conf,'r')
        for line in fd:
            if line[0] != '#':
                line_split = re.split(',', line.strip())
                self.apache_patterns.append([line_split[0], line_split[1], line_split[2], line_split[3]])
        fd.close()


    def get_patterns_from_file(self):
        fd = open(self.filename,'r')
        for line in fd:
            if line[0] != '#':
                line_split = re.split(',', line.strip())
                self.patterns.append([line_split[0], line_split[1], line_split[2]])
        fd.close()

    def get_new_patterns_from_file(self):
        fd = open(self.filename,'r')
        for line in fd:
            if line[0] != '#':
                line_split = re.split(',', line.strip())
                self.patterns.append([line_split[0], line_split[1], line_split[2], line_split[3]])
        fd.close()
        fd2 = open(self.cred_file,'r')
        for line in fd2:
            if line[0] != '#':
                line_split = re.split(',', line.strip())
                self.cred[line_split[0]] = [line_split[1], line_split[2]]
        fd2.close()

    def get_apache_patterns(self):
        return self.apache_patterns

    def get_patterns(self):
        return self.patterns

    def get_credentials(self):
        return self.cred

    def print_patterns(self):
        for f in self.patterns:
            print f

    def run(self):
        print "[confFileReader] Starting"
        # self.get_patterns_from_file()
        # self.get_new_patterns_from_file()
        self.get_patterns_from_apache_conf_file()

# if __name__ == "__main__":
#     cfile = ConfFileReader('config/Applications.conf')
#     cfile.run()
#     cfile.print_patterns()
