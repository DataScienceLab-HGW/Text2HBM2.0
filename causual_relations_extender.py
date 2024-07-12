'''
This script contains methods for the calculation of caulsality between 
words and phrases.
Please, note that it uses a modified version of the stattools grangercausality
'''

import itertools
import utils
from modified import grangercausality_stattools
import pandas as pd
import numpy as np
import copy
import networkx as nx
from collections import Counter
from relation import VbDobjRelationWithProperties, VbIndObjRelationWithProperties, VbNoobjRelation, VbDobjIndobjRelationWithProperties
import relationship_types as relationship_types


########################### graph methods

def create_graph_for_all_relations(list_of_dep_triples, deps_colors={'nmod':"orange", 'dobj':"blue", 'causes':"lightblue", 'property':"thistle" }):
    '''
    list of dependency triples: each triple looks like  ('nmod:from', ('take', 'VB', 0), ('counter', 'NN', 5))
    deps_colors: a dictionary with key = 'dep_name', value = 'color_name'
    output is a networkx graph with the relationships across all sentences
    '''
    G = nx.DiGraph()
    #edge_lbls = {}
    for dep in list_of_dep_triples:
        dep_head = dep[1][0]
        dep_tail = dep[2][0]
        dep_label = dep[0]
        if ":" in dep_label:
            dep_label_parts = dep_label.split(":")# remove the : from nmod:from - causes problems when converting to .dot
            dep_label_name = dep_label_parts[0]
            dep_label = dep_label_parts[1]
            dep_color = deps_colors.get(dep_label_name)
        else:
            dep_color = deps_colors.get(dep_label)
        if dep_label != "dobj":
           G.add_edge(dep_head, dep_tail, label = dep_label, color=dep_color)
        else:
           G.add_edge(dep_tail, dep_head, label = dep_label, color=dep_color) 
        #edge_lbls[(dep_head, dep_tail)] = dep_label

    return G

########################### creating vectors for different kinds of relations


def create_vector_representation_of_any_relationship(relationships_all_occurrences, relationships_sentencewise, return_objects = False):
    # returns a dictionary where the key is the relatinship and the value is the vector representation like [0,0,0,2...]
    # the number of components in the vector is the same as the number of n sentences and each component represents 
    # the number of occurrences of the relationship in the n-th sentence

    # takes a list of all rels of certain type which appear in the whole text and a list of sentwise appearances
    # and returns a vector which contains the corresponding number of occurrences in each of its components (similar to one-hot encoding, but instead of 
    # "ones" we have the count)
    # relationships_all_occurrences : a list (without repetitive elements) of all elements occuring in the whole text
    # relationships_sentencewise : here we have sentencewise the occurrences of 
    
    relation_count_vector_dict = {}

    for rel in relationships_all_occurrences:

        occur_vector = []
        for rel_sent in relationships_sentencewise:
            occur_vector.append(rel_sent.count(rel))
            rel_type = rel[0][0]
            if rel_type == relationship_types.DOBJ_RELATIONSHIP:
                rel_object = VbDobjRelationWithProperties(relation=rel[0], properties=rel[1])
            if rel_type == relationship_types.INDOBJ_RELATIONSHIP:
                rel_object = VbIndObjRelationWithProperties(relation=rel[0], preposition=rel[1], properties=rel[2])
            if rel_type == relationship_types.VBNOOBJ_RELATIONSHIP:
                rel_object = VbNoobjRelation(relation = rel[0])
            if rel_type == relationship_types.VB_DOBJ_INDOBJ_RELATIONSHIP:
                rel_object = VbDobjIndobjRelationWithProperties(relation = rel[0], preposition = rel[1], properties = rel[2])

        if return_objects:
            relation_count_vector_dict[rel_object] = occur_vector
        elif not return_objects:
            relation_count_vector_dict[rel_object.to_tuple()] = occur_vector
    
    return relation_count_vector_dict


########################### extraction methods

