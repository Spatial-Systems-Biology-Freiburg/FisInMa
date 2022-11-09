import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from pathlib import Path
import itertools

from FisInMa.model import FisherResults
from FisInMa.solving import ode_rhs


def plot_all_odes(fsr: FisherResults, outdir=Path("."), additional_name=""):
    """Plots results of the ODE with time points at which the ODE is evaluated
    for every input combination.

    :param fsr: Results generated by an optimization or solving routine.
    :type fsr: FisherResults
    :param outdir: Output directory to store the images in. Defaults to Path(".").
    :type outdir: Path, optional
    """
    for i, sol in enumerate(fsr.individual_results):
        # Get ODE solutions
        r = sol.ode_solution

        n_x = len(sol.ode_x0)

        # Get time interval over which to plot
        times_low = sol.ode_t0
        times_high = fsr.variable_definitions.times.ub if fsr.variable_definitions.times is not None else np.max(sol.times)
        
        # Solve the ODE on a sufficiently filled interval
        t_values = np.linspace(times_low, times_high)
        res = sp.integrate.solve_ivp(fsr.ode_fun, (times_low, times_high), sol.ode_x0, t_eval=t_values, args=(sol.inputs, sol.parameters, sol.ode_args))
        t = np.array(res.t)
        y = np.array(res.y)

        # Plot the solution and store in individual files
        for j in range(n_x):
            # Create figures and axis
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plot the continuous ODE solution
            ax.plot(t, y[j], color="#21918c", label="Ode Solution")
            
            # Determine where multiple time points overlap by rounding
            ax.scatter(sol.ode_solution.t, sol.ode_solution.y[j], s=160, alpha=0.5, color="#440154", label="Time Points: " + str(sol.inputs))
            ax.legend()
            # TODO - add table with parameters, inputs, ode_t0, ode_y0, etc.
            fig.savefig(outdir / Path("ODE_Result_{}_{}_{}_{:03.0f}_x_{:02.0f}.svg".format(fsr.ode_fun.__name__, fsr.criterion_fun.__name__ , additional_name, i, j)))

            # Remove figure to free space
            plt.close(fig)


def plot_all_sensitivities(fsr: FisherResults, outdir=Path("."), additional_name=""):
    r"""Plots results of the sensitivities :math:`s_{ij} = \frac{\partial y_i}{\partial p_j}` with time points at which the ODE is evaluated
    for every input combination.

    :param fsr: Results generated by an optimization or solving routine.
    :type fsr: FisherResults
    :param outdir: Output directory to store the images in. Defaults to Path(".")., defaults to Path(".")
    :type outdir: Path, optional
    """
    for i, sol in enumerate(fsr.individual_results):
        # Get time interval over which to plot
        times_low = sol.ode_t0
        times_high = fsr.variable_definitions.times.ub if fsr.variable_definitions.times is not None else np.max(sol.times)

        # Plot solution to sensitivities
        t_values = np.linspace(times_low, times_high)

        # Helper variables
        n_x = len(sol.ode_x0)
        n_p = len(sol.parameters)
        n_p_full = n_p + (n_x if callable(fsr.ode_dfdx0) else 0)

        # Define initial values for sensitivities
        if callable(fsr.ode_dfdx0):
            x0_full = np.concatenate((sol.ode_x0, np.zeros(n_x * n_p), np.ones(n_x)))
        else:
            x0_full = np.concatenate((sol.ode_x0, np.zeros(n_x * n_p)))

        # Solve the ODEs
        res = sp.integrate.solve_ivp(ode_rhs, (times_low, times_high), x0_full, t_eval=t_values, args=(fsr.ode_fun, fsr.ode_dfdx, fsr.ode_dfdp, fsr.ode_dfdx0, sol.inputs, sol.parameters, sol.ode_args, n_x, n_p))
        t = np.array(res.t)

        # Iterate over all possible sensitivities
        for j, k in itertools.product(range(n_x), range(n_p_full)):
            # Get ODE solutions
            if fsr.relative_sensitivities==False:
                norm1 = 1.0
                norm2 = 1.0
            else:
                norm1 = sol.ode_solution.y[:n_x].reshape((n_x, -1))[j]
                norm2 = np.array(res.y[:n_x].reshape((n_x, -1))[j])

            r = sol.ode_solution.y[n_x:].reshape((n_x, n_p_full, -1))[j, k] / norm1

            # Create figure and axis
            fig, ax = plt.subplots(figsize=(10, 6))
            y = np.array(res.y[n_x:].reshape((n_x, n_p_full, -1))[j, k]) / norm2
            ax.plot(t, y, color="#21918c", label="Sensitivities Solution")

            # Plot sampled time points
            ax.scatter(sol.ode_solution.t, r, s=160, alpha=0.5, color="#440154", label="Time Points: " + str(sol.inputs))
            ax.legend()
            # TODO - add table with parameters, inputs, ode_t0, ode_y0, etc.
            fig.savefig(outdir / Path("Sensitivities_Results_{}_{}_{}_{:03.0f}_x_{:02.0f}_p_{:02.0f}.svg".format(fsr.ode_fun.__name__, fsr.criterion_fun.__name__ , additional_name, i, j, k)))

            # Remove figure to free space
            plt.close(fig)

