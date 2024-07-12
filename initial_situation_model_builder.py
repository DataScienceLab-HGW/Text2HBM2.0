from nltk.corpus import wordnet as wn
import networkx as nx
from graphviz import Digraph as DG

import matplotlib.pyplot as plt
import itertools
import subprocess as subproc
from typing import List


from domain_knowledge_utils import handle_multi_word_instance_text

def closure_graph(synset, fn):
    seen = set()
    graph = nx.DiGraph()

    def recurse(s):
        if not s in seen:
            seen.add(s)
            graph.add_node(s._lemma_names[0])
            for s1 in fn(s):
                graph.add_node(s1._lemma_names[0])
                graph.add_edge(s._lemma_names[0], s1._lemma_names[0])
                recurse(s1)

    recurse(synset)
    return graph

def build_graph_least_common_hypernym_of_each_pair_of_words(words):

    synsets_of_words = [wn.synsets(word)[0] for word in words]

    lowest_common_hypernyms_pairwise = []
    pair_order_list = list(itertools.combinations(synsets_of_words,2))

    graph = nx.DiGraph()
    for pair in pair_order_list:
        lowest_common_hypernym = pair[0].lowest_common_hypernyms(pair[1])[0]._lemma_names[0]
        lowest_common_hypernyms_pairwise.append((pair[0]._lemma_names[0],pair[1]._lemma_names[0],lowest_common_hypernym))
        graph.add_node(pair[0]._lemma_names[0])
        graph.add_node(pair[1]._lemma_names[0])
        graph.add_edge(pair[0]._lemma_names[0],lowest_common_hypernym)
        graph.add_edge(pair[1]._lemma_names[0], lowest_common_hypernym)

    return graph

def create_hypernym_graph_for_a_word(word):

    hypernym_start = wn.synsets(word)[0]
    hypernym_graph = closure_graph(hypernym_start, lambda s: s.hypernyms())
    return hypernym_graph

def create_hypernym_graph_for_a_word_2(word, graph, depth):

    if(depth==0):
        hypernyms = wn.synsets(word)[0].hypernyms()
    else:
        hypernyms = word.hypernyms()
    
    if len(hypernyms) == 0:
       return graph

    else:
        hypernym_lemma = hypernyms[0]._lemma_names[0]
        hypernym = hypernyms[0]
        if graph is None:
            #graph = DigraphWrapper(comment="Situation model_1", strict=True)
            graph = nx.DiGraph()

        if depth<1:
            graph.add_edge(word, hypernym_lemma)
        else:
            graph.add_edge(word._lemma_names[0], hypernym_lemma)
        depth = depth + 1 

        return create_hypernym_graph_for_a_word_2(hypernym, graph, depth)

def create_hypernym_graph_for_a_word_wn_subproc(word):

    command =["wn",
               "\'" + word +"\'" ,
               "-hypen"]

    command_str = " ".join(command)

    wn_process = subproc.Popen(command_str, shell=True, stdout=subproc.PIPE)
    wn_output = wn_process.stdout.read().decode("utf-8")

    wn_output_2 = wn_output
    #RELEVANT TODO 20.03->get_word_senses_hierarchy(wn_output_2)
    # tale the word senses and then extract the words , convert to BERT vectors and calculate cosine dist.
    ##

    wn_output = wn_output.split("\n")
    hypernyms_output = wn_output[7:]#7 whitespaces to first first tree

    hierarchy = [word]
    #check if hypernyms exist at all
    #if no hypernyms exist, connect directly to "entity"
    if len(hypernyms_output) == 0:
        hierarchy.append("entity")
    else:

        for hypernym in hypernyms_output:
            hyp = hypernym.split("=> ")[1]
            hyp = hyp.split(", ")[0]
            hierarchy.append(hyp)
            if hyp == "entity":
               break

    graph = nx.DiGraph()
    [graph.add_edge(x,y) for x,y in zip(hierarchy[:-1], hierarchy[1:])]

    return graph

def remove_node(g, node):
    if g.is_directed():
        sources = [source for source, _ in g.in_edges(node)]
        targets = [target for _, target in g.out_edges(node)]
    else:
        sources = g.neighbors(node)
        targets = g.neighbors(node)

    new_edges = itertools.product(sources, targets)
    new_edges = [(source, target) for source, target in new_edges if source != target] # remove self-loops
    g.add_edges_from(new_edges)

    g.remove_node(node)

    return g
    