def extract_object_action_tuples(list_dep_words_and_ann_sentence_tokens):
    #generate dobj_time_series
    #generate VB time series

    # we are interested in the dobj relations and in the verbs
    dict_sentence_index_to_action_pair_count = {}
    #each key in the dic is the index of the sentence
    #each value is a dictionary ()
    
    for idx, annot_sent in enumerate(list_dep_words_and_ann_sentence_tokens):
        dobj_rels, _, _ = utils.filter_dobj_indobj_prop_relations([annot_sent])
        dobj_rels_no_caps = utils.remove_capitalization_in_dobj_or_indobj_rels(dobj_rels)
        dict_sentence_index_to_action_pair_count[idx] = dobj_rels

    return dict_sentence_index_to_action_pair_count

def create_dict_vectors_for_actions_dobj_relations(dobj_allsents, list_dep_words_and_ann_sentence_tokens):
    
    dobj_rels_in_sents = []
    
    for deps_in_sent in list_dep_words_and_ann_sentence_tokens:
        dobj_rels_in_sent, _, _ = utils.filter_dobj_indobj_prop_relations([deps_in_sent])
        dobj_rels_in_sent = utils.remove_capitalization_in_dobj_or_indobj_rels(dobj_rels_in_sent)
        dobj_rels_in_sents.append(dobj_rels_in_sent)
    
    dobj_rels_in_sents = [utils.remove_indices_from_annotion_tuples(sentence) for sentence in dobj_rels_in_sents]
    dobj_allsents = utils.remove_indices_from_annotion_tuples(dobj_allsents)

    dobj_rels_vectors_dict = {}

    for dobj_rel in dobj_allsents:
        vector = []
        for sent in dobj_rels_in_sents:
            vector.append(sent.count(dobj_rel))
        dobj_rels_vectors_dict[dobj_rel] = vector

    return dobj_rels_vectors_dict     

def create_dict_vectors_for_verbs(list_of_annotated_tokens_per_sentence):

    verbs_per_sent, verbs_overall = utils.extract_actions_from_annotated_tokens_per_sentence(list_of_annotated_tokens_per_sentence)

    verbs_vectors_dict = {}

    for verb in verbs_overall:
        vector = []
        for v in verbs_per_sent:
            vector.append(v.count(verb))
        verbs_vectors_dict[verb] = vector

    return verbs_vectors_dict

def create_action_vectors_given_dobj(actions, dobj_rels_sentencewise):
    # for instance for the direct object "knife" we create 
    # vectors for the whole text given a verb
    #
    #
    dobjs_all = []

    sentences_total = len(dobj_rels_sentencewise)
    dict_with_action_as_key_and_vector_as_value = {} 
    for action in actions:
        dict_with_action_as_key_and_vector_as_value[action]=np.zeros(sentences_total)


    for dobjs_rels in dobj_rels_sentencewise:
        for dobj_rel in dobjs_rels: #each sentence is a list [('dobj', ('put', 'VB', 0), ('plate', 'NN', 2))]
            dobj = dobj_rel[2][0]
            dobjs_all.append(dobj)

    dobj_sent_vector_as_dict_list = []

    for dobj in set(dobjs_all):
        dobj_sent_vector_as_dict = copy.deepcopy(dict_with_action_as_key_and_vector_as_value)
        for ind, dobj_rel_sent in enumerate(dobj_rels_sentencewise): 
            for dobj_rel in dobj_rel_sent:
                dobj_ = dobj_rel[2][0]
                if dobj == dobj_:
                   action = dobj_rel[1][0]
                   curent_action_vector = dobj_sent_vector_as_dict.get(action)
                   curent_action_vector[ind] = curent_action_vector[ind] + 1
                   dobj_sent_vector_as_dict[action] = curent_action_vector
        
        dobj_sent_vector_as_dict["dobj"] = dobj
        dobj_sent_vector_as_dict_list.append(dobj_sent_vector_as_dict)

    return dobj_sent_vector_as_dict_list       

############################ calculation methods

