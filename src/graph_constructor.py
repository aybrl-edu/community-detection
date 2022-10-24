from os import path
import networkx as nx
import pandas as pd
from pyvis.network import Network

SCRIPT_DIR = path.dirname(__file__)
file_path = path.join(SCRIPT_DIR, "data", "edges_data_long.json")
    
graph_df = pd.read_json(file_path)

G = nx.from_pandas_edgelist(graph_df, source='source', target='target')

nx.write_gexf(G, "git_repos_long.gexf")
# net = Network(notebook=True)
# net.from_nx(G)
# net.show("git_repos_long.html")