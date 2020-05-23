class Template:

    def __init__(self, path_to_impl):
        with open(path_to_impl, "r") as f:
            self.template = f.read()

    def genarate_code(self, programs, input_constraints):
        pass
