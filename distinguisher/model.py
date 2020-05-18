from distinguisher.checker import *
from distinguisher.solver import *
from distinguisher.interpreter import *


class InteractionModel:

    def generate_interaction(self, programs, input_constraints):
        pass

    def ask_user(self, inpt, results):
        pass


class OptionsInteractionModel(InteractionModel):

    def __init__(self, model_checker: ModelChecker, solver: Solver, interpreter: Interpreter):

        self.model_checker = model_checker
        self.solver = solver
        self.interpreter = interpreter

    def generate_interaction(self, programs, input_constraints):
        symbolic_representation = self.model_checker.generate_symbolic_representation(programs, input_constraints)
        variables = ["-{}".format(el) for el in symbolic_representation.eq_vars]
        symbolic_representation.add_hard_clause(variables)
        for var in variables:
            symbolic_representation.add_soft_clause(1, [var])
        model = self.solver.run(symbolic_representation)
        inpt = self.interpreter.extract_input(symbolic_representation, model, input_constraints)
        sets = self.get_sets(model, programs, symbolic_representation.eq_vars)
        representatives = {next(iter(el)): el for el in sets}
        results = {}
        for program in representatives:
            results[program] = self.interpreter.evaluate(program, inpt)
        return self.ask_user(inpt, results)

    def ask_user(self, inpt, results):
        print("Consider the following input", os.linesep, inpt, os.linesep)
        print("Select the corresponding output:")
        programs = sorted([program for program in results])
        count = 0
        for program in programs:
            print("Output number ({})".format(count), os.linesep, results[program], os.linesep)
            count += 1

        answer = int(input())
        return programs[answer]

    def get_sets(self, model, programs, eq_vars):
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
