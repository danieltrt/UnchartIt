from distinguisher.logger import get_logger
import os
import time
import subprocess


logger = get_logger("distinguisher.checker")

class ModelChecker:

    def generate_symbolic_representation(self, programs):
        raise NotImplementedError


class ModelInterpreter:

    def extract_input(self, symbolic_representation, model):
        raise NotImplementedError

    def extract_output(self, symbolic_representation, model, idx):
        raise NotImplementedError


class Template:

    def __init__(self, path_to_impl):
        f = open(path_to_impl, "r")
        self.template = f.read()
        f.close()

    def genarate_code(self, programs, input_constraints):
        pass


class CBMC(ModelChecker):

    header = """extern void init_input(void* input);
    extern void copy_input(void* from, void* to);
    extern int equiv(const void* o1, const void* o2);
    int is_equiv(int eq) { return eq; }
    int not_equiv(int eq) { return !eq; }
    """
    positive_assertion = "assert(is_equiv({}));"
    negative_assertion = "assert(not_equiv({}));"
    cbmc_positive_assertion = "return_value_is_equiv"
    cbmc_negative_assertion = "return_value_not_equiv"
    cbmc_input_name = "c main::1::input!0@1#"
    cbmc_output_name = "c main::1::output!0@1#"
    n_soft_clauses = 1024

    def __init__(self, template):
        self.template = template

    def generate_symbolic_representation(self, programs):
        c_program = self.template.generate_code(programs)
        main = self.generate_main(programs)

        file_n = round(time.time() * 100)
        with open("/tmp/cbmc_main_{}.c".format(file_n), "a+") as f:
            f.write(self.header.replace("    ", "") + os.linesep)
            f.write(c_program + os.linesep)
            f.write(main + os.linesep)

        logger.info("Now running CBMC...")
        cmd = "cbmc /tmp/cbmc_main_{}.c --dimacs --object-bits 10".format(file_n)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        lns = str(out, encoding='utf-8')
        logger.info("CBMC returned.")


        n_vars, n_clauses, inc_dimacs = self.get_dimacs(lns.splitlines())
        eq_vars = self.get_eq_vars(lns.splitlines())
        neq_vars = self.get_neq_vars(lns.splitlines())
        input_vars = self.get_input_vars(lns.splitlines())
        output_vars = self.get_output_vars(lns.splitlines(), len(programs))

        return SymbolicRepresentation(n_vars, n_clauses, self.n_soft_clauses, inc_dimacs, eq_vars, neq_vars, input_vars, output_vars)

    def generate_main(self, programs):
        main = "int main(int argc, char *argv[]) {" + os.linesep

        main += " " * 4 + programs[0].get_input_type() + " input;" + os.linesep
        main += " " * 4 + "init_input(&input);" + os.linesep
        main += " " * 4 + programs[0].get_input_type() + " {}[{}];".format("output", len(programs)) + os.linesep

        main += " " * 4 + "for (int i = 0; i < {}; i++)".format(len(programs)) + " {" + os.linesep
        main += " " * 8 + "copy_input(&input, output + i);" + os.linesep
        main += " " * 4 + "}" + os.linesep

        for i in range(len(programs)):
            main += " " * 4 + str(programs[i].call("&output[{}]".format(i))) + os.linesep

        equiv_vars = []
        for i in range(len(programs)):
            for j in range(i + 1, len(programs)):
                var_name = "a{}{}".format(programs[i].idx, programs[j].idx)
                assignment = "int {} = equiv(&output[{}], &output[{}]);".format(var_name, i, j)
                main += " " * 4 + assignment + os.linesep
                equiv_vars += [var_name]

        for i in range(len(equiv_vars)):
            main += " " * 4 + self.positive_assertion.format(equiv_vars[i]) + os.linesep
        for i in range(len(equiv_vars)):
            main += " " * 4 + self.negative_assertion.format(equiv_vars[i]) + os.linesep

        return main + "}"

    def get_dimacs(self, lines):
        while lines[0].find("p cnf ") == -1:
            lines = lines[1:]
        header = lines[0][len("p cnf "):].split(" ")
        inc_dimacs = list(filter(lambda line: not line.startswith("c "), lines[1:]))
        inc_dimacs = ["{} {}".format(self.n_soft_clauses + 1, el) for el in inc_dimacs]
        inc_dimacs = "{}".format(os.linesep).join(inc_dimacs)
        return int(header[0]), int(header[1]), inc_dimacs

    def get_eq_vars(self, lines):
        eq_vars = []
        for line in lines:
            if line.find(self.cbmc_positive_assertion) != -1:
                line = line[line.find(self.cbmc_positive_assertion):].split(" ")
                if line[2] == "FALSE" or line[2] == "TRUE":
                    eq_vars += [line[1]]
        return sorted(eq_vars, key=int)

    def get_neq_vars(self, lines):
        neq_vars = []
        for line in lines:
            if line.find(self.cbmc_negative_assertion) != -1:
                line = line[line.find(self.cbmc_negative_assertion):].split(" ")
                if line[2] == "FALSE" or line[2] == "TRUE":
                    neq_vars += [line[1]]
        return sorted(neq_vars, key=int)

    def get_input_vars(self, lines):
        inpt_vars = {}
        for line in lines:
            if line.find(self.cbmc_input_name) != -1:
                line = line[len(self.cbmc_input_name):].split(" ")
                inpt_vars[int(line[0])] = line[1:]

        inputs = inpt_vars[max(inpt_vars.keys())]
        return inputs

    def get_output_vars(self, lines, n_outputs):
        output_vars = {}
        for line in lines:
            if line.find(self.cbmc_output_name) != -1:
                line = line[len(self.cbmc_output_name):].split(" ")
                output_vars[int(line[0])] = line[1:]

        output_vars = output_vars[max(output_vars.keys())]
        vars_per_output = int(len(output_vars) / n_outputs)
        outputs = [[] for _ in range(n_outputs)]
        for i in range(n_outputs):
            for j in range(vars_per_output):
                outputs[i] += [output_vars[i*vars_per_output + j]]

        return outputs