def calculate_granger_for_actions(dict_vb_vectors):
    p_val =0.05/len(dict_vb_vectors) # divide the initial p_value by the number of unique verbs in the text
    res = calculate_causality_matrix(dict_vb_vectors, calc_granger_causality, 1, return_all_relations=True, p_value=p_val)
    return res

def calculate_causality_matrix(dicts_with_vects, causality_test_function, max_lag, p_value = 0.05, return_all_relations = False):
    '''
    the dict_with_vectors contains words as keys and
    the corresponding word vectors as values

    A small p (≤ 0.05), reject the null hypothesis. This is strong evidence that the null hypothesis is invalid.
    A large p (> 0.05) means the alternate hypothesis is weak, so you do not reject the null. 

    '''
    causal_relations_candidates = []
    for k_1, v_1 in dicts_with_vects.items():
        #print(k_1, 'corresponds to', v_1)
        for k_2, v_2 in dicts_with_vects.items():
            if k_1 != k_2:
               x1 = v_1
               x2 = v_2
               granger_output = causality_test_function(x1, x2, max_lag)
               # create a dict with all vectors and granger-related infos 
               causal_relations_candidates.append({"x1":k_1, "x1_seq": v_1, "x2":k_2 , "x2_seq":v_2, "granger_out": granger_output})

    causal_relations = filter_causal_relations_from_list_of_candidates(causal_relations_candidates, p_value)
    if return_all_relations:
       return causal_relations, causal_relations_candidates
    else:
       return causal_relations

def filter_causal_relations_from_list_of_candidates(list_with_candidate_relations, p_value):
    '''
    input is a list of objects of type dict having the following structure:
    {'x1': str (e.g. a word), 'x1_seq':[vector], 'x2':str (e.g. a word), 'x2_seq': [vector], "granger_out": [{'stat_test_name':str, 'lag': int, 'p-val': float}] }
    Assume p_value = p = 0.05 (example)
    A small p (≤ 0.05), reject the null hypothesis. This is strong evidence that the null hypothesis is invalid.
    A large p (> 0.05) means the alternate hypothesis is weak, so you do not reject the null. 
    
    '''
    
    outcome_cause_effect = []#(cause, effect, lag)

    for candidate in list_with_candidate_relations:
        granger_result_for_lag = candidate.get("granger_out")
    
        for granger_lag in granger_result_for_lag:
            p_resulted = granger_lag.get("p-val")
            lag = granger_lag.get("lag")
            if p_resulted <= p_value:
               cause_effect_dict = {"cause":candidate['x2'], "effect": candidate["x1"], "lag": lag, "p_val":p_resulted}
               outcome_cause_effect.append(cause_effect_dict)
           
    return outcome_cause_effect
    print("e")

def calculate_granger_causality_for_verbs(verbs_vectors_dict):
    pass

def calculate_granger_causality_for_actions_dobjs(dobj_vectors_dicts):
    '''
    Each doctopnary (dict) contains the action vectors for a given object.
    Example of a dict:
    'wash':array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    'open':array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    'cook':array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    'take':array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    'turn':array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    'put':array([0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    'cut':array([0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.])
    'dobj':'carrots'
    
    '''
    results = []
    results_detailed = []

    for dobj_vectors_dict in dobj_vectors_dicts:
        dobj_vectors_dict_copy = {key: value[:] for key, value in dobj_vectors_dict.items()}
        dobj = dobj_vectors_dict_copy["dobj"]
        print("Granger causality vectors for dobj:"+ dobj) 
        dobj_vectors_dict_copy.pop('dobj')
        #TODO: the 0.05 p-value should be set as a parameter in the method
        p_val =0.05/len(dobj_vectors_dict_copy) # divide the initial p_value by the number of unique verbs in the text
        res, res_detailed = calculate_causality_matrix(dobj_vectors_dict_copy, calc_granger_causality, 1, return_all_relations=True, p_value=p_val)
        for r in res:
            r["dobj"] = dobj
        results.extend(res)
        results_detailed.extend(res_detailed)
    
    return results, results_detailed

