

class Distinguisher:

    def __init__(self, interaction_model, programs, input_constraints):
        self.interaction_model = interaction_model
        self.programs = programs
        self.input_constraints = input_constraints

    def distinguish(self):
        while True:
            self.interaction_model.generate_interaction(self.programs, self.input_constraints)





