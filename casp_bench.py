import string

import caspailleur
import networkx as nx
import pandas as pd
from caspailleur import api, iter_proper_premises_via_keys, io, mine_equivalence_classes as mec, \
    implication_bases as impbas, list_keys
from bitarray import frozenbitarray, bitarray as fbarray, bitarray
from caspailleur.implication_bases import verify_proper_premise_via_keys
from typing import List, Dict, Tuple, Iterator, Iterable
from bitarray.util import subset
from IPython.display import Image
from graphviz import Digraph
import re


def get_bodies_of_water_example():
    l_df = caspailleur.io.from_fca_repo('bodiesofwater_en')

    l_df['temporary'] = [False, False, False, False, False, True, False, False, False, False, False,
                       False, False, False, False, False, False, ]

    return l_df


def text_to_binary(text):
    binary_result = ''.join(format(ord(char), '08b') for char in text)
    return binary_result


# Definieren aller möglichen Attribute
attributes = ['cartoon', 'mammal', 'cat', 'dog', 'real', 'tortoise']
mapping = {attr: i for i, attr in enumerate(attributes)}


# Funktion zur Konvertierung eines Intent-Sets in ein frozenbitarray
def intent_to_bitarray(intent, mapping, size):
    bitarr = bitarray(size)
    bitarr.setall(0)
    for attr in intent:
        bitarr[mapping[attr]] = 1
    return frozenbitarray(bitarr)

# Intents als Mengen
intents = [
    {'cartoon', 'mammal', 'cat'},
    {'cartoon', 'dog', 'mammal'},
    {'cat', 'real', 'mammal'},
    {'dog', 'real', 'mammal'},
    {'real', 'tortoise'}
]


# Konvertieren der Intents in frozenbitarray
bitarrays = [intent_to_bitarray(intent, mapping, len(attributes)) for intent in intents]

# Beispiel keys_to_intents Wörterbuch
keys_to_intents = {
    frozenbitarray('111000'): 0,
    frozenbitarray('110100'): 1
}

# Überprüfen und Ergänzen fehlender Schlüssel
for i, intent in enumerate(bitarrays):
    if intent not in keys_to_intents:
        keys_to_intents[intent] = i

# Aufruf der Funktion
proper_premises = iter_proper_premises_via_keys(bitarrays, keys_to_intents, all_frequent_keys_provided=True)


def verify_proper_premise_via_keys_niklas(
        key: fbarray, intent_idx: int, i_intents: List[fbarray], other_keys: Dict[fbarray, int],
        all_frequent_keys_provided: bool = True
) -> bool:
    """Test if `key` is a proper premise given dict of keys of smaller size

    Parameters
    ----------
    key: frozenbitarray
        A key (bitarray) to test
    intent_idx: int
        Index of the intent which is closure of `key`
    i_intents: List[frozenbitarray]
        List of bitarrays representing intents (i.e. closed subset of attributes)
    other_keys: Dict[frozenbitarray, int]
        Dictionary containing all keys of smaller sizes and intents, corresponding to them.
        Passing dictionary of keys of size = size(key) - 1 is enough for algorithm to work.
    all_frequent_keys_provided: bool
        a flag, whether `keys_to_intents` dictionary contains all the keys of all intents.
        If some keys/intents are missing, set the flag to False:
        it will slow down the computations, but will keep them correct.

    Returns
    -------
    flg: bool
        A flag, whether `key` is a proper premise

    Size of key -- size(key) -- is the number of True values in it (i.e. key.count() if key is a bitarray).
    """

    print("Drin!")

    intent = i_intents[intent_idx]

    if key == intent:
        print(1)
        return False

    if key.count() == 0:
        print(2)
        return True

    if all_frequent_keys_provided:
        subkeys = []
        for m in key.search(True):
            subkey = bitarray(key)
            subkey[m] = False
            subkeys.append(fbarray(subkey))
    else:
        subkeys = (other for other in other_keys if subset(other, key) and other != key)

    pseudo_closed_key = bitarray(key)
    for subkey in subkeys:
        pseudo_closed_key |= i_intents[other_keys[subkey]]
        if pseudo_closed_key == intent:
            return False
    print(True)
    return True


