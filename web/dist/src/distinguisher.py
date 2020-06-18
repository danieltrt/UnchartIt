from .model import *
from .logger import get_logger
from .model import *
from .program import *
from typing import List

logger = get_logger("dist.distinguisher")


class Distinguisher:
    n = 0

    def __init__(self, interaction_model: InteractionModel, programs: List[CProgram]):
        self.interaction_model = interaction_model
        self.programs = programs
        self.prev_run = None
        self.done = False
        self.n = Distinguisher.n
        Distinguisher.n += 1

    def distinguish(self):
        if not self.done:
            logger.info("Now distinguishing {} programs: {}.".format(len(self.programs), [str(p) for p in self.programs]))
            inpt, output, answers = self.interaction_model.generate_interaction(self.programs)
            self.prev_run = answers
            return inpt, output
        else:
            return True, True

    def update_programs(self, answer):
        self.programs = self.prev_run[answer]
        if len(self.programs) == 1:
            self.done = True

    def get_answer(self, answer):
        progs = self.prev_run.get(answer, None)
        if progs is None: progs = self.prev_run[None]
        return progs[0].string