def prune_graph_removing_intemediate_hypernyms_with_one_parent_or_one_child(graph, initial_words):
    #initial words (the objects) should not be pruned
    nodes = list(graph.nodes)
    edges = list(graph.edges)

    # remove the initial words from the nodes list
    # for each node count the number of incoming edges and the outcoming edges
    nodes_to_prune = [node for node in nodes if node not in initial_words]
    
    nodes_to_remove = []
    for node in nodes_to_prune:

        times_node_as_source =  0
        times_node_as_target = 0

        for edge in edges:
            source = edge[0]
            target = edge[1]
            if source == node:
                times_node_as_source = times_node_as_source + 1
            if target == node:
                times_node_as_target = times_node_as_target + 1
            
        if times_node_as_source == 1 and times_node_as_target <= 1:
           nodes_to_remove.append(node)

    for node in nodes_to_remove:
        new_graph = remove_node(graph, node)
    
    edges = list(new_graph.edges)
    for edge in edges:
        new_graph.add_edge(edge[0],edge[1],label="isa")
    
    return new_graph

def count_number_of_whitespaces_at_beginning(word):

    count_whitespaces = sum( 1 for _ in itertools.takewhile(str.isspace, word) )
    return count_whitespaces

def build_initial_hypernym_graph(input_words):
    '''
    Parts of this function are similar to build_initial_situation_model(), however
    here we create only the hypernyms graph

    The hypernyms hierarchy will be then used to extract the
    :types in the pddl domain description

    returns a networkx graph object
    '''

    graphs = [create_hypernym_graph_for_a_word_wn_subproc(word) for word in input_words]
    hypernymG = nx.compose_all(graphs)

    #the commando below makes the graph look better (with fill, etc)
    #graph_with_hypernyms = transform_graph_to_graphviz(graph_with_hypernyms, input_words)

    return hypernymG

def build_initial_hypernym_graph_with_domain_knowledge(input_words:list = None, types_instances:dict = None, types_hierarchy:list = None,  graph_export_path:str = None):
    #create a graph visualizing the domain knowledge provided by the user (domain expert)
    #after creating the knowledge graph, merge it with the other graph as created by the 
    #wordnet ontology using the known types as additional input words.
    known_instances = []
    for _, instances in types_instances.items():
        known_instances.extend(list(map(lambda x: handle_multi_word_instance_text(x.txt), instances )))


    graph_domain_knowledge = build_known_types_instances_graph(types_instances, types_hierarchy)
    #nx.drawing.nx_pydot.write_dot(graph_domain_knowledge, graph_export_path)

    # we want to find wordnet hypernyms of words which have an out_degree of 0 (leaf nodes)
    # The node out degree is the number of edges pointing out of the node.
    types_as_wordnet_inputs = []
    for node_name, out_degree in graph_domain_knowledge.out_degree:
        if(out_degree == 0):
            types_as_wordnet_inputs.append(node_name)

    # we remove the words from the input words which have already been stored in a hypernym graph 
    input_words = [in_word for in_word in input_words if in_word not in known_instances ]
    input_words.extend(types_as_wordnet_inputs)

    graphs = [create_hypernym_graph_for_a_word_wn_subproc(word) for word in input_words]
    graphs.append(graph_domain_knowledge)

    hypernymG = nx.compose_all(graphs)

    if graph_export_path:

        nx.drawing.nx_pydot.write_dot(hypernymG, graph_export_path) 

    #the commando below makes the graph look better (with fill, etc)
    #graph_with_hypernyms = transform_graph_to_graphviz(graph_with_hypernyms, input_words)

    return hypernymG

def build_known_types_instances_graph(types_instances:dict, types_hierarchy: List[List]):
    # types_hierarchy is a list of lists, where each sublist represents a hierarchy
    # we iterate over the sublists and create a graph fo each sublist

    types = [] # initialize an array to save only the types which will be later used to find wordnet hypernyms
    #the types which have not been user defined in the types_hierarchy will be directly used to find hypernyms

    types_instances_graphs = []
    for type, instances in types_instances.items():
        type_gr =  nx.DiGraph()
        for instance in instances:
            type_gr.add_edge(handle_multi_word_instance_text(instance.txt), type)
            types.append(type)
        types_instances_graphs.append(type_gr)

    sub_graphs_type_hierarchy = []

    for sub_hierarchy in types_hierarchy:
        graph_type_sub_hieararchy = nx.DiGraph()
        [graph_type_sub_hieararchy.add_edge(x,y) for y,x in zip(sub_hierarchy[:-1], sub_hierarchy[1:])]
        sub_graphs_type_hierarchy.append(graph_type_sub_hieararchy)
    
    graph_types_hierarchy = nx.compose_all(sub_graphs_type_hierarchy)
    graph_type_hierarchy_and_instances = nx.compose_all(types_instances_graphs)

    graph_all = nx.compose(graph_types_hierarchy, graph_type_hierarchy_and_instances)

    return(graph_all)