def iter_proper_premises_via_keys_niklas(
        intents: List[fbarray], keys_to_intents: Dict[fbarray, int],
        all_frequent_keys_provided: bool = True
) -> Iterator[Tuple[fbarray, int]]:
    """Obtain the set of proper premises given intents, intents parents relation, and keys

    Parameters
    ----------
    intents: List[frozenbitarray]
        list of closed descriptions (in the form of bitarrays)
    keys_to_intents: Dict[frozenbitarray, int]
        the dictionary of keys in the context and the indices of the corresponding intents
    all_frequent_keys_provided: bool
        a flag, whether `keys_to_intents` dictionary contains all the keys of all intents.
        If some keys/intents are missing, set the flag to False:
        it will slow down the computations, but will keep them correct.

    Returns
    -------
    proper_premises: Iterator[Tuple[frozenbitarray, int]]
        Iterator with found proper premises

    """
    return (
        (key, intent_idx) for key, intent_idx in keys_to_intents.items()
        if verify_proper_premise_via_keys_niklas(key, intent_idx, intents, keys_to_intents, all_frequent_keys_provided)
    )


def print_premise():
    iter_proper_premises_via_keys_niklas(bitarrays, keys_to_intents, all_frequent_keys_provided=True)


def byte_to_text(binary_str):
    # Split the binary string into chunks of 8 bits (1 byte)
    n = 8
    binary_chunks = [binary_str[i:i + n] for i in range(0, len(binary_str), n)]

    # Convert each binary chunk to a decimal (ASCII) and then to a character
    text = ''.join(chr(int(chunk, 2)) for chunk in binary_chunks)

    return text


def binary_to_text(binary_bytes):
    # Wandelt eine Liste von Bytes (als binäre Zeichenketten) in Text um
    text = ''.join(chr(int(byte, 2)) for byte in binary_bytes)
    return text


def test_list_proper_premises_via_keys():
    n_attrs = 5
    intents = [set(), {0}, {2}, {3}, {0, 2}, {0, 3}, {1, 2}, {1, 2, 3}, {0, 1, 2, 3, 4}]

    # Konvertiert die Liste der Intents zu bitarrays
    intents = list(io.isets2bas(intents, n_attrs))

    # Creates a Dict {frozenbitarray, int}, a key gets added to the frozenbitarrays
    keys_to_intents = mec.list_keys(intents)

    pprems_true = list(io.isets2bas([{1}, {4}, {2, 3}, {0, 1}, {0, 2, 3}], 5))

    pprems = dict(impbas.iter_proper_premises_via_keys(intents, keys_to_intents))

    print(intents)


# Definiere alle möglichen Attribute
attributes = [0, 1, 2, 3, 4, 5]  # Passe diese Liste an deine Anforderungen an
mapping = {attr: i for i, attr in enumerate(attributes)}


def set_to_bitarray(attr_set, i_mapping, size):
    bitarr = bitarray(size)
    bitarr.setall(0)
    for attr in attr_set:
        bitarr[i_mapping[attr]] = 1
    return frozenbitarray(bitarr)


# Intents als Sets
intents = [{0, 4, 5}, {0, 3, 5}, {1, 4, 5}, {1, 3, 5}, {1, 2}]

# Konvertiere die Sets zu frozenbitarray
bitarrays = [set_to_bitarray(intent, mapping, len(attributes)) for intent in intents]

# Sortiere die bitarrays in aufsteigender Reihenfolge basierend auf der Anzahl der True-Werte
sorted_bitarrays = sorted(bitarrays, key=lambda ba: (ba.count(), ba.to01()))


def niklas_proper_premises():
    """
    Get the premises of the 'Famous Animals' dataset.

    Die Liste mit bitarray-intents muss topologisch aufsteigend sortiert sein.
    """
    n_attrs = 6  # Anzahl der Attribute
    intents_int = [{0, 4, 5}, {0, 3, 5}, {1, 4, 5}, {1, 3, 5}, {1, 2}]  # Liste der Intent-Sets
    intents_bitarray = list(map(lambda x: set_to_bitarray(x, mapping, n_attrs), intents_int))
    print(intents_bitarray)
    i_sorted_bitarrays = sorted(intents_bitarray, key=lambda ba: (ba.count(), ba.to01()))
    keys_to_intents_dict = list_keys(i_sorted_bitarrays)
    r_proper_premises = dict(iter_proper_premises_via_keys(intents_bitarray, keys_to_intents_dict))
    print(r_proper_premises)


#-------------------------------------------------------------------------------------------------#


df = get_bodies_of_water_example()

concepts_df = caspailleur.mine_concepts(df, min_support=0)