# New (corrected) sensitivities plotting
def plot_all_sensitivities2(fsr: FisherResults, outdir=Path("."), additional_name=""):
    for i, sol in enumerate(fsr.individual_results):
        times_low = sol.ode_t0
        times_high = fsr.variable_definitions.times.ub if fsr.variable_definitions.times is not None else np.max(sol.times)
        # Plot solution to sensitivities
        t_values = np.linspace(times_low, times_high)

        # Helper variables
        n_x = len(sol.ode_x0)
        n_p = len(sol.parameters)
        n_p_full = n_p + (n_x if callable(fsr.ode_dfdx0) else 0)
        if callable(fsr.obs_fun) and callable(fsr.obs_dgdp) and callable(fsr.obs_dgdx):
            n_obs = np.array(fsr.obs_fun(sol.ode_t0, sol.ode_x0, sol.inputs, sol.parameters, sol.ode_args)).size
        else:
            n_obs = n_x

        # Define initial values for sensitivities
        if callable(fsr.ode_dfdx0):
            x0_full = np.concatenate((sol.ode_x0, np.zeros(n_x * n_p), np.ones(n_x)))
        else:
            x0_full = np.concatenate((sol.ode_x0, np.zeros(n_x * n_p)))

        # Solve the ODEs
        res = sp.integrate.solve_ivp(ode_rhs, (times_low, times_high), x0_full, t_eval=t_values, args=(fsr.ode_fun, fsr.ode_dfdx, fsr.ode_dfdp, fsr.ode_dfdx0, sol.inputs, sol.parameters, sol.ode_args, n_x, n_p))
        t = np.array(res.t)

        # If the observable was specified we will transform the result with
        # dgdp = dgdp + dxdp * dgdx
        x = res.y[:n_x].reshape((n_x, -1))
        r = np.array(res.y[n_x:])
        s = np.swapaxes(r.reshape((n_x, n_p_full, -1)), 0, 1)
        #s, obs = _calculate_sensitivities_with_observable(fsmp, t_red, x, s, Q, n_x0, n_obs, n_p, relative_sensitivities, **kwargs)

        n_t = t.size
        if callable(fsr.obs_fun) and callable(fsr.obs_dgdp) and callable(fsr.obs_dgdx):
            # Calculate the first term of the equation
            term1 = np.array([fsr.obs_dgdp(ti, x[:,i_t], sol.inputs, sol.parameters, sol.ode_args) for i_t, ti in enumerate(t)]).reshape((n_t, n_obs, n_p)).swapaxes(0, 2)

            # Calculate the second term of the equation and add them
            term2 = np.array([
            # This has shape (n_x, n_obs)
                np.array(fsr.obs_dgdx(ti, x[:,i], sol.inputs, sol.parameters, sol.ode_args), dtype=float)
                    .reshape((n_x, n_obs))
                    .T
                    .dot(s[:n_p,:,i].T)
                    for i, ti in enumerate(t)
            ]).reshape((n_t, n_obs, n_p)).swapaxes(0, 2)

        if callable(fsr.ode_dfdx0) and callable(fsr.obs_dgdx0):
            # Calculate term1_add which is dgdx0_ik for every time point in t
            term1_add = np.array([
                fsr.obs_dgdx0(ti, x[:,i_t], sol.inputs, sol.parameters, sol.ode_args)
                for i_t, ti in enumerate(t)
            ]).reshape((-1, n_obs, n_x)).swapaxes(0, 2)

            # Calculate term2_add which is dgdx0_ij * s_jk
            term2_add = np.array([
                np.array(fsr.obs_dgdx(ti, x[:,ii], sol.inputs, sol.parameters, sol.ode_args), dtype=float)
                    .reshape((n_x, n_obs))
                    .T
                    .dot(s[n_p:,:,ii].T)
                for ii, ti in enumerate(t)
            ]).reshape((n_t, n_obs, n_x)).swapaxes(0, 2)
            
            term1_full = np.concatenate([term1, term1_add], axis=0)
            term2_full = np.concatenate([term2, term2_add], axis=0)

            s = term1_full + term2_full
        else:
            s = term1 + term2
        # Also calculate the results for the observable which can be used later for relative sensitivities
        obs = np.array([fsr.obs_fun(ti, x[:,i_t], sol.inputs, sol.parameters, sol.ode_args) for i_t, ti in enumerate(t)]).reshape((-1, n_obs)).T
        if fsr.relative_sensitivities==True:
            # Multiply by parameter
            if callable(fsr.ode_dfdx0):
                params = sol.parameters + (*sol.ode_x0,)
            else:
                params = sol.parameters
            print(params)
            for ii, p in enumerate(params):
                s[ii] *= p

            # Divide by observable
            for ii, o in enumerate(obs):
                s[(slice(None), ii)] /= o

        for j, k in itertools.product(range(n_obs), range(n_p_full)):
            r = sol.sensitivities[k, j]
            y = s[k, j]

            # Create figure and axis
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(t, y, color="#21918c", label="Sensitivities Solution")

            # Plot sampled time points
            ax.scatter(sol.ode_solution.t, r, s=160, alpha=0.5, color="#440154", label="Design" + str(sol.inputs))
            ax.legend()
            fig.savefig(outdir / Path("Sensitivities_Results2_{}_{}_{}_{:03.0f}_x_{:02.0f}_p_{:02.0f}.svg".format(fsr.ode_fun.__name__, fsr.criterion_fun.__name__ , additional_name, i, j, k)))

            # Remove figure to free space
            plt.close(fig)


def plot_all_solutions(fsr: FisherResults, outdir=Path("."), additional_name=""):
    r"""Combines functionality of plot_all_odes and plot_all_sensitivities.
    Plots results of the ODE with time points at which the ODE is evaluated
    and results of the sensitivities :math:`s_{ij} = \frac{\partial y_i}{\partial p_j}`
    with time points at which the ODE is evaluated for every input combination.

    :param fsr: Results generated by an optimization or solving routine.
    :type fsr: FisherResults
    :param outdir: Output directory to store the images in. Defaults to Path(".")., defaults to Path(".")
    :type outdir: Path, optional
    """
    plot_all_odes(fsr, outdir)
    plot_all_sensitivities(fsr, outdir)


# TODO - find way to plot json dump from database
