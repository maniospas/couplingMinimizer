
def _params2conductance(nom, external_links, internal_links):
    if nom>internal_links/2:
        external_links = internal_links - external_links
    if external_links==0 or nom==0:
        return float('inf')
    return nom / external_links


def conductance(ranks, g):
    external_links = 0
    internal_links = 0
    for i, j in g.edges():
        external_links += ranks.get(i, 0)*(1-ranks.get(j, 0)) + (1-ranks.get(i, 0))*ranks.get(j, 0)
        internal_links += ranks.get(i, 0)*ranks.get(j, 0)
    return _params2conductance(external_links, internal_links, g.number_of_edges())


def sweep(ranks, g):
    best_conductance = float('inf')
    external_links = 0
    internal_links = 0
    prev = set()
    best_set = set()
    for v in sorted(ranks, key=ranks.get, reverse=True):
        for u in set().union(g.successors(v), g.predecessors(v)):
            if u in prev:
                external_links -= 1
                internal_links += 1
            else:
                external_links += 1
        prev.add(v)
        curr_cond = _params2conductance(external_links, internal_links, g.number_of_edges())
        if curr_cond<best_conductance:
            best_conductance = curr_cond
            best_set = set(prev)
    return best_conductance, best_set