node_labels = concepts_df['intent'].map(', '.join) + '<br><br>' + concepts_df['extent'].map(', '.join)

diagram_code = caspailleur.io.to_mermaid_diagram(node_labels, concepts_df['previous_concepts'])

#print(diagram_code)


def lists_to_mermaid(nodes, edges):
    # Anfang des Diagramm-Strings
    diagram_code = "flowchart TD\n"

    # Knoten hinzufügen
    for node, attrs in nodes:
        diagram_code += f'{node}["{attrs}"];\n'

    # Kanten hinzufügen
    for start, end in edges:
        diagram_code += f'{start} --- {end};\n'

    return diagram_code


def parse_mermaid(data):
    nodes = re.findall(r'([A-Z])\["(.*?)"\]', data)
    edges = re.findall(r'([A-Z]) --- ([A-Z]);', data)
    return nodes, edges


def build_graph(nodes, edges):
    G = nx.DiGraph()
    for node, attrs in nodes:
        G.add_node(node, label=attrs)
    for start, end in edges:
        G.add_edge(start, end)
    return G


def update_labels_for_objects(G):
    updated_labels = {}
    seen_objects = set()

    # Topologisch sortieren und in umgekehrter Reihenfolge durchlaufen
    sorted_nodes = list(nx.topological_sort(G))

    for node in reversed(sorted_nodes):
        if node in ['A', 'M']:
            continue
        label = G.nodes[node]['label']
        split_label = label.split('<br><br>')
        objects = set(split_label[1].split(', ')) if len(split_label) > 1 else set()

        objects_to_display = objects - seen_objects
        seen_objects.update(objects_to_display)

        updated_labels[node] = '<br><br>' + ', '.join(objects_to_display)

    return updated_labels


def update_labels_for_attributes(G):
    updated_labels = {}
    seen_attributes = set()

    # Topologisch sortieren und von den Wurzeln zu den Blättern durchlaufen
    sorted_nodes = list(nx.topological_sort(G))

    for node in sorted_nodes:
        if node in ['A', 'M']:
            continue
        label = G.nodes[node]['label']
        split_label = label.split('<br><br>')
        attributes = set(split_label[0].split(', ')) if split_label[0] else set()

        attributes_to_display = attributes - seen_attributes
        seen_attributes.update(attributes_to_display)

        if node in updated_labels:
            updated_labels[node] = ', '.join(attributes_to_display) + updated_labels[node]
        else:
            updated_labels[node] = ', '.join(attributes_to_display) + '<br><br>'

    return updated_labels


def generate_mermaid(nodes, edges, updated_labels):
    diagram_code = "flowchart TD\n"
    for node in nodes:
        node_id = node[0]
        if node_id in ['A', 'M']:
            diagram_code += f'{node_id}["{node[1]}"];\n'
        elif updated_labels[node_id].strip("<br><br>") != '':  # Überprüfen, ob das Label nicht leer ist
            diagram_code += f'{node_id}["{updated_labels[node_id]}"];\n'
    for start, end in edges:
        diagram_code += f'{start} --- {end};\n'
    return diagram_code


def simple_mermaid_concept_lattice(i_diagram_code):
    # Extrahiere die Knoten
    nodes = re.findall(r'([A-Z])\["(.*?)"\]', i_diagram_code)

    # Extrahiere die Kanten
    edges = re.findall(r'([A-Z]) --- ([A-Z]);', i_diagram_code)

    # Liste von Knoten und Kanten
    nodes_list = [(node, attrs) for node, attrs in nodes]
    edges_list = [(start, end) for start, end in edges]

    # Erste Node leeren.
    nodes_list[0] = ['A', 'Start']

    # Letzte Node leeren
    nodes_list[-1] = [string.ascii_uppercase[len(nodes_list)-1], 'Ende']

    l_diagram_code = lists_to_mermaid(nodes_list, edges_list)

    nodes, edges = parse_mermaid(l_diagram_code)
    G = build_graph(nodes, edges)
    updated_labels_attributes = update_labels_for_attributes(G)
    updated_labels_objects = update_labels_for_objects(G)

    # Merge the two updated label dictionaries
    updated_labels = {node: updated_labels_attributes.get(node, '') + updated_labels_objects.get(node, '') for node in
                      G.nodes if node not in ['A', 'M']}

    new_mermaid = generate_mermaid(nodes, edges, updated_labels)

    print("Generated Mermaid Diagram Code:\n", new_mermaid)


simple_mermaid_concept_lattice(diagram_code)
