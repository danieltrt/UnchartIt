from .model import *
from .logger import get_logger

logger = get_logger("polls.distinguisher")


class Distinguisher:

    def __init__(self, interaction_model, programs):
        self.interaction_model = interaction_model
        self.programs = programs

    def distinguish(self, programs=None):
        if programs is None: programs = self.programs
        logger.info("Now distinguishing {} programs: {}.".format(len(programs), [str(p) for p in programs]))
        inpt, output, programs = self.interaction_model.generate_interaction(programs)
        return inpt, output, programs
