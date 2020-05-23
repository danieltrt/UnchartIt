class Program:

    def __init__(self, path, idx):
        self.idx = idx

        with open(path, "r+") as f:
            self.string = f.read()

    def call(self, var):
        pass

    def equiv(self, other):
        pass

    def get_input_type(self):
        pass

    def get_input_vector(self, name, size):
        pass

    def __lt__(self, other):
        pass




