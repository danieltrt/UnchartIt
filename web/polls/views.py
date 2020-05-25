from django.http import HttpResponse
from .src.logger import *
from .src.program import *
from .src.checker import *
from .src.interpreter import *
from .src.solver import *
from .src.model import *
from .src.distinguisher import *
from json import load
from os import listdir
import sys

logger = get_logger("polls")
logger.setLevel("DEBUG")

def index(request):
    with open("./polls/example/instance1.json") as f:
        data = load(f)

    # UnchartIt specific
    logger.debug("Loading programs.")
    programs = []
    programs_paths = [data['programs'] + f for f in listdir(data['programs'])]
    for program_path in programs_paths:
        programs += [UnchartItProgram(program_path)]

    logger.debug("Loading CBMC template.")
    template = UnchartItTemplate(data["cbmc_template"], data['input_constraints'])
    interpreter = UnchartItInterpreter(data['input_constraints'])

    # Generic
    model_checker = CBMC(template)
    solver = Solver(data["solver"])
    interaction_model = YesNoInteractionModel(model_checker, solver, interpreter)

    dst = Distinguisher(interaction_model, programs)
    inpt, output = dst.distinguish()
    return HttpResponse("{}\n{}".format(inpt.display(), output.display()))
