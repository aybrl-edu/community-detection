from os import path

import networkx as nx
import numpy as np
import pandas as pd

SCRIPT_DIR = path.dirname(__file__)


def load_network():
    file_path = path.join(SCRIPT_DIR, "data", "final_edges.json")

    graph_df = pd.read_json(file_path)

    return nx.from_pandas_edgelist(graph_df, source='source', target='target')


def detect_communities():
    network = load_network()
    exec_algo(network)


def exec_algo(network):
    print("Calculating edge betweenness centrality...")
    b_centrality = nx.edge_betweenness_centrality(network)

    count = 0
    while len(network.edges) > 0:
        max_bc = 0
        max_bc_edge = None

        print("Determining the edge with the highest B_C...")
        for edge in network.edges:
            if b_centrality[edge] > max_bc:
                max_bc = b_centrality[edge]
                max_bc_edge = edge

        print("Deleting the edge with the highest B_C...")
        network.remove_edge(*max_bc_edge)

        if count % 1000 == 0:
            # Coloring the communities
            color = random_color()
            for source, target in network.edges:
                if max_bc_edge[0] == source and max_bc_edge[1] == target:
                    color = random_color()
                network.nodes[f'{source}']['viz'] = {'color': {'r': color[0], 'g': color[1], 'b': color[2], 'a': 0}}

            print(f"Saving the network state after {count} iterations...")
            nx.write_gexf(network, f"visualisations/newman_iterations/communities_{count}_iterations.gexf")

        count = count + 1


def edge_betweenness_centrality():
    print('je;zs')


def random_color():
    return tuple(np.random.randint(256, size=3)) + (255,)
