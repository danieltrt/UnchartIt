from sys import byteorder
from .logger import get_logger

logger = get_logger("dist.interpreter")


class Table:

    text_strings = {-1: "NA", 0: "''", 1: "Google", 2: "Microsoft", 3: "Apple", 4: "Oracle",
                    5: "JP Morgan", 6: "Facebook", 7: "Deutsche Bank", 8: "General Motors", 9: "Logitech", 10: "Sony"}

    def __init__(self, table, active_rows, active_cols, order, col_names):
        self.table = table
        self.active_rows = active_rows
        self.active_cols = active_cols
        self.order = order
        self.n_rows = sum(active_rows)
        self.n_cols = sum(active_cols) + 1
        self.col_names = [col_names[i] for i in range(len(active_cols)) if active_cols[i]]

    def display(self):
        string = ""
        for i in range(len(self.active_rows)):
            if self.active_rows[self.order[i]] == 1:
                for j in range(len(self.active_cols)):
                    if self.active_cols[j] == 1:
                        string += " [" + str(self.table[self.order[i]][j]) + "]"
                string += "\n"
        return string[:-1]

    def get_active_cols(self):
        cols = []
        for j in range(len(self.active_cols)):
            col = []
            if self.active_cols[j] == 1:
                for i in range(len(self.active_rows)):
                    if self.active_rows[self.order[i]] == 1:
                        col += [self.table[self.order[i]][j]]
            if not col: continue
            if col[0] >= 100:
                col = list(map(lambda x: x / 100, col))
            cols += [col]

        try:
            cols[0] = list(map(lambda x: self.text_strings[x], cols[0]))
        except:
            logger.error("Could not map {} to strings.".format(cols[0]))
        return cols

    def get_active_rows(self):
        rows = list(map(list, zip(*self.get_active_cols())))
        return rows

    def get_header(self):
        return self.col_names

    def get_maximum(self):
        return max(self.get_active_cols()[-1])


class ModelInterpreter:

    def extract_input(self, symbolic_representation, model):
        raise NotImplementedError

    def extract_output(self, symbolic_representation, model, idx):
        raise NotImplementedError


class UnchartItInterpreter(ModelInterpreter):

    def __init__(self, input_constraints):
        self.rows = input_constraints[1]
        self.cols = input_constraints[2]
        self.n_bits = input_constraints[3]
        self.n_bits_table = input_constraints[4]
        self.col_names = input_constraints[5]

    def extract_input(self, symbolic_representation, model):
        table, active_rows, active_cols, order = self.extract_table(model, symbolic_representation.input_vars)
        return Table(table, active_rows, active_cols, order, self.col_names)

    def extract_output(self, symbolic_representation, model, idx):
        table, active_rows, active_cols, order = self.extract_table(model, symbolic_representation.output_vars[idx])
        return Table(table, active_rows, active_cols, order, self.col_names)

    def extract_table(self, model, vars):
        table = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        active_rows = [0 for _ in range(self.rows)]
        active_cols = [0 for _ in range(self.cols)]
        order = [0 for _ in range(self.rows)]
        groups = [0 for _ in range(self.rows)]
        first = 0

        for i in range(self.rows):
            for j in range(self.cols):
                bit_str, first = self.read_bits(model, vars, first, self.n_bits_table)
                table[i][j] = self.twos(bit_str, self.n_bits_table // 8)
        for i in range(self.rows):
            bit_str, first = self.read_bits(model, vars, first, self.n_bits)
            active_rows[i] = self.twos(bit_str, self.n_bits // 8)
        for i in range(self.cols):
            bit_str, first = self.read_bits(model, vars, first, self.n_bits)
            active_cols[i] = self.twos(bit_str, self.n_bits // 8)
        for i in range(self.rows):
            bit_str, first = self.read_bits(model, vars, first, self.n_bits)
            order[i] = self.twos(bit_str, self.n_bits // 8)
        for i in range(self.rows):
            bit_str, first = self.read_bits(model, vars, first, self.n_bits)
            groups[i] = self.twos(bit_str, self.n_bits // 8)
        return table, active_rows, active_cols, order

    @staticmethod
    def read_bits(model, vars, first, bits):
        bit_str = ""
        for k in range(0, bits):
            if vars[first] == "FALSE":
                bit_str = "0" + bit_str
            elif vars[first] == "TRUE":
                bit_str = "1" + bit_str
            elif model[vars[first]]:
                bit_str = "1" + bit_str
            else:
                bit_str = "0" + bit_str
            first += 1
        return bit_str, first

    @staticmethod
    def twos(val_str, bytes):
        val = int(val_str, 2)
        b = val.to_bytes(bytes, byteorder=byteorder, signed=False)
        return int.from_bytes(b, byteorder=byteorder, signed=True)
