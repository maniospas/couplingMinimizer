import networkx as nx
import visualize.visualizer as vis
import graph_generation
import conductance


# create graph
G, modules = graph_generation.create_pyan_graph("./experimentOn/TheAlgorithms-master", content="name")

# weight edges for a symmetrically normalized Laplacian formulation (best personalized PageRank setup
for (u, v, d) in G.edges(data=True):
    d["weight"] = (G.in_degree(u)+G.out_degree(u))**(-0.5)*(G.in_degree(v)+G.out_degree(v))**(-0.5)

# run the personalized PageRank using the module's nodes to construct the seed vector
module = modules[list(modules.keys())[1]]
print(list(module))
print(module)
seed_vector = {u: 1 if u in module else 0 for u in G.nodes()}
ranks = nx.pagerank(G, alpha=0.85, personalization=seed_vector, weight="weight")
# calculate the minimum conductance
unpersonalized_ranks = nx.pagerank(G, alpha=0.85, weight="weight")
ranks = {u: ranks[u]/unpersonalized_ranks[u] if unpersonalized_ranks[u]!=0 else 0 for u in G.nodes()}
print(len({u: ranks[u] for u in ranks.keys() if ranks[u]!=1}))
best_cond, best_set = conductance.sweep(ranks, G)

print("Original conductance",conductance.conductance(seed_vector, G))
print("New conductance", conductance.conductance({u: 1 if u in best_set else 0 for u in G.nodes()}, G))

vis.visualize(G, ranks, {u: 1 if u in module else 0 for u in G.nodes()})