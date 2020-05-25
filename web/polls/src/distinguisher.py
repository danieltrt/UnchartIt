from .model import *
from .logger import get_logger

logger = get_logger("polls.distinguisher")


class Distinguisher:

    def __init__(self, interaction_model, programs):
        self.interaction_model = interaction_model
        self.programs = programs

    def distinguish(self):
        while True:
            logger.info("Now distinguishing {} programs: {}.".format(len(self.programs), [str(p) for p in self.programs]))
            inpt, output = self.interaction_model.generate_interaction(self.programs)
            return inpt, output
