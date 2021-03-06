import networkx as nx
from pyan.analyzer import Flavor
from pyan.analyzer import CallGraphVisitor


def _path2files(path):
    import os
    from glob import glob
    filenames = list()
    pattern   = "*.py"
    for found_dir,_,_ in os.walk(path):
        filenames.extend(glob(os.path.join(found_dir,pattern)))
    print("Found",len(filenames),"files")
    return filenames


def _converter(content="default"):
    if content == "default":
        return lambda node: [str(node)]
    elif content == "trace":
        return lambda node: [node.get_name()]
    elif content == "predicates":
        return lambda node: node.get_name().split(".")
    elif content == "name":
        return lambda node: [node.name]
    else:
        raise Exception("Invalid converter content")


def create_test_graph():
    G = nx.DiGraph()
    G.add_node("A")
    G.add_node("B")
    G.add_node("C")
    G.add_node("D")
    G.add_node("E")
    G.add_node("F")
    G.add_node("G")
    G.add_node("H")
    G.add_node("I")
    G.add_node("J")
    G.add_node("K")
    G.add_edge("A", "B")
    G.add_edge("B", "C")
    G.add_edge("C", "D")
    G.add_edge("D", "E")
    G.add_edge("E", "F")
    G.add_edge("F", "G")
    G.add_edge("G", "H")
    G.add_edge("H", "I")
    G.add_edge("I", "J")
    G.add_edge("J", "K")
    G.add_edge("A", "D")
    G.add_edge("B", "D")
    G.add_edge("B", "E")
    G.add_edge("E", "G")
    G.add_edge("G", "J")
    G.add_edge("G", "I")
    G.add_edge("H", "J")
    G.add_edge("I", "K")

    modules = {"module1": ["A", "B", "C", "D", "E", "F", "G"], "module2": ["H", "I", "J", "K"]} # G should be in module2
    return G, modules


def _is_of_interest(node):
    return not node.flavor==Flavor.CLASS and not node.flavor==Flavor.MODULE


def create_pyan_graph(path, keep_undefined=False, content="default"):
    converter = _converter(content)

    visitor = CallGraphVisitor(_path2files(path))
    visited_nodes = [node for name in visitor.nodes for node in visitor.nodes[name] if node.defined or keep_undefined]
    #visited_nodes.sort(key=lambda x: (x.namespace, x.name))
    print("Found",len(visited_nodes),"entities")
    G = nx.DiGraph()
    modules = {}
    for node in visited_nodes:
        """
        if node in visitor.defines_edges:
            for called in visitor.defines_edges[node]:
                if called.defined or keep_undefined:
                    for cnode in converter(node):
                        for ccalled in converter(called):
                            G.add_node(cnode)
                            G.add_node(ccalled)
                            G.add_edge(cnode, ccalled)
                            """
        if node in visitor.uses_edges and _is_of_interest(node):
            for called in visitor.uses_edges[node]:
                if (called.defined or keep_undefined) and _is_of_interest(node):
                    for cnode in converter(node):
                        for ccalled in converter(called):
                            G.add_node(cnode)
                            G.add_node(ccalled)
                            G.add_edge(cnode, ccalled)

    modules = {}
    for node in visited_nodes:
        module_name = node.get_namespace_label()
        G.add_node(module_name)
        if _is_of_interest(node) and module_name is not None and module_name!='':
            for ccalled in converter(node):
                G.add_node(ccalled)
                if module_name not in modules:
                    modules[module_name] = [module_name]
                modules[module_name].append(ccalled)
                G.add_edge(module_name, ccalled)
    """
    for node in modules.keys():
        for cnode in converter(node):
            G.add_node(cnode)
        for called in modules[node]:
            if G.has_node(called):
                for cnode in converter(node):
                    G.add_edge(cnode, called)
                    """
    return G, modules


def _create_graph(pairs):
    print('----- Constructing Network -----')
    G = nx.DiGraph()
    for node1, node2 in pairs:
        if not G.has_node(node1):
            G.add_node(node1)
        if not G.has_node(node2):
            G.add_node(node2)
        G.add_edge(node1, node2)
    print('Avg. Degree: ',sum(G.degree[v] for v in G.nodes())/len(G.nodes()))
    return G


def create_predicate_graph(path):
    import astor
    import ast
    import re
    
    def _get_function_words(node):
        words = list()
        for line in astor.to_source(node).split('\n'):
            line_text = re.sub(r"\(|\)|\:|\.|\_|\[|\]|\"|\'|\||\\|\{|\}|\=|\+|\-|\*|\/|\%|\.|\,|\<|\>", " ", line)
            words.extend([word for word in line_text.split(' ') if len(word)>1])
            #words.extend(word.lower() for word in re.findall("[A-Z]*[a-z]+", line))
        return words
    
    pairs = list()
    function_names = list()
    frequencies = {}
    for path in _path2files(path):
        a = astor.code_to_ast.parse_file(path)
        for node in ast.iter_child_nodes(a):
            if type(node).__name__ == 'ClassDef':
                for method in ast.iter_child_nodes(node):
                    pairs.append((node.name, method.name))
                    function_names.append(node.name)
                    method_name = method.name
                    frequencies[method_name] = frequencies.get(method_name,0) + 1
                    if type(method).__name__ == 'FunctionDef':
                        function_names.append(method_name)
                        for word in _get_function_words(method):
                            pairs.append((method_name, word))
                            frequencies[word] = frequencies.get(word,0) + 1
            if type(node).__name__ == 'FunctionDef':
                pairs.append((path.split('\\')[-2].split('.')[-1], node.name))
                function_names.append(path.split('\\')[-2].split('.')[-1])
                function_names.append(node.name)
                frequencies[node.name] = frequencies.get(node.name,0) + 1
                for word in _get_function_words(node):
                    pairs.append((node.name, word))
                    frequencies[word] = frequencies.get(word,0) + 1
    pairs = [(node1, node2) for node1, node2 in pairs if node1!=node2 and (frequencies[node2]>1 or node2 in function_names) ]
    G = _create_graph(pairs)
    return G