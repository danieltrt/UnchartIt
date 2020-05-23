class Program:
    idx = 0

    def __init__(self, path, return_value, input_type):
        self.idx = Program.idx
        self.return_value = return_value
        self.input_type = input_type

        with open(path, "r+") as f:
            self.string = f.read()

        Program.idx += 1

    def get_input_type(self):
        return self.input_type

    def call(self, var):
        pass

    def get_input_vector(self, name, size):
        pass

    def __lt__(self, other):
        return self.idx < other.idx



