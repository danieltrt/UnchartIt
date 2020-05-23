from distinguisher.checker import *
from distinguisher.solver import *


class InteractionModel:

    def generate_interaction(self, programs):
        pass

    def ask_user(self, inpt, results):
        pass


class OptionsInteractionModel(InteractionModel):

    def __init__(self, model_checker, solver, interpreter):
        self.model_checker = model_checker
        self.solver = solver
        self.interpreter = interpreter

    def generate_interaction(self, programs):
        symbolic_representation = self.model_checker.generate_symbolic_representation(programs)
        variables = ["-{}".format(el) for el in symbolic_representation.eq_vars]
        symbolic_representation.add_hard_clause(variables)
        for var in variables:
            symbolic_representation.add_soft_clause(1, [var])
        model = self.solver.run(symbolic_representation)
        if model is None:
            return programs
        inpt = self.interpreter.extract_input(symbolic_representation, model)
        sets = self.get_sets(model, symbolic_representation.eq_vars, programs)
        representatives = {next(iter(el)): el for el in sets}
        results = {}
        for program in representatives:
            idx = programs.index(program)
            results[program] = self.interpreter.extract_output(symbolic_representation, model, idx)

        return list(representatives[self.ask_user(inpt, results)])

    def ask_user(self, inpt, results):
        print("Consider the following input:")
        print(inpt.display(), os.linesep)
        print("Select the corresponding output:")
        programs = [program for program in results]
        count = 0
        for program in programs:
            print("Output ({})".format(count))
            print(results[program].display(), os.linesep)
            count += 1

        answer = int(input())
        return programs[answer]

    def get_sets(self, model, eq_vars, programs):
        sets = [{programs[i]} for i in range(len(programs))]
        variables = sorted(eq_vars, key=int)
        count = 0
        for i in range(len(programs)):
            for j in range(i + 1, len(programs)):
                if model[variables[count]]:
                    set1 = list(filter(lambda x: programs[i] in x, sets))[0]
                    set2 = list(filter(lambda x: programs[j] in x, sets))[0]
                    if set1 != set2:
                        sets.remove(set1)
                        sets.remove(set2)
                        sets += [set1 | set2]
                count += 1
        return sets


class YesNoInteractionModel(InteractionModel):

    def __init__(self, model_checker, solver, interpreter):

        self.model_checker = model_checker
        self.solver = solver
        self.interpreter = interpreter

    def generate_interaction(self, programs):
        symbolic_representation = self.model_checker.generate_symbolic_representation(programs)
        b = self.create_bij_constraints(len(programs), symbolic_representation)
        pA, pB = self.create_group_constraints(len(programs), symbolic_representation, b)
        sumA, sumB = self.create_counters(len(programs), symbolic_representation, pA, pB)
        self.create_at_most_constraint(programs, sumB, symbolic_representation)
        self.create_minimization_constraint(len(programs), symbolic_representation, sumA, sumB)
        model = self.solver.run(symbolic_representation)
        programs_in_a = list(map(lambda x: programs[x], list(filter(lambda x: model[pA[x]], [i for i in range(len(programs))]))))
        programs_in_b = list(map(lambda x: programs[x], list(filter(lambda x: model[pB[x]], [i for i in range(len(programs))]))))
        idx = programs.index(programs_in_a[0])
        if len(programs_in_a) == len(programs):
            print("Programs are equal")
            return None

        inpt = self.interpreter.extract_input(symbolic_representation, model)
        output = self.interpreter.extract_output(symbolic_representation, model, idx)

        if self.ask_user(inpt, output) == "y":
            return programs_in_a
        return programs_in_b

    def ask_user(self, inpt, results):
        print("Consider the following input:")
        print(inpt.display(), os.linesep)
        print("Is the following output correct (y/n):")
        print(results.display(), os.linesep)
        return input()

    def create_bij_constraints(self, n_progs, symbolic_representation):
        count = 0
        b = [[0 for _ in range(n_progs)] for _ in range(n_progs)]
        for i in range(n_progs):
            for j in range(i + 1, n_progs):
                b[i][j] = b[j][i] = symbolic_representation.add_variable()
                symbolic_representation.add_hard_clause([symbolic_representation.neq_vars[count], b[i][j]])
                symbolic_representation.add_hard_clause([symbolic_representation.eq_vars[count], '-' + b[i][j]])
                symbolic_representation.add_hard_clause([symbolic_representation.eq_vars[count], symbolic_representation.neq_vars[count]])
                symbolic_representation.add_hard_clause(['-' + symbolic_representation.eq_vars[count], '-' + symbolic_representation.neq_vars[count]])
                count += 1
        return b

    def create_group_constraints(self, n_progs, symbolic_representation, b):
        pA = [0 for _ in range(n_progs)]
        pB = [0 for _ in range(n_progs)]

        for i in range(n_progs):
            pA[i] = symbolic_representation.add_variable()
            pB[i] = symbolic_representation.add_variable()

        for i in range(n_progs):
            for j in range(n_progs):
                if i != j:
                    symbolic_representation.add_hard_clause(['-' + b[i][j], pA[i], pB[i]])
                    symbolic_representation.add_hard_clause(['-' + b[i][j], pA[i], pB[j]])
                    symbolic_representation.add_hard_clause(['-' + b[i][j], pA[j], pB[i]])
                    symbolic_representation.add_hard_clause(['-' + b[i][j], pA[j], pB[j]])
                    symbolic_representation.add_hard_clause([b[i][j], '-' + pA[i], '-' + pA[j]])

            # programs must be in A or B
            symbolic_representation.add_hard_clause([pA[i], pB[i]])
            symbolic_representation.add_hard_clause(['-' + pA[i], '-' + pB[i]])
        return pA, pB

    def create_counters(self, n_progs, symbolic_representation, pA, pB):
        sumA = symbolic_representation.create_totalizer(0, n_progs - 1, pA)[1:]  # counts the number of elements on pA
        sumB = symbolic_representation.create_totalizer(0, n_progs - 1, pB)[1:]  # counts the number of elements on pB
        return sumA, sumB

    def create_at_most_constraint(self, programs, sumB, symbolic_representation):
        symbolic_representation.add_hard_clause(['-' + sumB[len(programs) - 1]])

    def create_minimization_constraint(self, n_progs, symbolic_representation, sumA, sumB):
        for i in range(n_progs):
            symbolic_representation.add_soft_clause(1, ['-' + sumA[i], sumB[i]])
            symbolic_representation.add_soft_clause(1, [sumA[i], '-' + sumB[i]])