def build_initial_situation_model(input_words):

    graphs = [create_hypernym_graph_for_a_word_wn_subproc(word) for word in input_words]

    G = nx.compose_all(graphs)

    final_graph = prune_graph_removing_intemediate_hypernyms_with_one_parent_or_one_child(G, input_words)

    for node in final_graph.nodes(data=True):
        #add some color to the hyperonyms-nodes
        if node[0] in input_words:
           node[1]["color"]="grey"
           node[1]["style"] = "filled"

    return final_graph

def build_initial_situation_model_with_intermediate_hypernym(input_words:list, hypernym_graph:nx.Graph):
    #get the successorts of the input words (these will be the direct hypernyms)
    direct_hypernyms = [list(hypernym_graph.successors(word))[0] for word in input_words]

    # we don't prune the nouns for which we found the hypernyms and also we don't prune the first hypernym
    nodes_not_to_prune = direct_hypernyms + input_words

    final_graph = prune_graph_removing_intemediate_hypernyms_with_one_parent_or_one_child(hypernym_graph, nodes_not_to_prune)

    for node in final_graph.nodes(data=True):
        #add some color to the hyperonyms-nodes
        if node[0] in input_words:
           node[1]["color"]="grey"
           node[1]["style"] = "filled"

    return final_graph

def unite_graphs(nx_graph_1, nx_graph_2):
    return nx.compose(nx_graph_1, nx_graph_2)

def convert_causal_relations_objects_list_to_dicts(causal_rels_containing_objects):
    '''
    returns a list of dicts of type {'cause':'take','effect':'put'
    '''
    list_of_cause_effect_dicts=[]
    
    for rel in causal_rels_containing_objects:
        cause = rel.get("cause").verb
        effect = rel.get("effect").verb
        rel_d = {"cause":cause, "effect": effect}
        list_of_cause_effect_dicts.append(rel_d)

    return list_of_cause_effect_dicts

def add_causal_rels_to_model(model:nx.Graph, caus_rels_dicts)-> nx.Graph:
    '''
    caus_rels_dict is of type: {'cause':'take','effect':'put','lag':1,'p_val':0.05}
    '''
    for caus_rel_dict in caus_rels_dicts:
        source_node = caus_rel_dict.get('cause')
        target_node = caus_rel_dict.get('effect')
        model.add_edge(source_node, target_node, label="causes", color = "lightblue")

    return model

def add_actions_to_model(model:nx.Graph, actions)-> nx.Graph:
    
    for action in actions:
        model.add_node(action, color = "lightblue", style="filled" )

    return model

def add_properties_to_model(model:nx.Graph, properties)-> nx.Graph:
    
    for prop in properties:
        model.add_node(prop, color = "thistle", style="filled" )
    
    return model

#words = ["bottle","counter","board", "table", "knife","pot", "plate","water_tap","cupboard","sink","spoon","stove","soup","sponge","water","glass","carrots","minutes"]
#build_initial_situation_model(words, "./initial_situation_model_100", False)
#print("a")



#Added 02. Feb 2024
#TODO

# 
def get_word_senses_hierarchy(wordnet_output):
    senses = wordnet_output.split('Sense ')
    senses_hierarchy = {}
    for i, sense in enumerate(senses[1:], start=1):
        sense_hierarchy = []
        lines = sense.split('\n')
        for line in lines:
            if '=>' in line:
                words = [word.strip() for word in line.split('=>') if word.strip()]
                sense_hierarchy.append(words)
        senses_hierarchy[f"sense{i}"] = sense_hierarchy
    print(senses_hierarchy)


def get_word_senses_hierarchy_2(word, output):
    senses = output.split('Sense ')
    senses_hierarchy = {}
    for i, sense in enumerate(senses[1:], start=1):
        sense_hierarchy = []
        lines = sense.split('\n')
        current_level = sense_hierarchy
        for line in lines:
            if '=>' in line:
                words = [word.strip() for word in line.split('=>') if word.strip()]
                current_level.append(words)
                current_level = words
        senses_hierarchy[f"sense{i}"] = sense_hierarchy
    print(senses_hierarchy)