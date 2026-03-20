"""
MultiExperiment Example Script

This script demonstrates how to use the MultiExperiment class to set up and simulate
multiple electrochemical experiments simultaneously. It combines both FTACV (Fourier
Transform Alternating Current Voltammetry) and SWV (Square Wave Voltammetry) experiments
with different parameters, showing how to:
1. Configure multiple experiments with shared and unique parameters
2. Set up Fourier transform analysis for FTACV experiments
3. Define optimization parameters and boundaries
4. Group experiments for analysis and visualization
5. Run simulations across all experiments
"""

import Surface_confined_inference as sci
import numpy as np
import matplotlib.pyplot as plt
import os

# Dictionary to hold all experiment configurations
experiments_dict = {}

# =============================================================================
# FTACV Experiment Setup
# =============================================================================
# Define FTACV experiments at three different frequencies (3, 9, and 15 Hz)
# All experiments share the same voltage parameters except for frequency (omega)
dictionary_list = [
    # 0.5 Hz FTACV experiment
    {'E_start': np.float64(-0.09876774216779083), 'E_reverse': np.float64(0.29641788993070595), 'omega': np.float64(0.5057906962584071), 'phase': np.float64(6.278193605469088), 'delta_E': np.float64(0.1481879466674736), 'v': np.float64(0.0009993951805744579)},
    # 1.0 Hz FTACV experiment
    {'E_start': np.float64(-0.09876609297169336), 'E_reverse': np.float64(0.29641415059122433), 'omega': np.float64(1.0115814554049478), 'phase': np.float64(6.27308558049971), 'delta_E': np.float64(0.1481748395236738), 'v': np.float64(0.0009993787562514553)},
    # 1.25 Hz FTACV experiment
    {'E_start': np.float64(-0.0987884029581716), 'E_reverse': np.float64(0.2964315180022883), 'omega': np.float64(1.264475200454587), 'phase': np.float64(6.274697544033324), 'delta_E': np.float64(0.14815977053257964), 'v': np.float64(0.0014991916817624204)},
]
# Fourier transform options for FTACV experiments
# These control how the time-series data is transformed into frequency domain
FT_options = dict(
    Fourier_fitting=True,              # Enable Fourier transform analysis
    Fourier_window="hanning",          # Window function to reduce spectral leakage
    top_hat_width=0.05,                # Width of the top-hat filter in frequency domain
    Fourier_function="abs",            # Use absolute value of Fourier transform
    Fourier_harmonics=list(range(3, 10)),  # Fit harmonics 3 through 9
    dispersion_bins=[100],              # Number of bins for parameter dispersion modeling
    optim_list=["E0_mean", "E0_std", "k0", "gamma", "Ru", "Cdl", "CdlE1", "CdlE2","alpha"],  
)

# Parameter boundaries for optimization
# These define the search space for each electrochemical parameter
boundaries = {
    "E0_mean": [0.1, 0.12],          # Formal potential (V)
    "E0_std": [0.01, 0.2],	# Standard deviation in E0 (V)
    "k0": [0.01, 1],          # Standard rate constant (s^-1)
    "gamma": [1e-10, 5e-9],     # Surface coverage (mol/cm^2)
    "Ru": [1000, 10000],          # Uncompensated resistance (Ohms)
    "Cdl": [1e-6, 1e-3],         # Double layer capacitance (F)
    "alpha": [0.4, 0.6],          # Charge transfer coefficient (dimensionless)
    "CdlE1":[-1e-4, 1e-4],
    "CdlE2":[-1e-5, 1e-5]
}

# Labels for the three FTACV experiments
labels = ["0.5_Hz", "1.0_Hz", "1.25_Hz"]

# Common parameters shared across ALL experiments (both FTACV and SWV)
# These are fixed experimental conditions
common = {
    "Temp": 293,              # Temperature (K)
    "N_elec": 1,              # Number of electrons transferred in redox reaction
    "area": 0.036,            # Electrode area (cm^2)
    #"area": 0.0314,
    "Surface_coverage": 1e-9 # Surface coverage (mol/cm^2)
}

# Worst case simulation to calculate hypervolume threshold for multi experiment optimisation
# Format: [E0_mean, E0_std, k0, gamma, Ru, Cdl, alpha]
zero_ft = [0.11, 0.05, 0.1, 5e-9, 6000, 1.8e-4, 0, 0, 0.5]

# Construct the FTACV experiments and add them to the experiments dictionary. These can be anything, and will be used as
# identifiers when grouping experiments below
for i in range(0, len(labels)):
    experiments_dict = sci.construct_experimental_dictionary(
        experiments_dict,
        {**{"Parameters": dictionary_list[i]}, **{"Options": FT_options}, "Zero_params": zero_ft},
        "FTACV",     # Experiment type
        labels[i],   # Frequency label (e.g., "3_Hz")
        "150_mVamp"     # Voltage amplitude label
    )

# =============================================================================
# Square Wave Voltammetry (SWV) Experiment Setup
# =============================================================================
# Define 14 different frequencies for SWV experiments (in Hz)
sw_freqs = [5, 10, 15, 20, 25, 30, 35, 40]

# Defining threshold parameters - this involves subtracting the Fardaic peak, and smoothing 
# the resulting data
zero_sw = {
    "potential_window": [0.11-0.1, 0.11+0.1],  # Window around E0 for baseline
    "thinning": 10,       # Data point reduction factor
    "smoothing": 20       # Smoothing window size
}

# SWV experiments will be run in both anodic (oxidation) and cathodic (reduction) directions
directions = ["cathodic","anodic"]

