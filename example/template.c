#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ROWS N_ROWS
#define COLS N_COLS
#define FALSE 0
#define TRUE 1
#define INFINITY 8388607
#define N_DECIMALS 100
#define NUMBER_PROGRAMS N_PROGRAMS
#define CBMC

#ifdef CBMC
typedef __CPROVER_bitvector[8] int8;
typedef __CPROVER_bitvector[24] dec24;
#else
typedef char int8;
typedef int dec24;
#endif

typedef struct dataframe {
    dec24 table[ROWS][COLS];
    int8 active_rows[ROWS];
    int8 active_cols[COLS];
    // only supporting one group for now
    int8 order[ROWS];
    int8 groups[ROWS];
    int8 col_group;

} dataframe;

// define how many int8s we need for our examples
//typedef __CPROVER_int8vector[2] bv;

enum filter_op{lte, ne, eq, gte};
enum mutate_op{normalize, normalize_100};
enum mutate_date_op{wday, year, month, days_between};
enum summarize_op{mean, median, sum, max, min};
enum arrange_op{ascending, descending};

// aux functions
void insertion_sort(dec24 array[], int8 max_val) {
    dec24 key;
    int8 i, j;
    for (i = 1; i < ROWS; i++) {
        if (i < max_val) {
            key = array[i];
            j = i - 1;
            while (j >= 0 && array[j] > key) {
                array[j + 1] = array[j];
                j = j - 1;
            }
            array[j + 1] = key;
        }
    }
}


void arrange_aux(dataframe *df, enum arrange_op operator, int8 col, int8 order[]) {
    if (df->active_cols[col] == 1) {
        dec24 key;
        for (int8 i = 0; i < ROWS; i++) {
            order[i] = i;
        }
        for (int8 i = 1; i < ROWS; i++) {
            int8 j = i - 1;
            int8 idx = order[i];
            key = df->table[idx][col];
            if (operator == ascending) {
                while (j >= 0 && df->table[order[j]][col] < key) {
                    order[j+1] = order[j];
                    j = j - 1;
                }
            }
            else {
                while (j >= 0 && df->table[order[j]][col] > key) {
                    order[j+1] = order[j];
                    j = j - 1;
                }
            }
            order[j+1] = idx;
        }
    }
}

// dplyr functions
void group_by(dataframe *df, int8 col) {
    if (df->active_cols[col]){
        df->col_group = col;
        // reset the previous groups
        for (int8 i = 0; i < ROWS; i++)
            df->groups[i] = 0;
        int8 current_group = 1;
        for (int8 i = 0; i < ROWS; i++){
            if (df->groups[i] != 0)
                continue;
            for (int8 j = i+1; j < ROWS; j++){
                if (df->table[i][col] == df->table[j][col])
                    df->groups[j] = current_group;
            }
            df->groups[i] = current_group;
            current_group++;
        }
    }
}

void filter (dataframe *df, enum filter_op operator, int8 col, dec24 value) {
    if (df->active_cols[col]){
        for (int8 i=0; i < ROWS; i++){
            if (!df->active_rows[i])
                continue;
            if (operator == lte){
                if (!(df->table[i][col] <= value))
                    df->active_rows[i]=0;
            } else if (operator == eq){
                if (!(df->table[i][col] == value)){
                    df->active_rows[i]=0;
                }
            } else if (operator == ne){
                if (!(df->table[i][col] != value)){
                    df->active_rows[i]=0;
                }
            } else if (operator == gte){
                if (!(df->table[i][col] >= value)){
                    df->active_rows[i]=0;
                }
            }
        }
    }
}

void count(dataframe *df) {
    int8 n_elements[ROWS]; // n_elements[i] ---> number of elements of group[i]
    int8 chosen_elements[ROWS]; // chosen_element[i] ---> representative of group[i]

    //initialize variables
    for (int8 i = 0; i < ROWS; i++){
        n_elements[i] = 0;
        chosen_elements[i] = -1;
    }

    for (int8 i = 0; i < COLS; i++){
        df->active_cols[i] = 0; //all cols inactive
    }
    df->active_cols[df->col_group] = 1; //grouped col
    df->active_cols[COLS-1] = 1; //count result

    //count the number of elements in each group.
    //activate only 1 row per group, thus choose the first;
    for (int8 i = ROWS - 1; i >= 0; i--) {
        if (df->active_rows[i] == 1) {
            chosen_elements[df->groups[i]-1] = i; // row selected to be a representative of the group
            n_elements[df->groups[i]-1]++;
            df->active_rows[i] = 0; //deactivate all rows
        }
    }
    for (int8 i = 0; i < ROWS; i++) {
        if (chosen_elements[i] != -1) {
            int8 row = chosen_elements[i];
            df->active_rows[row] = 1; //activate the selected representative of the group
            df->table[row][COLS-1] = n_elements[i] * N_DECIMALS;
        }
    }
}