def calc_granger_causality_btw_verbs_without_considering_objects():
    pass 
    '''
    We use verbs and events interchangeably.
    For identifying relations between events without considering the object, we
    also took a lag of 1, because in texts with longer sentences, the test tends to discover false positives 
    when applied with a longer lag. Furthermore, to
    reduce the familywise error rate during the multiple comparisons,
    we decreased the significance threshold by applying the Bonferroni correction
    '''

def calc_granger_causality_btw_events_considering_objects():
    pass 
    '''
    For the case of events given the object we per-
    formed Granger causality test with a lag from 1 to
    5 as the shortest instructions text has 5 sentences.
    '''

def calc_granger_causality_btw_events_and_states():
    pass
    '''
    For identifying relations between events and states
    we used a lag of 1, as the event and the change of
    state are usually described in the same sentence or
    in following sentences.
    '''

def calc_granger_causality(x1, x2, max_lag, stat_test_name = 'ssr_ftest' ):
    '''
    x1 : array_like
    x2 : array_like 
        Test if x2 Granger causes the first time series (x1). 
    max_lag : {int, Iterable[int]}
    stat_test_name: string (can be : 'ssr_ftest' , 'ssr_chi2test', 'lrtest', 'params_ftest')

    NULL hypothesis granger: 
    The Null hypothesis for grangercausalitytests is that the time series in the second column, x2, does NOT 
    Granger cause the time series in the first column, x1.
    Grange causality means that past values of x2 have a statistically significant effect on
    the current value of x1, taking past values of x1 into account as regressors. 
    We reject the null hypothesis that x2 does not Granger cause x1 if the pvalues are below a desired size
    of the test.
    if p = 5%
    A small p (≤ 0.05), reject the null hypothesis. This is strong evidence that the null hypothesis is invalid.
    Rejecting the null hypothesis means that x2 DOES granger cause x1 
    A large p (> 0.05) means the alternate hypothesis is weak, so you do not reject the null. 
    '''
    #np.array(list(zip(lat, lon)))

    d = {"x1": x1, "x2": x2}
    df = pd.DataFrame(d)

    gc_result_output = grangercausality_stattools.grangercausalitytests(df, max_lag)    
    gc_result_as_dict = parse_causality_test_output_into_dict(gc_result_output, max_lag, stat_test_name)

    return gc_result_as_dict

def parse_causality_test_output_into_dict(causality_test_output, max_lag, stat_test_name):
    '''
    takes the output of the causality test from the external python package
    returns a list of dicts for each lag
    stat_test_name can be : 'ssr_ftest' , 'ssr_chi2test', 'lrtest', 'params_ftest' 
    '''
    list_of_dicts_per_lag = []

    for lag in range(1, max_lag+1):
        lag_result_dict = causality_test_output.get(lag)[0]# at get(lag) results into a tuple where idx 0 is a dict with the values
        test_results =  lag_result_dict.get(stat_test_name)
        resulted_p_val = test_results[1]
        result_as_dict = {"stat_test_name": stat_test_name, "lag":lag, "p-val": resulted_p_val}
        list_of_dicts_per_lag.append(result_as_dict)

    return list_of_dicts_per_lag

def transform_causual_relations_results_from_dict_to_tuples(dict_causual_relations):
    # the purpose is to use this transformation for 
    # the creation of the graph (extended situation model)
    pass

def find_cyclic_causal_relations(causal_relations):
    
    #label_for_caus_relation_edge = "causes"
    #cycles_in_model = nx.simple_cycles(model_graph) # find all cyclic relations in the model
    # now filter only the ones of type "causes" (label == causes)
    #cycles_with_two_nodes = [cycle for cycle in cycles_in_model if len(cycle)==2]
    
    # using a Counter object checks if two lists should be considered equal, 
    # because they have exactly the same elements, only in different order.
    # Counter() runs with N complexity
    #Counter(list1) == Counter(list2)
    all_pairwise_combs = list(itertools.combinations(causal_relations, 2))
    cycles = [ pair for pair in all_pairwise_combs if Counter(pair[0]) == Counter(pair[1]) ]

    return cycles

