import networkx as nx


class Conductance:
    def __init__(self, graph):
        self.graph = graph.copy()
        self._graph_links = graph.number_of_edges()

    def _params2conductance(self, external_links, internal_links) -> float:
        if internal_links > self._graph_links/2:
            internal_links = self._graph_links - internal_links
        if internal_links == 0 or external_links == 0:
            return 1#float('inf')
        return external_links / internal_links

    def conductance(self, ranks):
        external_links = 0
        internal_links = 0
        for i, j in self.graph.edges():
            external_links += ranks.get(i, 0)*(1-ranks.get(j, 0)) + (1-ranks.get(i, 0))*ranks.get(j, 0)
            internal_links += ranks.get(i, 0)*ranks.get(j, 0)
        return self._params2conductance(external_links, internal_links)

    def sweep(self, ranks):
        best_conductance = float('inf')
        external_links = 0
        internal_links = 0
        prev = set()
        best_set = set()
        for v in sorted(ranks, key=ranks.get, reverse=True):
            for u in self.graph.neighbors(v):
                if u in prev:
                    external_links -= 1
                    internal_links += 1
                else:
                    external_links += 1
            prev.add(v)
            curr_cond = self._params2conductance(external_links, internal_links)
            if curr_cond<best_conductance:
                best_conductance = curr_cond
                best_set = prev.copy()
        # print("Minimum conductance", best_conductance)
        return best_set
