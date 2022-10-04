import numpy as np
from scipy.integrate import odeint
import itertools as iter
import multiprocessing as mp
import time

from src.data_structures import FischerModel


def get_S_matrix(fsm: FischerModel):
    """now we calculate the derivative with respect to the parameters
    The matrix S has the form
    i   -->  index of parameter
    jk  -->  index of kth variable
    t   -->  index of time
    S[i, j1, j2, ..., t] = (dO/dp_i(v_j1, v_j2, v_j3, ..., t))"""
    (y0, t0) = fsm.y0_t0
    S = np.zeros((len(fsm.parameters),) + (fsm.times.shape[-1],) + tuple(len(x) for x in fsm.q_values))
    error_n = np.zeros((fsm.times.shape[-1],) + tuple(len(x) for x in fsm.q_values))

    # Iterate over all combinations of Q-Values
    solutions = []
    for index in iter.product(*[range(len(q)) for q in fsm.q_values]):
        # Store the results of the respective ODE solution
        Q = [fsm.q_values[i][j] for i, j in enumerate(index)]
        t = fsm.times[index]

        # Actually solve the ODE for the selected parameter values
        #r = solve_ivp(ODE_func, [t0, t.max()], y0, method='Radau', t_eval=t,  args=(Q, P, Const), jac=jacobian).y.T[1:,:]
        r = odeint(fsm.ode_func, y0, np.insert(t, 0, t0), args=(Q, fsm.parameters, fsm.constants), Dfun=fsm.jacobian).T[:, 1:]

        # Calculate the S-Matrix with the supplied jacobian
        S[(slice(None), slice(None)) + index] = r[1:]

        # Assume that the error of the measurement is 25% from the measured value r[0] n 
        # (use for covariance matrix calculation)
        error_n[:, index] = r[0].reshape(fsm.times.shape[-1], 1) * 0.25
        solutions.append((t, Q, r))
    # Reshape to 2D Form (len(P),:)
    S = S.reshape((len(fsm.parameters),np.prod(S.shape[1:])))
    error_n = error_n.reshape(np.prod(error_n.shape))
    cov_matrix = np.eye(len(error_n), len(error_n)) * error_n**2
    C = np.linalg.inv(cov_matrix)
    return S, C, solutions


def fischer_determinant(fsm: FischerModel, S, C):
    # Calculate Fisher Matrix
    F = (S.dot(C)).dot(S.T)

    # Calculate Determinant
    det = np.linalg.det(F)
    return det


def fischer_sumeigenval(fsm: FischerModel, S, C):
    # Calculate Fisher Matrix
    F = S.dot(C).dot(S.T)

    # Calculate sum eigenvals
    sumeigval = np.sum(np.linalg.eigvals(F))
    return sumeigval

def fischer_mineigenval(fsm: FischerModel, S, C):
    # Calculate Fisher Matrix
    F = S.dot(C).dot(S.T)

    # Calculate sum eigenvals
    mineigval = np.min(np.linalg.eigvals(F))
    return mineigval


def calculate_fischer_observable(fsm: FischerModel, covar=False):
    S, C, r = get_S_matrix(fsm)
    if covar == False:
        C = np.eye(S.shape[1])
    obs = fsm.observable(fsm, S, C)
    return obs, fsm, S, C, r
