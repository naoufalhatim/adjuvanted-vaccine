# -*- coding: utf-8 -*-
"""
@author: cparrarojas

This program fits the PDE model defined in the module functions_global.py to the
data using the differential evolution algorithm.

Please, refer to the accompanying README file for details.
"""

# We import the necessary packages
from functions_global import *
import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

# Do we carry out the parameter fiting in log scale?
logscale = False
if logscale:
    costfn = rmse_log
    costfn_adj = rmse_adj_log
else:
    costfn = rmse
    costfn_adj = rmse_adj

# We start by loading the raw data and tidying it up.
# It contains 4 data points per vaccine configuration per time point.
dataRaw = pd.read_csv('../../data/VNA.csv')
timesData = dataRaw['days'].tolist() # List of time points
nMeasurements = 4

# We construct the arrays of data for each vaccine configuration
PBS = []  # Non-adjuvanted vaccine
MF59 = []  # Vaccine with MF59
AS03 = []  # Vaccine with AS03
Diluvac = []  #Vaccine with Diluvac
X_data = [] # List of (repeated) time points

for i in range(len(timesData)):
    for j in range(1,nMeasurements+1):
        X_data.append(timesData[i])
        PBS.append(dataRaw.T.iloc[j][i])
    for j in range(nMeasurements+1,2*nMeasurements+1):
        MF59.append(dataRaw.T.iloc[j][i])
    for j in range(2*nMeasurements+1,3*nMeasurements+1):
        AS03.append(dataRaw.T.iloc[j][i])
    for j in range(3*nMeasurements+1,4*nMeasurements+1):
        Diluvac.append(dataRaw.T.iloc[j][i])
PBS = np.array(PBS)
MF59 = np.array(MF59)
AS03 = np.array(AS03)
Diluvac = np.array(Diluvac)
X_data = np.array(X_data)

# Boundary values for the parameters to be estimated in the adjuvanted case
#                betaNA       betaHA       betaAb
bounds_adj = [(1.0, 100.0), (1.0, 100.0), (1.0, 1.0)]

# We use the base parameters of model A
params_base = pd.Series.from_csv('../../params/best_fit_params_base_A.csv')
gammaNA, gammaHA, mu, dmax = params_base['gammaNA'], params_base['gammaHA'], params_base['mu'], params_base['dmax']

# Base affinities and pool of naive B cells for given dmax
baseQ = vQ0(np.abs(grid), dmax) + vQ0(np.abs(1 - grid), dmax)
H = Htilde*0.5*(np.sign(grid - 0.99*dmax) + np.sign(1.0 - 0.99*dmax - grid))
base_params = [gammaNA, gammaHA, mu, dmax, baseQ, H]

# We initialise the output for the adjuvanted case and include the base
# parameters in the packed arguments
adjuvants = ['MF59', 'AS03', 'Diluvac']
betaNA_list = []
betaHA_list = []
betaAb_list = []

args_MF59 = (X_data, MF59, base_params)
args_AS03 = (X_data, AS03, base_params)
args_Diluvac = (X_data, Diluvac, base_params)

# We estimate and print the best parameters for each adjuvant
# MF59
estimation_MF59 = differential_evolution(costfn_adj, bounds_adj, args=args_MF59)
#betaNA_0, betaHA_0 = estimation_MF59.x
betaNA_0, betaHA_0, betaAb_0 = estimation_MF59.x

print """Best parameters for MF59:
betaNA: {}
betaHA: {}
betaAb: {}
""".format(betaNA_0, betaHA_0, betaAb_0)

betaNA_list.append(betaNA_0)
betaHA_list.append(betaHA_0)
betaAb_list.append(betaAb_0)

# AS03
estimation_AS03 = differential_evolution(costfn_adj, bounds_adj, args=args_AS03)
#betaNA_0, betaHA_0 = estimation_AS03.x
betaNA_0, betaHA_0, betaAb_0 = estimation_AS03.x

print """Best parameters for AS03:
betaNA: {}
betaHA: {}
betaAb: {}
""".format(betaNA_0, betaHA_0, betaAb_0)

betaNA_list.append(betaNA_0)
betaHA_list.append(betaHA_0)
betaAb_list.append(betaAb_0)

# Diluvac
estimation_Diluvac = differential_evolution(costfn_adj, bounds_adj,
                                            args=args_Diluvac)
#betaNA_0, betaHA_0 = estimation_Diluvac.x
betaNA_0, betaHA_0, betaAb_0 = estimation_Diluvac.x

print """Best parameters for Diluvac:
betaNA: {}
betaHA: {}
betaAb: {}
""".format(betaNA_0, betaHA_0, betaAb_0)

betaNA_list.append(betaNA_0)
betaHA_list.append(betaHA_0)
betaAb_list.append(betaAb_0)

best_fit_params_adj = {'adjuvant': adjuvants,
                       'betaNA': betaNA_list, 'betaHA': betaHA_list,
                       'betaAb': betaAb_list}
#best_fit_params_adj = {'adjuvant': adjuvants,
#                       'betaNA': betaNA_list, 'betaHA': betaHA_list}
best_fit_params_adj = pd.DataFrame(best_fit_params_adj)
best_fit_params_adj.set_index(best_fit_params_adj['adjuvant'])
best_fit_params_adj.to_csv('../../params/best_fit_params_adj_Astar.csv')
