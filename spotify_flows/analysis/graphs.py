# Standard library imports
from typing import List

# Third party imports
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# Local imports
import spotify_flows.spotify.collections as spocol

# Main body


def graph_recursion(artist_id, memo, rec=0):
    if artist_id in memo:
        return memo

    # Recursion
    related_artists = (
        spocol.Artist.from_id(artist_id).related_artists(5, include=False).collections
    )

    related_artists_ids = list(
        set([related_artist.id_ for related_artist in related_artists])
    )

    for related_artist_id in related_artists_ids:
        memo[artist_id] = related_artists_ids

        if rec < 5:
            graph_recursion(related_artist_id, memo, rec + 1)


def draw_graph(
    graph: nx.Graph,
    file_path: str,
    with_labels: bool = True,
    starting_nodes: List[str] = [],
    special_nodes: List[str] = [],
):

    pos = nx.spring_layout(
        graph, k=0.3 * 1 / np.sqrt(len(graph.nodes())), iterations=20
    )
    f = plt.figure(3, figsize=(60, 60))

    nx.draw_networkx_nodes(graph, pos, node_color="tab:blue")
    nx.draw_networkx_nodes(graph, pos, nodelist=starting_nodes, node_color="tab:green")
    nx.draw_networkx_nodes(graph, pos, nodelist=special_nodes, node_color="tab:red")
    nx.draw_networkx_edges(graph, pos, width=1.0, alpha=0.5)

    if with_labels:
        nx.draw_networkx_labels(graph, pos=pos)
    f.savefig(file_path)


def artist_popularity_weight_func(G, start_artist, u, v, d):
    node_v_wt = G.nodes[v].get("popularity", 1)
    node_u_wt = G.nodes[u].get("popularity", 1)

    if node_v_wt == 0:
        node_v_wt = 1
    if node_u_wt == 0:
        node_u_wt = 1

    pop_ratio = 2 * start_artist.popularity / (node_v_wt + node_u_wt)

    return pop_ratio
