from os import path
import networkx as nx
import pandas as pd
from pyvis.network import Network

SCRIPT_DIR = path.dirname(__file__)
file_path = path.join(SCRIPT_DIR, "data", "final_edges.json")
    
graph_df = pd.read_json(file_path)

print(graph_df)

G = nx.from_pandas_edgelist(graph_df, source='source', target='target')

nx.write_gexf(G, "visualisations/network_viz/cleaned_graph_final.gexf")
net = Network(notebook=True)
#net.from_nx(G)
#net.show("visualisations/network_viz/git_repos_long.html")