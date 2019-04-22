import networkx as nx


class Ranker:
    def __init__(self, graph):
        self.graph = graph.to_undirected()
        # weight edges for a symmetrically normalized Laplacian formulation (best personalized PageRank setup
        for (u, v, d) in graph.edges(data=True):
            d["weight"] = graph.degree(u) ** (-0.5) * graph.degree(v) ** (-0.5)
        self._unpersonalized_ranks = nx.pagerank(self.graph, alpha=0.85, weight="weight")

    def to_seed(self, module):
        return {u: 1.0 if u in module else 0 for u in self.graph.nodes()}

    def rank(self, module, normalize=False):
        ranks = nx.pagerank(self.graph, alpha=0.85, personalization=self.to_seed(module), weight="weight")
        ranks = {u: ranks[u] / self._unpersonalized_ranks[u] if self._unpersonalized_ranks[u] != 0 else 0 for u in self.graph.nodes()}
        if normalize:
            max_rank = max(ranks.values())
            ranks = {u: value/max_rank for u, value in ranks.items()}
        return ranks
