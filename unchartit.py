from distinguisher.template import *
from distinguisher.distinguisher import *
from distinguisher.interpreter import *
from distinguisher.program import *
from argparse import *
from os import listdir
import json
import os
import sys


class UnchartItProgram(CProgram):

    def __init__(self, path):
        with open(path, "r+") as f:
            super().__init__(f.read(), "void", "dataframe")


class UnchartItTemplate(Template):

    template_n_programs = "N_PROGRAMS"
    template_init_inputs = "INPUT_CONSTRAINTS"
    template_programs = "PROGRAM_STRINGS"
    template_n_cols = "N_COLS"
    template_n_rows = "N_ROWS"

    def __init__(self, path, input_constraints):
        super().__init__(path)
        self.init_input = input_constraints[0]
        self.n_rows = input_constraints[1]
        self.n_cols = input_constraints[2]

    def generate_code(self, programs):
        n_programs = str(len(programs))
        programs_strings = ""

        for program in programs:
            programs_strings += program.string + os.linesep

        template = self.template.replace(self.template_n_programs, n_programs)
        template = template.replace(self.template_init_inputs, self.init_input)
        template = template.replace(self.template_n_rows, str(self.n_rows))
        template = template.replace(self.template_n_cols, str(self.n_cols))
        template = template.replace(self.template_programs, programs_strings)
        return template


class UnchartItInterpreter(ModelInterpreter):

    def __init__(self, input_constraints):
        self.rows = input_constraints[1]
        self.cols = input_constraints[2]
        self.n_bits = input_constraints[3]
        self.n_bits_table = input_constraints[4]

    def extract_input(self, symbolic_representation, model):
        table, active_rows, active_cols, order = self.extract_table(model, symbolic_representation.input_vars)
        return Table(table, active_rows, active_cols, order)

    def extract_output(self, symbolic_representation, model, idx):
        table, active_rows, active_cols, order = self.extract_table(model, symbolic_representation.output_vars[idx])
        return Table(table, active_rows, active_cols, order)

    def extract_table(self, model, vars):
        table = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        active_rows = [0 for _ in range(self.rows)]
        active_cols = [0 for _ in range(self.cols)]
        order = [0 for _ in range(self.rows)]
        groups = [0 for _ in range(self.rows)]
        first = 0

        for i in range(self.rows):
            for j in range(self.cols):
                bit_str, first = self.read_bits(model, vars, first, self.n_bits_table)
                table[i][j] = self.twos(bit_str, self.n_bits_table // 8)
        for i in range(self.rows):
            bit_str, first = self.read_bits(model, vars, first, self.n_bits)
            active_rows[i] = self.twos(bit_str, self.n_bits // 8)
        for i in range(self.cols):
            bit_str, first = self.read_bits(model, vars, first, self.n_bits)
            active_cols[i] = self.twos(bit_str, self.n_bits // 8)
        for i in range(self.rows):
            bit_str, first = self.read_bits(model, vars, first, self.n_bits)
            order[i] = self.twos(bit_str, self.n_bits // 8)
        for i in range(self.rows):
            bit_str, first = self.read_bits(model, vars, first, self.n_bits)
            groups[i] = self.twos(bit_str, self.n_bits // 8)
        return table, active_rows, active_cols, order

    @staticmethod
    def read_bits(model, vars, first, bits):
        bit_str = ""
        for k in range(0, bits):
            if vars[first] == "FALSE":
                bit_str = "0" + bit_str
            elif vars[first] == "TRUE":
                bit_str = "1" + bit_str
            elif model[vars[first]]:
                bit_str = "1" + bit_str
            else:
                bit_str = "0" + bit_str
            first += 1
        return bit_str, first

    @staticmethod
    def twos(val_str, bytes):
        val = int(val_str, 2)
        b = val.to_bytes(bytes, byteorder=sys.byteorder, signed=False)
        return int.from_bytes(b, byteorder=sys.byteorder, signed=True)


class Table:
    def __init__(self, table, active_rows, active_cols, order):
        self.table = table
        self.active_rows = active_rows
        self.active_cols = active_cols
        self.order = order
        self.n_rows = sum(active_rows)
        self.n_cols = sum(active_cols) + 1

    def display(self):
        string = ""
        for i in range(len(self.active_rows)):
            if self.active_rows[self.order[i]] == 1:
                for j in range(len(self.active_cols)):
                    if self.active_cols[j] == 1:
                        string += " [" + str(self.table[self.order[i]][j]) + "]"
                string += "\n"
        return string[:-1]


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", "--details", type=str)
    arg_parser.add_argument("-s", "--solver", type=str)
    cmd_args = arg_parser.parse_args()

    with open(cmd_args.details) as f:
        data = json.load(f)

    # UnchartIt specific
    programs = []
    programs_paths = [data['programs'] + f for f in listdir(data['programs'])]
    for program_path in programs_paths:
        programs += [UnchartItProgram(program_path)]
    template = UnchartItTemplate(data["cbmc_template"], data['input_constraints'])
    interpreter = UnchartItInterpreter(data['input_constraints'])

    # Generic
    model_checker = CBMC(template)
    solver = Solver(cmd_args.solver)
    interaction_model = OptionsInteractionModel(model_checker, solver, interpreter)

    dst = Distinguisher(interaction_model, programs)
    dst.distinguish()
