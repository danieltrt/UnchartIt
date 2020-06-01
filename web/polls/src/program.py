import os


class CProgram:
    idx = 1

    def __init__(self, string, output_type, input_type):
        self.string = string
        self.output_type = output_type
        self.input_type = input_type
        self.idx = CProgram.idx
        CProgram.idx += 1

    def get_input_type(self):
        return self.input_type

    def call(self, var):
        first_line = self.string.split(os.linesep)[0]
        begin = len(self.output_type) + 1
        end = first_line.find("(")
        call_string = first_line[begin:end]
        call_string += "({});".format(var)
        return call_string

    def __lt__(self, other):
        return self.idx < other.idx

    def __str__(self):
        first_line = self.string.split(os.linesep)[0]
        begin = len(self.output_type) + 1
        end = first_line.find("(")
        return first_line[begin:end]


class UnchartItProgram(CProgram):

    def __init__(self, path=None, f=None):
        if path is not None:
            with open(path, "r+") as f:
                super().__init__(f.read(), "void", "dataframe")
        elif f is not None:
            super().__init__(f.read().decode(encoding='UTF-8'), "void", "dataframe")


