import graph_utils
import visualize.visualizer as vis
import graph_generation
import module_ranker

# load graph
G, modules = graph_generation.create_test_graph()
#G, modules = graph_generation.create_pyan_graph("./experimentOn/TheAlgorithms2-master")
#G, modules = graph_generation.create_pyan_graph("C:\\Users\\manios\\Documents\\eclipse\\Python - CommunityDetection")

G = G.to_undirected()
conductance = graph_utils.Conductance(G)
ranker = module_ranker.Ranker(G)
ranks = {module_name: ranker.rank(module, normalize=False) for module_name, module in modules.items()}
print(ranks)

print("Original avg. conductance", sum(conductance.conductance(ranker.to_seed(module)) for module in modules.values())/len(modules))

new_modules = {module_name: [u for u in G.nodes() if max([m for m in modules.keys()], key=lambda m: ranks[m][u])==module_name] for module_name in modules.keys()}
print(new_modules)
print("New avg. conductance", sum(conductance.conductance(ranker.to_seed(module)) for module in new_modules.values())/len(modules))

print("----- Test Module -----")
module_name = list(modules.keys())[1]
print(modules[module_name])
#best_set = conductance.sweep(ranks[module_name])
print("Original conductance",conductance.conductance(ranker.to_seed(modules[module_name])))
print("New conductance", conductance.conductance(ranker.to_seed(new_modules[module_name])))
vis.visualize(G, ranker.to_seed(modules[module_name]), ranker.to_seed(new_modules[module_name]))


"""
Relevant works:
- Hill scanning: https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=7573823
"""