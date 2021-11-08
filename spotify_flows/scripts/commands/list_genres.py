import pickle
import difflib


def list_genres(matches: str = None, contains: str = None):

    # 1. Unpickle the graph
    with open("data/genre_graph.p", "rb") as f:
        genre_graph = pickle.load(f)

    all_genres = list(genre_graph.nodes())

    def similarity(a, b):
        return difflib.SequenceMatcher(a=a, b=b).ratio()

    if matches:
        genres_to_print = [
            genre for genre in all_genres if similarity(genre, matches) > 0.5
        ]

    elif contains:
        genres_to_print = [genre for genre in all_genres if contains in genre]

    else:
        genres_to_print = all_genres

    for node in genres_to_print:
        print(node)