void mutate(dataframe *df, enum mutate_op operator, int8 col) {
    if (df->active_cols[col]) {
        float sum = 0;
        int8 bad = FALSE;
        for (int8 i = 0; i < ROWS; i++){
            if (df->active_rows[i] == 1) {
                sum += df->table[i][col];
                if (df->table[i][col] < 0) bad = TRUE;
            }
        }

        for (int8 i = 0; i < ROWS; i++){
            if (df->active_rows[i] == 1) {
                if (bad || sum == 0) {
                    df->table[i][col] = -100;
                }
                else {
                    df->table[i][col] = (df->table[i][col]) / (sum / 100.0f);
                    if (operator == normalize_100)
                        df->table[i][col] *= 100;
                }
            }
        }
    }
}


void mutate_date(dataframe *df, enum mutate_date_op operator, int8 col1, int8 col2) {
    if (df->active_cols[col1]) {
        if (operator == wday) {
            for (int8 i = 0; i < ROWS; i++){
                // dia 1 de janeiro de 1970 ... quinta-feira
                if (df->active_rows[i] == 1) {
                    df->table[i][col1] = (df->table[i][col1] + 4) % 7 + 1;
                }
            }
        } else if (operator == days_between) {
            if (df->active_cols[col2]) {
                df->active_cols[col2] = 0;
                for (int8 i = 0; i < ROWS; i++){
                    if (df->active_rows[i] == 1) {
                        df->table[i][col1] = df->table[i][col2] - df->table[i][col1];
                    }
                }
            }
        } else if (operator == year) {
            for (int8 i = 0; i < ROWS; i++){
                // dia 1 de janeiro de 1970 ... quinta-feira
                if (df->active_rows[i] == 1) {
                    df->table[i][col1] = 1970 + (df->table[i][col1] * 100) / 36525; //slightly wrong
                }
            }
        } else if (operator == month) {
            for (int8 i = 0; i < ROWS; i++){
                if (df->active_rows[i] == 1) {
                    int val = (df->table[i][col1] * 10000) / 36525;
                    int dia = 365 * (val % 100);
                    df->table[i][col1] = dia / 3050 + 1; //well
                }
            }
        }
    }
}


