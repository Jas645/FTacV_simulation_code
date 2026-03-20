import Surface_confined_inference as sci
import matplotlib.pyplot as plt
import numpy as np
plot_class=sci.BaseMultiExperiment.results_loader("/users/jas645/Cytochrome_ME/results_25-12-12_C6-OH_newprep_SWV_2")
get_params=plot_class._plot_manager._un_normalise_parameters()

#gets the scores
score_array=np.array([[x["scores"][y] for y in plot_class.grouping_keys] for x in plot_class._results_array])
get_params=plot_class._plot_manager._un_normalise_parameters()
#finds the best score for each technique (change the number next to the colon i.e. between 0 and 6)
best_5_ft_idx=np.argsort(score_array[:,0])[0]
print(dict(zip(plot_class._all_parameters, get_params[best_5_ft_idx, :])))
#plot the best index
plot_class.results(pareto_index=[best_5_ft_idx])
#Plot all of the "best scores"
plot_class.results(best="all")
#simulate specific parameters (have to be normalised)
#plot_class.results(parameters=sim_params)
#show the values of all the paramters in the pareto front
plot_class._plot_manager.pareto_parameter_plot(show_depths=False)
plt.show()