# Configuration for each scan direction
directions_dict = {
    "anodic": {"v": 1, "E_start": -0.2},    # Scan from negative to positive potential
    "cathodic": {"v": -1, "E_start": 0.4}     # Scan from positive to negative potential
}

# SWV-specific options
sw_options = dict(
    square_wave_return="net",  # Return net current (backward - forward)
    dispersion_bins=[100],      # Number of bins for parameter dispersion modeling
    optim_list=["E0_mean", "E0_std", "k0", "gamma", "alpha"]  # Parameters to optimize (fewer than FTACV as can't model contribution of Cdl or Ru)
)

# Construct all SWV experiments
for i in range(0, len(sw_freqs)):
    for j in range(0, len(directions)):
        params = {
            "omega": sw_freqs[i],            # Frequency (Hz)
            "scan_increment": 5e-3,          # Potential step size (V)
            "delta_E": 0.6,                  # Total potential scan range (V)
            "SW_amplitude": 10e-3,            # Square wave pulse amplitude (V)
            "sampling_factor": 120,          # Points per square wave cycle
            "E_start": directions_dict[directions[j]]["E_start"],  # Starting potential
            "v": directions_dict[directions[j]]["v"]               # Scan direction (+1 or -1)
        }
        experiments_dict = sci.construct_experimental_dictionary(
            experiments_dict,
            {**{"Parameters": params}, **{"Options": sw_options}, "Zero_params": zero_sw},
            "SWV",                           # Experiment type
            "{0}_Hz".format(sw_freqs[i]),    # Frequency label
            directions[j]                    # Direction label ("anodic" or "cathodic")
        )



# =============================================================================
# Experiment Grouping for Visualization
# =============================================================================
# Define how experiments should be grouped when fitting. Multiobjetive optimisation generally
# can only optimise over fewer objectives than we have experiments, so we scalararise (and scale)
# the experiments
# Each group specification selects experiments from the total list
group_list = [
    # Group 1: FTACV time-series for frequencies 1.25 Hz
    {
        "experiment": "FTACV",
        "type": "ts",  # Time-series data
        "numeric": {"Hz": {"equals": 1.25}, "mVamp": {"equals": 150}},
        "scaling": {"divide": ["omega", "delta_E"]}  # Normalize by frequency and amplitude
    },
    # Group 2: FTACV Fourier transform for 1.25 Hz
    {
        "experiment": "FTACV",
        "type": "ft",  # Fourier transform data
        "numeric": {"Hz": {"equals": 1.25}, "mVamp": {"equals": 150}},
        "scaling": {"divide": ["omega", "delta_E"]}
    },
    # Group 3: FTACV time-series for frequencies 0.5 and 1.0 Hz
    {
        "experiment": "FTACV",
        "type": "ts",  # Time-series data
        "numeric": {"Hz": {"lesser": 1.25}, "mVamp": {"equals": 150}},
        "scaling": {"divide": ["omega", "delta_E"]}  # Normalize by frequency and amplitude
    },
    # Group 4: FTACV Fourier transform for 0.5 and 1.0 Hz
    {
        "experiment": "FTACV",
        "type": "ft",  # Fourier transform data
        "numeric": {"Hz": {"lesser": 1.25}, "mVamp": {"equals": 150}},
        "scaling": {"divide": ["omega", "delta_E"]}
    },
]

# =============================================================================
# MultiExperiment Initialization and Simulation
# =============================================================================
# Create MultiExperiment object with all configured experiments
# Total: 3 FTACV experiments + 28 SWV experiments = 31 experiments
cls = sci.MultiExperiment(
    experiments_dict,
    common=common,          # Shared parameters across all experiments
    synthetic=False,         # Flag to indicate data is synthetic
    normalise=True,         # When simulating, parameters are normalised between 0 and 1 using boundaries
    boundaries=boundaries,   # Parameter search boundaries
    SWV_e0_shift=True
)

# Get list of all parameters that will be optimized
params = cls._all_parameters

# Assign the grouping configuration 
cls.group_list = group_list

# Load experimental data files from test directory
#The (.txt) files need to be:
#1) In dimensional form
#2) Time in column 1, Current in column 2
#3) Labelled according to the group structure defined above 
# It needs an experimental signifier, numerical values in the format number_unit
# and these signifiers seperated by dashes (-)
#(e.g. FTACV-3_Hz-280_mV.txt)
fileloc = os.path.join(os.getcwd(), "/users/jas645/experimental/25-12-05_pH6.5_New_Prep_CytC6/Time_Current")
cls.file_list = [os.path.join(fileloc, file) for file in os.listdir(fileloc)]

# Check the grouping and scaling operations
#cls.check_grouping()

# Generate random parameter values for demonstration (between 0 and 1 as normalisation is on )
# In a real scenario, these would come from optimization or fitting
sim_param_vals = np.random.rand(len(params))

# Run simulations across all 31 experiments with the random parameters
# This demonstrates that the MultiExperiment infrastructure is working
cls.results(parameters=sim_param_vals)
plt.show()
ax_class=sci.AxInterface(name="Cytochrome_first_try",
			independent_runs=3,
			num_iterations=100,
			max_run_time=48,
			results_directory="/users/jas645/Cytochrome_ME/results_26-01-08_C6-OH_newprep_just_FTV",
			log_directory="/users/jas645/Cytochrome_ME/logs",
			num_cpu=30,
			simulate_front=True,
			email="jas645@york.ac.uk",
			in_cluster=True,
			project="chem-electro-2024",
			GB_ram=20)
ax_class.setup_client(cls)
ax_class.experiment()
#ax_class.run(0)
