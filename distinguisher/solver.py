import subprocess
import time


class Solver:

    def __init__(self, name):
        self.name = name

    def run(self, symbolic_representation):
        dimacs = symbolic_representation.get_dimacs()
        file_n = round(time.time() * 100)
        with open("/tmp/{}_{}.in".format(self.name, file_n), "a+") as f:
            f.write(dimacs)
            f.flush()

        cmd = "{} /tmp/{}_{}.in".format(self.name, self.name, file_n)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        lns = str(out, encoding='utf-8')

        model = self.get_model(lns.splitlines())
        return model

    def sign(self, l):
        return l[0] == '-'

    def get_model(self, lns):
        vals = dict()
        found = False
        for l in lns:
            l = l.rstrip()
            if not l: continue
            if not l.startswith('v ') and not l.startswith('V '): continue
            found = True
            vs = l.split()[1:]
            for v in vs:
                if v == '0': break
                vals[str(abs(int(v)))] = not self.sign(v)
        return vals if found else None