void summarize(dataframe *df, enum summarize_op operator, int8 col) {
    if (df->active_cols[col]){
        for (int8 i = 0; i < COLS; i++){
            df->active_cols[i] = 0; //all cols inactive
        }
        df->active_cols[df->col_group] = 1; //grouped col
        df->active_cols[COLS-1] = 1; //count result


        if (operator == mean || operator == sum){
            dec24 group_sum[ROWS]; // sum[i] ---> sum of all elements of group[i]
            int8 n_elements[ROWS]; // n_elements[i] ---> number of elements of group[i]
            int8 chosen_elements[ROWS]; // chosen_element[i] ---> representative of group[i]
            int8 bad = FALSE;

            for (int8 i = 0; i < ROWS; i++){
                group_sum[i] = 0;
                n_elements[i] = 0;
                chosen_elements[i] = -1;
            }
            for (int8 i = ROWS - 1; i >= 0; i--){
                if (df->active_rows[i] == 1) {
                    group_sum[df->groups[i]-1] += df->table[i][col];
                    n_elements[df->groups[i]-1]++;
                    chosen_elements[df->groups[i]-1] = i;
                    df->active_rows[i] = 0;
                    if (df->table[i][col] < 0) bad = TRUE;
                }
            }
            for (int8 i = 0; i < ROWS; i++) {
                if (chosen_elements[i] != -1) {
                    int8 row = chosen_elements[i];
                    df->active_rows[row] = 1;
                    if (bad) {
                        df->table[row][COLS-1] = -100; // we don't sum NAs
                    } else if (operator == mean) {
                        df->table[row][COLS-1] = group_sum[i]/n_elements[i];
                    } else if (operator == sum) {
                        df->table[row][COLS-1] = group_sum[i];
                    }
                }
            }
        } else if (operator == max || operator == min) {
            dec24 group_res[ROWS]; // group_res[i] ---> max/min of group[i]
            int8 chosen_elements[ROWS]; // chosen_element[i] ---> representative of group[i]
            for (int8 i = 0; i < ROWS; i++){
                group_res[i] = operator == max ? -INFINITY : INFINITY;
                chosen_elements[i] = -1;
            }
            for (int8 i = 0; i < ROWS; i++){
                if (df->active_rows[i] == 1) {
                    if (df->table[i][col] > group_res[df->groups[i]-1] && operator == max) {
                        group_res[df->groups[i]-1] = df->table[i][col];
                        chosen_elements[df->groups[i]-1] = i;
                    } else if (df->table[i][col] < group_res[df->groups[i]-1] && operator == min) {
                        group_res[df->groups[i]-1] = df->table[i][col];
                        chosen_elements[df->groups[i]-1] = i;
                    }
                    df->active_rows[i] = 0;
                }
            }
            for (int8 i = 0; i < ROWS; i++){
                if (chosen_elements[i] != -1) {
                    int8 row = chosen_elements[i];
                    df->active_rows[row] = 1;
                    df->table[row][COLS-1] = group_res[i];
                }
            }
        } else if (operator == median) {
            dec24 group_vals[ROWS][ROWS]; // group_vals[i][j] ---> j'th element of group i
            int8 chosen_elements[ROWS]; // chosen_element[i] ---> representative of group[i]
            int8 counter[ROWS]; // aux var to populate group_vals
            for (int8 i = 0; i < ROWS; i++){
                memset(group_vals[i], 0, ROWS * sizeof(group_vals[i][0]));
                chosen_elements[i] = -1;
                counter[i] = 0;
            }
            for (int8 i = ROWS - 1; i >= 0; i--) {
                if (df->active_rows[i] == 1) {
                    int8 group_n = df->groups[i]-1;
                    group_vals[group_n][counter[group_n]++] = df->table[i][col];
                    chosen_elements[group_n] = i;
                    df->active_rows[i] = 0;

                }
            }
            for (int8 i = 0; i < ROWS; i++) {
                if (chosen_elements[i] != -1) {
                    int8 row = chosen_elements[i];
                    df->active_rows[row] = 1;

                    insertion_sort(group_vals[i], counter[i]); // we sort the elements of each group
                    int8 mid = counter[i] / 2; // take the median value
                    if (counter[i] % 2 != 0) { // if size of the array is odd
                        df->table[row][COLS-1] = group_vals[i][mid];
                    } else { // otherwise we calculate the average
                        df->table[row][COLS-1] = (group_vals[i][mid] + group_vals[i][mid-1])/2;

                    }
                }
            }
        }
    }
}


void arrange(dataframe *df, enum arrange_op operator, int8 col){
    arrange_aux(df, operator, col, df->order);
}


void top_n(dataframe *df, int8 col, int8 n) {
    if (df->active_cols[col] == 1) {
        int8 order[ROWS];
        arrange_aux(df, ascending, col, order);
        int8 count = 0;
        for (int8 i = 0; i < ROWS; i++){
            if (df->active_rows[order[i]] == 1 && count >= n) {
                df->active_rows[order[i]] = 0;
            }
            else if (df->active_rows[order[i]] == 1) {
                count++;
            }
        }
    }
}

void bottom_n(dataframe *df, int8 col, int8 n) {
    if (df->active_cols[col] == 1) {
        int8 order[ROWS];
        arrange_aux(df, descending, col, order);
        int8 count = 0;
        for (int8 i = 0; i < ROWS; i++){
            if (df->active_rows[order[i]] == 1 && count >= n) {
                df->active_rows[order[i]] = 0;
            }
            else if (df->active_rows[order[i]] == 1) {
                count++;
            }
        }
    }
}

void select_(dataframe *df, int8* cols, int8 n_cols) {
    for (int8 i = 0; i < COLS; i++) {
        df->active_cols[i] = 0;
    }
    for (int8 i = 0; i < COLS; i++) {
        if (i < n_cols) {
            df->active_cols[cols[i]] = 1;
        }
    }
}

PROGRAM_STRINGS

