from distinguisher.model import *
from distinguisher.program import *
from typing import List
from distinguisher.logger import get_logger

logger = get_logger("distinguisher.distinguisher")


class Distinguisher:

    def __init__(self, interaction_model, programs):
        self.interaction_model = interaction_model
        self.programs = programs

    def distinguish(self):
        while True:
            logger.info("Now distinguishing {} programs".format(len(self.programs)))
            programs = self.interaction_model.generate_interaction(self.programs)
            if programs == self.programs or len(programs) == 1:
                return programs
            self.programs = programs