class SymbolicRepresentation:

    def __init__(self, n_vars, n_clauses, n_soft_clauses, inc_dimacs, eq_vars, neq_vars, input_vars, output_vars):
        self.n_vars = n_vars
        self.n_clauses = n_clauses
        self.n_soft_clauses = n_soft_clauses
        self.inc_dimacs = inc_dimacs + os.linesep
        self.eq_vars = eq_vars
        self.neq_vars = neq_vars
        self.input_vars = input_vars
        self.output_vars = output_vars

    def add_variable(self):
        self.n_vars += 1
        return str(self.n_vars)

    def add_hard_clause(self, variables):
        clause = "{} ".format(self.n_soft_clauses + 1)
        for var in variables:
            clause += "{} ".format(var)
        clause += "0{}".format(os.linesep)

        self.n_clauses += 1
        self.inc_dimacs += clause

    def add_soft_clause(self, weight, variables):
        clause = "{} ".format(weight)
        for var in variables:
            clause += "{} ".format(var)
        clause += "0{}".format(os.linesep)

        self.n_clauses += 1
        self.inc_dimacs += clause

    def get_dimacs(self):
        header = "p wcnf {} {} {}".format(self.n_vars, self.n_clauses, self.n_soft_clauses + 1) + os.linesep
        return header + self.inc_dimacs

    def create_totalizer(self, l, u, p):
        ret = [self.add_variable()]
        ending = [self.add_variable()]
        self.add_hard_clause([ret[0]])
        self.add_hard_clause(['-' + ending[0]])
        if l >= u:
            return ret + [p[l]] + ending

        left_vars = self.create_totalizer(l, l + (u-l)//2, p)  #[q]
        right_vars = self.create_totalizer(l + (u-l)//2 + 1, u, p) #[r]

        for i in range(l, u+1):
            ret += [self.add_variable()]

        ret += ending

        for i in range(len(left_vars)-1):
            for j in range(len(right_vars)-1):
                self.add_hard_clause(['-' + left_vars[i], '-' + right_vars[j], ret[i+j]]) #[p]
                self.add_hard_clause([left_vars[i+1], right_vars[j+1], '-' + ret[i+j+1]]) #[p]

        return ret
