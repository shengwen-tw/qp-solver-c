'''
do not directly run this script, you should execute the unit test
by launching the "run_test.sh"
'''

import libqpsolver
import os
import numpy as np
from cvxopt import matrix, solvers

test_failed_counter = 0

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def quadprog_cvxopt(P, q, A=None, b=None, A_eq=None, b_eq=None, options=None):
    """
    qp solver provided by cvxopt package:

    Minimize    (1/2)(x.' * P * x) + (q.' * x)
    Subject to  A * x < b
    and         A_eq * x = b_eq
    """

    #verbose option
    #options = solvers.options['show_progress'] = False

    #objective function
    P, q = matrix(P), matrix(q)

    #inequality constraint
    if (A is not None) and (b is not None):
        A, b = matrix(A), matrix(b)
    else:
        A, b = None, None

    #equality constraint
    if (A_eq is not None) and (b_eq is not None):
        A_eq, b_eq = matrix(A_eq), matrix(b_eq)
    else:
        A_eq, b_eq = None, None

    #solve qp
    sol = solvers.qp(P, q, A, b, A_eq, b_eq, options);
    return np.array(sol['x'])

def matrix_compare(mat1, mat2):
    epsilon = 1 #1e-3

    if len(mat1) != len(mat2):
        print('dimension of matrices are not equal for comparasion')
        return False;

    for i in range(len(mat1)):
        abs_diff = abs(mat1[i] - mat2[i])
        if abs_diff > epsilon:
            return False

    return True

def generate_symmetric_positive_definite_matrix(row, column, max_val):
    vec = np.random.rand(row, column)
    vec_transposed = np.transpose(vec)

    spd_matrix = np.matmul(vec, vec_transposed)
    spd_matrix = np.multiply(max_val, spd_matrix)

    return spd_matrix

def generate_random_row_vector(row, max_val):
    vec = np.random.rand(row, 1)
    vec = np.multiply(max_val, vec)

    return vec

def test_random_2x2_qp_problem(cost_func_max_val):
    P = generate_symmetric_positive_definite_matrix(2, 2, cost_func_max_val);

    q = generate_random_row_vector(2, cost_func_max_val)

    A = np.array([[+1.0, +1.0],
                  [-1.0, +2.0],
                  [+2.0, +1.0]])
    b = np.array([[2.0],
                  [2.0],
                  [3.0]])

    #randomlly turn on / off the equality constraints
    A_eq = None;
    b_eq = None;
    if np.random.rand(1, 1) < 0.5:
        A_eq = np.array([[1.0, 1.0]])
        b_eq = np.array([[0.0]])

    print('[Test input matrices]')
    print('P = \n%s' %(P))
    print('q = \n%s' %(q))
    print('A = \n%s' %(A))
    print('b = \n%s' %(b))
    print('A_eq = \n%s' %(A_eq))
    print('b_eq = \n%s\n' %(b_eq))

    print('[debug message from CVXOPT]')
    cvxopt_sol = quadprog_cvxopt(P, q, A, b, A_eq, b_eq, None)

    print('\n[debug message from libqpsolver]')
    libqpsolver_sol = libqpsolver.quadprog(P, q, A, b, A_eq, b_eq, None, None)

    print('\n[Optimal solution by CVXOPT]')
    print(cvxopt_sol)

    print('\n[Optimal solution by libqpsolver]')
    print(libqpsolver_sol)

    test_result = matrix_compare(cvxopt_sol, libqpsolver_sol)

    global test_failed_counter

    if test_result == True:
        print(f"{bcolors.OKGREEN}\n[unit test passed]{bcolors.ENDC}")
    else:
        print(f"{bcolors.FAIL}\n[error, unit test did not passed]{bcolors.ENDC}")
        test_failed_counter = test_failed_counter + 1

    print('=============================================================')

    return test_result

def test_libqpsolver():
    for i in range(0, 50):
        test_random_2x2_qp_problem(100)
        test_random_2x2_qp_problem(500)
        test_random_2x2_qp_problem(1000)

def main():
    test_libqpsolver()
    print('unit test failed times: %d' %(test_failed_counter))

    if test_failed_counter > 0:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__": main()
