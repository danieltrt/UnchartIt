import os

class Program:

    def __init__(self, path):

        with open(path, "r+") as f:
            self.string = f.read()

    def call(self):
        pass

    def equiv(self, other):
        pass

    def __lt__(self, other):
        pass

class UnchartItProgram(Program):
    name = "program"
    end = "("
    return_value = "int8"
    equiv_fn = "equiv"

    def get_number(self):
        first_line = self.string.split(os.linesep)[0]
        begin = first_line.find(self.name) + len(self.name)
        end = first_line.find(self.end)-len(self.end) + 1
        return int(first_line[begin:end])

    def call(self):
        first_line = self.string.split(os.linesep)[0]
        begin = first_line.find(self.name)
        end = first_line.find(self.end)
        call_string = first_line[begin:end]
        call_string += "(&p[{}]);".format(self.get_number() - 1)

        return call_string

    def equiv(self, other):
        var_name = "a{}{}".format(self.get_number(), other.get_number())
        assignment = "{} {} = {}(&p[{}], &p[{}]);".format(self.return_value, var_name, self.equiv_fn,
                                                         self.get_number() - 1, other.get_number() - 1)

        return var_name, assignment

    def __lt__(self, other):
        return self.get_number() < other.get_number()

