import Surface_confined_inference as sci
import matplotlib.pyplot as plt
import numpy as np
import os
import csv

plot_class=sci.BaseMultiExperiment.results_loader("/users/jas645/Cytochrome_ME/results_25-12-12_C6-OH_newprep_SWV_2")
get_params=plot_class._plot_manager._un_normalise_parameters()
score_array=np.array([[x["scores"][y] for y in plot_class.grouping_keys] for x in plot_class._results_array])

best_5_ft_idx=np.argsort(score_array[:,1])[1]

best_dict=dict(zip(plot_class._all_parameters, get_params[best_5_ft_idx,:]))
for key in best_dict.keys():
 print("'{0}'".format(key), ":", best_dict[key], ",")

#values={
#'E0_std_1' : 0.07722660056375939 ,
#'E0_std_2' : 0.08 ,
#'E0_std_3' : 0.08 ,
#'gamma_1' : 1.9029782017136977e-11 ,
#'gamma_2' : 1e-11 ,
#'gamma_3' : 1e-11 ,
#'Cdl' : 9.414814150806344e-05 ,
#'Ru' : 533.0767111134156 ,
#'k0' : 97.46666388107144 ,
#'alpha' : 0.6 ,
#'E0_mean' : 0.15 ,
#}

values={
'E0_mean' : 0.11 ,
'Cdl' : 0.0002574556773010604 ,
'CdlE2' : 6.0274944935698335e-06 ,
'E0_std' : 0.031095751033080127 ,
'CdlE1' : 4.143885012988815e-06 ,
'Ru' : 6194.426662707727 ,
'k0' : 0.2591118686481044 ,
'gamma' : 3.258708475832017e-9 ,
'alpha' : 0.5 ,
}

import copy
extra_boundaries=copy.deepcopy(plot_class.boundaries)
for key in values.keys():
 if key not in extra_boundaries:
  for key2 in plot_class.boundaries.keys():
   if key2 in key:
    extra_boundaries[key]=plot_class.boundaries[key2]
print(extra_boundaries)
sim_params=[sci._utils.normalise(values[x], extra_boundaries[x]) for x in plot_class._all_parameters]
#plot_class.results(best="all")
plot_class.results(parameters=sim_params)
#plot_class._plot_manager.pareto_parameter_plot(show_depths=False)
plt.show()
