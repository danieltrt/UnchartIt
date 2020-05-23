from distinguisher.template import *
from distinguisher.distinguisher import *
from distinguisher.interpreter import *
from distinguisher.program import *
from argparse import *
from os import listdir
import json
import os
import sys
import subprocess


class UnchartItProgram(Program):

    def __init__(self, path):
        super().__init__(path, "void", "dataframe")

    def call(self, var):
        first_line = self.string.split(os.linesep)[0]
        begin = len(self.return_value) + 1
        end = first_line.find("(")
        call_string = first_line[begin:end]
        call_string += "({});".format(var)
        return call_string

    def get_input_vector(self, name, size):
        return self.get_input_type() + " {}[{}];".format(name, size)


class CBMCTemplate(Template):

    template_n_programs = "N_PROGRAMS"
    template_init_inputs = "INPUT_CONSTRAINTS"
    template_programs = "PROGRAM_STRINGS"
    template_n_cols = "N_COLS"
    template_n_rows = "N_ROWS"

    def generate_code(self, programs, input_constraints):
        n_programs = str(len(programs))
        programs_strings = ""

        for program in programs:
            programs_strings += program.string + os.linesep

        template = self.template.replace(self.template_n_programs, n_programs)
        template = template.replace(self.template_init_inputs, input_constraints[0])
        template = template.replace(self.template_n_rows, str(input_constraints[1]))
        template = template.replace(self.template_n_cols, str(input_constraints[2]))
        template = template.replace(self.template_programs, programs_strings)
        return template


class InterpreterTemplate(Template):

    template_n_cols = "N_COLS"
    template_n_rows = "N_ROWS"
    template_n_programs = "N_PROGRAMS"
    template_program_calls = "PROGRAM_CALLS"
    template_programs = "PROGRAM_STRINGS"
    template_actual_table = "ACTUAL_TABLE"
    template_program_output = "PROGRAM_OUTPUTS"
    template_print = "pretty_print"
    input_var = "input"

    def genarate_code(self, program, inpt):
        #header
        template = self.template.replace(self.template_n_programs, "1")
        template = template.replace(self.template_n_rows, str(inpt.n_rows))
        template = template.replace(self.template_n_cols, str(inpt.n_cols))

        #inputs
        template = template.replace(self.template_actual_table, inpt.generate_code())

        #call
        template = template.replace(self.template_programs, program.string)
        program_call = program.call("&{}".format(self.input_var))
        template = template.replace(self.template_program_calls, program_call)
        program_output = "{}(&{});".format(self.template_print, self.input_var)
        template = template.replace(self.template_program_output, program_output)

        return template


class UnchartItInterpreter(Interpreter):

    def evaluate(self, program, inpt):
        code = self.template.genarate_code(program, inpt)
        file_n = int(time.time() * 100)
        with open("/tmp/uncharit_interpreter_{}.c".format(file_n), "a+") as f:
            f.write(code)

        cmd = "gcc /tmp/uncharit_interpreter_{}.c -o /tmp/uncharit_interpreter_{}".format(file_n, file_n)
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        subprocess.call(["rm", "/tmp/uncharit_interpreter_{}.c".format(file_n)])

        p = subprocess.Popen('/tmp/uncharit_interpreter_{}'.format(file_n), shell=True, stdout=subprocess.PIPE)
        output = p.communicate()[0].decode()
        subprocess.call(["rm", "/tmp/uncharit_interpreter_{}".format(file_n)])

        return self.extract_output(output)

    def extract_input(self, symbolic_representation, model, input_constraints):
        rows = input_constraints[1]
        cols = input_constraints[2]
        n_bits = input_constraints[3]
        n_bits_table = input_constraints[4]

        table = [[0 for _ in range(cols)] for _ in range(rows)]
        active_rows = [0 for _ in range(rows)]
        active_cols = [0 for _ in range(cols)]
        order = [0 for _ in range(rows)]
        groups = [0 for _ in range(rows)]
        first = symbolic_representation.input_vars[0]

        for i in range(rows):
            for j in range(cols):
                bit_str, first = self.read_bits(model, first, n_bits_table)
                table[i][j] = self.twos(bit_str, n_bits_table // 8)
        for i in range(rows):
            bit_str, first = self.read_bits(model, first, n_bits)
            active_rows[i] = self.twos(bit_str, n_bits // 8)
        for i in range(cols):
            bit_str, first = self.read_bits(model, first, n_bits)
            active_cols[i] = self.twos(bit_str, n_bits // 8)
        for i in range(rows):
            bit_str, first = self.read_bits(model, first, n_bits)
            order[i] = self.twos(bit_str, n_bits // 8)
        for i in range(rows):
            bit_str, first = self.read_bits(model, first, n_bits)
            groups[i] = self.twos(bit_str, n_bits // 8)
        return Table(table, active_rows, [1 for _ in range(len(active_cols) - 1)] + [0])

    def extract_output(self, output):
        output = output.splitlines()
        active_cols = [1 for _ in range(len(output[0].split(" ")[:-1]))]
        table = []
        active_rows = []
        for line in output[1:]:
            line = line.split(" ")[:-1]
            line = list(map(lambda x: int(x), line))
            table += [line]
            active_rows += [1]
        return Table(table, active_rows, active_cols)

    def read_bits(self, model, first, bits):
        bit_str = ""
        for k in range(0, bits):
            if model[first]:
                bit_str = "1" + bit_str
            else:
                bit_str = "0" + bit_str
            first = str(int(first) + 1)
        return bit_str, first

    def twos(self, val_str, bytes):
        val = int(val_str, 2)
        b = val.to_bytes(bytes, byteorder=sys.byteorder, signed=False)
        return int.from_bytes(b, byteorder=sys.byteorder, signed=True)


class Table:
    def __init__(self, table, active_rows, active_cols):
        self.table = table
        self.active_rows = active_rows
        self.active_cols = active_cols
        self.n_rows = sum(active_rows)
        self.n_cols = sum(active_cols) + 1

    def display(self):
        string = ""
        for i in range(len(self.active_rows)):
            if self.active_rows[i] == 1:
                for j in range(len(self.active_cols)):
                    if self.active_cols[j] == 1:
                        string += " [" + str(self.table[i][j]) + "]"
                string += "\n"
        return string[:-1]

    def generate_code(self):
        tab = ""
        active = ""
        for i in range(len(self.active_rows)):
            if self.active_rows[i] == 1:
                active += "df->active_rows[{}] = 1;\n".format(i)
                for j in range(len(self.active_cols)):
                    if self.active_cols[j] == 1:
                        tab += "df->table[{}][{}]".format(i,j) + " = " + str(self.table[i][j]) + ";\n"
                tab += "\n"
        return tab + active


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-d", "--details", type=str)
    arg_parser.add_argument("-s", "--solver", type=str)
    cmd_args = arg_parser.parse_args()

    with open(cmd_args.details) as f:
        data = json.load(f)

    programs = []
    programs_paths = [data['programs'] + f for f in listdir(data['programs'])]
    for program_path in programs_paths:
        programs += [UnchartItProgram(program_path)]
    cbmc_template = CBMCTemplate(data["cbmc_template"])
    interpreter_template = InterpreterTemplate(data["interpreter_template"])

    model_checker = CBMC(cbmc_template)
    solver = Solver(cmd_args.solver)
    interpreter = UnchartItInterpreter(interpreter_template)
    interaction_model = OptionsInteractionModel(model_checker, solver, interpreter)

    dst = Distinguisher(interaction_model, programs, data['input_constraints'])
    dst.distinguish()