# TODO: make some tests!
def find_direct_cyclic_causal_relations_in_dict_list(causal_relations_dict_list):
    # A -> B , B -> A : direct cyclic relations
    cyclic_rels_pairs = []
    all_pairwise_combs = list(itertools.combinations(causal_relations_dict_list, 2))
    for pair in all_pairwise_combs:
        fst_rel = pair[0]
        snd_rel = pair[1]
        # using a Counter object checks if two lists should be considered equal, 
        # because they have exactly the same elements, only in different order.
        # Counter() runs with N complexity
        fst_rel_cause_effect_obj_list = [fst_rel["cause"], fst_rel["effect"]]
        snd_rel_cause_effect_obj_list = [snd_rel["cause"], snd_rel["effect"]]
        if Counter(fst_rel_cause_effect_obj_list) == Counter(snd_rel_cause_effect_obj_list):
           cyclic_rels_pairs.append(pair)

    return cyclic_rels_pairs   
        
def transitive_causal_relations(cyclic_relations):
    # for A,B,C: A cyclic B, B cyclic C , C cyclic A -> transitive rel

    pass


def find_transitive_causal_relations(cyclic_relations):
    # for A,B,C: A cyclic B, B cyclic C , C cyclic A -> transitive rel
    cyclic_relations = [cycle[0] for cycle in cyclic_relations]
    transitive_relations = []
    for ind in range(len(cyclic_relations)):
        relation = cyclic_relations[ind]
        rel_candidates = []
        for rel_candidate in cyclic_relations[ind+1:]:
            if relation[0] or relation[1] in rel_candidate:
                rel_candidates.append(rel_candidate)
        transitive_relations.append(find_transitive_rels_helper(rel_candidates, relation))

    return transitive_relations

def find_transitive_rels_helper(candidate_rels, initial_relation):

    transitive_rels_all = []
    for rel in candidate_rels:
        intersection = set(initial_relation).intersection(set(rel))
        if len(intersection)>1:
            continue
        node_diff = list(set(initial_relation) - intersection)[0]
        node_diff_2 = list(set(rel) - intersection)[0]
        transitive_rels = [list(set(rel + rel_)) for rel_ in candidate_rels if rel_ != rel and node_diff in rel_ and len(set(rel + rel_))==3 and node_diff_2 in rel_ ]
        transitive_rels_sorted = [sorted(transitive_rel) for transitive_rel in transitive_rels]

        transitive_rels_all.extend(transitive_rels_sorted)
    transitive_rels_without_duplicates = set(map(tuple, transitive_rels_all))
    transitive_rels_without_duplicates_list = map(list, transitive_rels_without_duplicates)
    #merged_transitive_relations_all = itertools.chain(transitive_rels_all)

    return list(transitive_rels_without_duplicates_list)

def find_transitive_causal_relations_using_graph(cyclic_relations):
    '''
    using the networkx library
    each element in cyclyc_relations is a tuple ([A, B],[B,A])
    A, B are nodes (or words) and each of both lists represents a "causes"
    relationship between two nodes
    '''
    graph = nx.DiGraph()
    #we transform the cyclic relations to graph nodes 
    # we use a directed Graph, since the current version of networkx does
    # not have an implementation of a method to find cycles
    # transitive relations are cycles (of 3 nodes) in the graph
    for cyclic_rel in cyclic_relations:
        nodes = cyclic_rel[0] # we can take only the first list, since the second contains the same nodes
        graph.add_edge(nodes[0], nodes[1])    
        graph.add_edge(nodes[1], nodes[0])
    
    cycles = list(nx.simple_cycles(graph))
    cycles_wo_dups = utils.remove_dups_from_list_of_lists(cycles)
    transitive_relations = [cycle for cycle in cycles_wo_dups if len(cycle) == 3]#see paper for transitive relation definition
    #now, remove duplicates
    return transitive_relations