from distinguisher.distinguisher import *
from distinguisher.checker import *
from distinguisher.model import *
from distinguisher.program import *
from distinguisher.solver import *
from os import linesep
from sys import byteorder

logger = get_logger("distinguisher")
logger.setLevel("DEBUG")

class ToyTemplate(Template):
    template_init_inputs = "INPUT_CONSTRAINTS"
    template_programs = "PROGRAM_STRINGS"

    def __init__(self, template, input_constraints):
        super().__init__(template)
        self.input_constraints = input_constraints

    def generate_code(self, programs):
        programs_strings = ""

        for program in programs:
            programs_strings += program.string + linesep

        template = self.template.replace(self.template_init_inputs, self.input_constraints)
        template = template.replace(self.template_programs, programs_strings)
        return template


class ToyInterpreter(ModelInterpreter):

    def __init__(self):
        pass

    def extract_input(self, symbolic_representation, model):
        first = 0
        vals = [0, 0]
        for i in range(2):
            bit_str, first = self.read_bits(model, symbolic_representation.input_vars, first, 32)
            vals[i] = self.twos(bit_str, 4)
        return Pair(vals[0], vals[1])

    def extract_output(self, symbolic_representation, model, idx):
        first = 0
        vals = [0, 0]
        for i in range(2):
            bit_str, first = self.read_bits(model, symbolic_representation.output_vars[idx], first, 32)
            vals[i] = self.twos(bit_str, 4)
        return Pair(vals[0], vals[1])

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
        b = val.to_bytes(bytes, byteorder=byteorder, signed=False)
        return int.from_bytes(b, byteorder=byteorder, signed=True)


class Pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def display(self):
        return "({}, {})".format(self.x, self.y)


if __name__ == "__main__":
    programs = []
    programs += [CProgram("void prog1(pair* p) { p->x = sum(p->x, p->y); }", "void", "pair")]
    programs += [CProgram("void prog2(pair* p) { p->x = mul(p->x, p->x); }", "void", "pair")]
    programs += [CProgram("void prog3(pair* p) { p->y = sub(p->x, p->y); }", "void", "pair")]
    programs += [CProgram("void prog4(pair* p) { p->y = div(p->x, p->y); }", "void", "pair")]
    programs += [CProgram("void prog5(pair* p) { p->y = mul(p->x, p->y); p->y = mul(p->x, p->y); }", "void", "pair")]

    inpt_constraints = " " * 4 + "__CPROVER_assume(p->x < 10 && p->y < 10 );" + os.linesep
    inpt_constraints += " " * 4 + "__CPROVER_assume(p->x > 0 && p->y > 0 );"
    template = ToyTemplate("./example/cbmc_toy.c", inpt_constraints)

    interpreter = ToyInterpreter()

    model_checker = CBMC(template)
    solver = Solver("Open-LinSBPS")
    interaction_model = OptionsInteractionModel(model_checker, solver, interpreter)

    dst = Distinguisher(interaction_model, programs)
    dst.distinguish()
