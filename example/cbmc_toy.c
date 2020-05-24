typedef struct pair {
    int x, y;
} pair;

int equiv(const void* o1, const void* o2) {
    pair* p1 = (pair*) o1;
    pair* p2 = (pair*) o2;

    return p1->x == p2->x && p1->y == p2->y;
}

void init_input(void *input) {
    pair* p = (pair*) input;
INPUT_CONSTRAINTS
}

void copy_input(void *from, void* to) {
    pair* f = (pair*) from;
    pair* t = (pair*) to;

    t->x = f->x;
    t->y = f->y;
}

int sum(int x, int y) { return x + y; }
int sub(int x, int y) { return x - y; }
int mul(int x, int y) { return x * y; }
int div(int x, int y) { return x / y; }

PROGRAM_STRINGS