int8 equiv(dataframe *df1, dataframe *df2){
    int8 eq = 1;

    if (eq){
        int8 sum1 = 0;
        int8 sum2 = 0;
        for (int8 i = 0; i < ROWS; i++){
            sum1 += df1->active_rows[i];
            sum2 += df2->active_rows[i];
        }
        if (sum1 != sum2)
            eq = 0;
        //hack
        if (sum1 == 0 && sum2 == 0)
            return 1;
    }

    if (eq) {
        for (int8 i = 0; i < COLS; i++){
            if(df1->active_cols[i] != df2->active_cols[i])
                eq = 0;
        }
    }

    if (eq){

        //WE NEED TO FILTER THE ORDERING BECAUSE SOME ROWS MIGHT BE INACTIVE
        int8 filter_order1[ROWS], filter_order2[ROWS];
        memset(filter_order1, -1, ROWS * sizeof(filter_order1[0]));
        memset(filter_order2, -1, ROWS * sizeof(filter_order2[0]));

        //aux vars
        int8 prev1 = -1;
        int8 prev2 = -1;
        for (int8 i = 0; i < ROWS; i++){
            int8 break1 = FALSE;
            int8 break2 = FALSE;


            for (int8 j = 0; j < ROWS; j++) {
                if (df1->active_rows[df1->order[j]] == 1 && j > prev1 && !break1) {
                    filter_order1[i] = df1->order[j];
                    prev1 = j;
                    break1 = TRUE;
                }
                if (df2->active_rows[df2->order[j]] == 1 && j > prev2 && !break2) {
                    filter_order2[i] = df2->order[j];
                    prev2 = j;
                    break2 = TRUE;
                }
            }
        }
        //WE CAN DO ROWWISE COMPARISONS NOW !!
        for (int8 i = 0; i < ROWS; i++){
            if (filter_order1[i] != -1) {
                for (int8 j = 0; j < COLS; j++){
                    if (df1->active_cols[j]){
                        if (df1->table[filter_order1[i]][j] != df2->table[filter_order2[i]][j]){
                            eq = 0;
                        }
                    }
                }
            }
        }
    }
    return eq;
}

int8 not_equiv(int8 eq) {
    return !eq;
}

int8 is_equiv(int8 eq) {
    return eq;
}


void init_input(dataframe *df){
#ifdef CBMC
    for (int8 i = 0; i < ROWS; i++) {
INPUT_CONSTRAINTS
    }
#else

#endif

    //no groups
    for (int8 i = 0; i < ROWS; i++)
        df->groups[i] = 0;
    df->col_group = 0;
    // the last column is for special operators and it is disabled
    for (int8 i = 0; i < ROWS; i++)
        df->table[i][COLS-1] = 0;

    // at least one active row
#ifdef CBMC
    int8 row_sum = 0;
    for (int8 i = 0; i < ROWS; i++) {
        row_sum += df->active_rows[i];
        __CPROVER_assume(df->active_rows[i] >= 0 && df->active_rows[i] <= 1);
    }
    __CPROVER_assume(row_sum > 1);

    __CPROVER_assume(df->active_rows[0] == 1);
    for (int8 i = 1; i < ROWS; i++)
        __CPROVER_assume(df->active_rows[i] == 0 || df->active_rows[i-1] == 1);
#else
    for (int8 i = 0; i < ROWS; i++)
        df->active_rows[i] = 0;
INITIALIZE_ACTUAL_INPUTS

#endif

    df->active_cols[COLS-1] = 0;
    for (int8 i = 0; i < COLS-1; i++){
        df->active_cols[i] = 1;
    }
     for (int8 i = 0; i < ROWS; i++){
        df->order[i] = i;
    }
}



void copy_input(dataframe *from, dataframe *to){
    for (int8 i = 0; i < ROWS; i++){
        for (int8 j = 0; j < COLS; j++){
            to->table[i][j] = from->table[i][j];
        }
    }

    for (int8 i =0; i < ROWS; i++){
        to->active_rows[i] = from->active_rows[i];
    }

    for (int8 i =0; i < COLS; i++){
        to->active_cols[i] = from->active_cols[i];
    }

    to->col_group = from->col_group;

    for (int8 i = 0; i < ROWS; i++)
        to->groups[i] = from->groups[i];

    for (int8 i = 0; i < ROWS; i++)
        to->order[i] = from->order[i];

}

#ifndef CBMC
void pretty_print(dataframe *df){
    printf("Output Table:\n");
    for (int i = 0; i < ROWS; i++){
        if (df->active_rows[df->order[i]] == 1) {
            for (int j = 0; j < COLS; j++){
                if (df->active_cols[j] == 1) {
                    printf(" [%d]",df->table[df->order[i]][j]);
                }
            }
            printf("\n");
        }
    }
}
#endif

int main(int argc, char *argv[]) {

    dataframe df;
    init_input(&df);

    dataframe p[NUMBER_PROGRAMS];

PROGRAM_CALLS
#ifdef CBMC
EQUALITY_PROGRAMS

ASSERTIONS
#endif
}
