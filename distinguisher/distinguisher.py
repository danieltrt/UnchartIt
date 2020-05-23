from distinguisher.model import *
from distinguisher.program import *
from typing import List


class Distinguisher:

    def __init__(self, interaction_model: InteractionModel, programs: List[CProgram]):
        self.interaction_model = interaction_model
        self.programs = programs

    def distinguish(self):
        while True:
            programs = self.interaction_model.generate_interaction(self.programs)
            if programs == self.programs or len(programs) == 1:
                return programs
            self.programs = programs





