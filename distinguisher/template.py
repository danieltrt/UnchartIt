import os

class Template:

    def __init__(self, path_to_template):
        with open(path_to_template, "r") as f:
            self.template = f.read()

    def genarate_c(self, programs, input_constraints):
        pass


class CBMCTemplate(Template):

    template_n_programs = "N_PROGRAMS"
    template_program_calls = "PROGRAM_CALLS"
    template_init_inputs = "INPUT_CONSTRAINTS"
    template_programs = "PROGRAM_STRINGS"
    template_equality = "EQUALITY_PROGRAMS"
    template_n_cols = "N_COLS"
    template_n_rows = "N_ROWS"

    def generate_c(self, programs, input_constraints):
        n_programs = str(len(programs))
        program_calls = ""
        equality = ""
        programs_strings = ""

        for program in programs:
            programs_strings += program.string + os.linesep

        for i in range(len(programs)):
            programs[i].current_idx = i  # hack
            program_calls += str(programs[i].call()) + os.linesep

        equiv_vars = []
        for i in range(len(programs)):
            for j in range(i + 1, len(programs)):
                var_name, assignment = programs[i].equiv(programs[j])
                equality += assignment + os.linesep
                equiv_vars += [var_name]

        template = self.template.replace(self.template_n_programs, n_programs)
        template = template.replace(self.template_init_inputs, input_constraints[0])
        template = template.replace(self.template_n_rows, str(input_constraints[1]))
        template = template.replace(self.template_n_cols, str(input_constraints[2]))
        template = template.replace(self.template_program_calls, program_calls)
        template = template.replace(self.template_equality, equality)
        template = template.replace(self.template_programs, programs_strings)
        return template, equiv_vars


class InterpreterTemplate(Template):

    template_n_cols = "N_COLS"
    template_n_rows = "N_ROWS"
    template_n_programs = "N_PROGRAMS"
    template_program_calls = "PROGRAM_CALLS"
    template_programs = "PROGRAM_STRINGS"
    template_actual_table = "ACTUAL_TABLE"
    template_program_output = "PROGRAM_OUTPUTS"
    template_print = "pretty_print"

    def genarate_c(self, program, inpt):
        #header
        template = self.template.replace(self.template_n_programs, "1")
        template = template.replace(self.template_n_rows, str(inpt.n_rows))
        template = template.replace(self.template_n_cols, str(inpt.n_cols))

        #inputs
        template = template.replace(self.template_actual_table, inpt.generate_c())

        #call
        template = template.replace(self.template_programs, program.string)
        program_call = "{}{}(&input);".format(program.name, program.get_number())
        template = template.replace(self.template_program_calls, program_call)
        program_output = "{}(&input);".format(self.template_print)
        template = template.replace(self.template_program_output, program_output)

        return template


