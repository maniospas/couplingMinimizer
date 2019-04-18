def visualize(g, ranks=None, highlighted=None):
    if ranks is None:
        ranks = {v: 0 for v in g.nodes()}
    if highlighted is None:
        highlighted = {v: 0 for v in g.nodes()}
    ranks_max = max(ranks.values())
    if ranks_max != 0:
        ranks = {v: ranks.get(v, 0)/ranks_max for v in g.nodes()}
    
    print('----- Visualizing -----')
    print('Packing data')
    data = dict()
    data['nodes'] = [{'id': str(u),'group': ranks[u]+highlighted[u]*1.00001} for u in g.nodes()]
    data['links'] = [{'source': str(node1), 'target': str(node2), 'value': 1} for node1, node2 in g.edges()]
    print('Writing to file')
    import json
    with open('visualize/data.json', 'w') as outfile:  
        json.dump(data, outfile)
    print("Running firefox")    # Chrome with default settings cannot loading external files from scripts
    import os
    os.system('start firefox.exe "file:///'+os.getcwd()+'/visualize/visualize.html"')


def visualize_clusters(clusters):
    print('----- Visualizing -----')
    print('Packing data')
    data = dict()
    data['name'] = ""
    data['children'] = [{"name": "", "children": [{"name": entity, "size": 3} for entity in cluster]} for cluster in clusters]
    import json
    with open('visualize/dataCluster.json', 'w') as outfile:
        json.dump(data, outfile)
    print("Running firefox")    # Chrome with default settings cannot loading external files from scripts
    import os
    os.system('start firefox.exe "file:///'+os.getcwd()+'/visualize/visualizeCluster.html"')
