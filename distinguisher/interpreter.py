import sys

class Interpreter:

    def evaluate(self, program, inpt):
        pass

    def extract_input(self, symbolic_representation, model, input_constraints):
        pass


class UnchartItInterpreter(Interpreter):

    def __init__(self, template):
        self.template = template

    def evaluate(self, program, inpt):
        pass

    def extract_input(self, symbolic_representation, model, input_constraints):
        rows = input_constraints[1]
        cols = input_constraints[2]
        n_bits = input_constraints[3]
        n_bits_table = input_constraints[4]

        table = [[0 for _ in range(cols)] for _ in range(rows)]
        active_rows = [0 for _ in range(rows)]
        active_cols = [0 for _ in range(cols)]
        order = [0 for _ in range(rows)]
        groups = [0 for _ in range(rows)]
        first = symbolic_representation.input_vars[0]

        for i in range(rows):
            for j in range(cols):
                bit_str, first = self.read_bits(model, first, n_bits_table)
                table[i][j] = self.twos(bit_str, n_bits_table // 8)
        for i in range(rows):
            bit_str, first = self.read_bits(model, first, n_bits)
            active_rows[i] = self.twos(bit_str, n_bits // 8)
        for i in range(cols):
            bit_str, first = self.read_bits(model, first, n_bits)
            active_cols[i] = self.twos(bit_str, n_bits // 8)
        for i in range(rows):
            bit_str, first = self.read_bits(model, first, n_bits)
            order[i] = self.twos(bit_str, n_bits // 8)
        for i in range(rows):
            bit_str, first = self.read_bits(model, first, n_bits)
            groups[i] = self.twos(bit_str, n_bits // 8)
        return Table(table, active_rows, [1 for _ in range(len(active_cols) - 1)] + [0])

    def read_bits(self, model, first, bits):
        bit_str = ""
        for k in range(0, bits):
            if model[first]:
                bit_str = "1" + bit_str
            else:
                bit_str = "0" + bit_str
            first = str(int(first) + 1)
        return bit_str, first

    def twos(self, val_str, bytes):
        val = int(val_str, 2)
        b = val.to_bytes(bytes, byteorder=sys.byteorder, signed=False)
        return int.from_bytes(b, byteorder=sys.byteorder, signed=True)


class Table:
    def __init__(self, table, active_rows, active_cols):
        self.table = table
        self.active_rows = active_rows
        self.active_cols = active_cols
        self.rows = sum(active_rows)
        self.cols = sum(active_cols)

    def toString(self):
        string = "Input Table\n"
        for i in range(len(self.active_rows)):
            if self.active_rows[i] == 1:
                for j in range(len(self.active_cols)):
                    if self.active_cols[j] == 1:
                        string += " [" + str(self.table[i][j]) + "]"
                string += "\n"
        return string[:-1]

    def __str__(self):
        tab = ""
        active = ""
        for i in range(len(self.active_rows)):
            if self.active_rows[i] == 1:
                active += "df->active_rows[{}] = 1;\n".format(i)
                for j in range(len(self.active_cols)):
                    if self.active_cols[j] == 1:
                        tab += "df->table[{}][{}]".format(i,j) + " = " + str(self.table[i][j]) + ";\n"
                tab += "\n"
        return tab + active
