#!/usr/bin/env python3

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt


# Import custom package to solve such fisher models
from FisInMa import *


# System of equation for pool-model and sensitivities
###############################
### USER DEFINES ODE SYSTEM ###
###############################
def exp_growth(t, y, Q, P, Const):
    (a,) = P
    (Temp,) = Q
    (n_max,) = Const
    (n,) = y
    return [Temp * a * (n_max - n)]

def dedx(t, y, Q, P, Const):
    (a,) = P
    (Temp,) = Q
    (n_max,) = Const
    (n,) = y
    return [[- Temp * a]]

def dedp(t, y, Q, P, Const):
    (a,) = P
    (Temp,) = Q
    (n_max,) = Const
    (n,) = y
    return [[- Temp * n]]


if __name__ == "__main__":
    ###############################
    ### USER DEFINES PARAMETERS ###
    ###############################

    # Define constants for the simulation duration
    n_max = 2e4
    constants = (n_max,)

    # Define initial parameter guesses
    a = 0.065
    parameters = (a,)

    # Define bounds for sampling
    temp_low = 3.0
    temp_high = 8.0

    # Define bounds for times
    times_low = 0.0
    times_high = 16.0

    # Initial values for complete ODE (with S-Terms)
    n0 = 0.25
    y0 = n0

    # Construct parameter hyperspace
    n_times = 4
    n_temps = 3
    
    # Values for temperatures (Q-Values)
    inputs = [
        (temp_low, temp_high, n_temps)
    ]

    # Create a complete Fisher Model
    fsm = FisherModel(
            ode_fun=exp_growth,
            ode_dfdx=dedx,
            ode_dfdp=dedp,
            ode_y0=y0,
            ode_t0=times_low,
            times=(times_low, times_high, n_times),
            inputs=inputs,
            parameters=parameters,
            constants=constants,
    )

    fsmp = FisherModelParametrized.init_from(fsm)

    S, C, solutions = get_S_matrix(fsmp)

    ####################
    ### OPTIMIZATION ###
    ####################
    # fsr = find_optimal(fsm, "scipy_differential_evolution", discrete=0.5, workers=1)
    # print(fsr.times)
    # print(fsr.criterion)
    # d = fsr.criterion
    # solutions = fsr.ode_solutions

    ####################
    ##### PLOTTING #####
    ####################
    # plot_all_odes(fsr)
