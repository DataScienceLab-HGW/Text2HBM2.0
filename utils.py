'''
This script contains some utility functions


Some of the functions such as 
is_indobj_relation, is_dobj_relation and is_property_relation require domain knowledge

In order to add/remove information, please modify the function itself


https://sites.google.com/site/partofspeechhelp/home/vb_vbp

################# Noun annotations according to the parser #################


Noun, singular or mass
NNS 	Noun, plural
NNP 	Proper noun, singular
NNPS 	Proper noun, plural 


################# Verb annotations according to the parser #################

VB 	    Verb, base form
VBD 	Verb, past tense
VBG 	Verb, gerund or present participle
VBN 	Verb, past participle
VBP 	Verb, non-3rd person singular present
VBZ     Verb, 3rd person singular present 

At the moment only VB is used, but maybe later on we should add 
the other type of verbs (of course, we should consider the definition of an "action")

'''
from typing import List
from networkx import Graph
from collections import Counter

RELATION_VERB_NO_OBJ = "verbNoObj" #TODO: there is another definition in parser_subproc.py
RELATION_INDOBJ = "indObj"
VB_DOBJ_INDOBJ_RELATIONSHIP = "verbDobjIndobj"
ADJECTIVE_TAGS = ["JJ", "JJR", "JJS"]
VERB_TAGS = ["VB", "VBZ", "VBP", "VBD"]
NOUN_TAGS = ["NN", "NNS", "NNP"]

VERB_PAST_TENSE_TAG = "VBD"
VERB_PRESENT_TENSE_TAG = "VB"


########### FUNCTIONS CONCERNING PARSED INPUT FILE
def extract_verbs_and_nouns_from_parsed_text(parsed_text_sentencewise, lower_case_bool):
    
    vbs = []
    nouns = []
   
    for sentence in parsed_text_sentencewise:
        for token in sentence:
            if is_verb(token[1]): #idx 1 is the type description of the token
                if lower_case_bool:
                   vbs.append(token[0].lower()) # idx 0 is the word
                else:
                    vbs.append(token[0])
            if is_noun(token[1]):
                if not lower_case_bool:
                   nouns.append(token[0])
                else:
                   nouns.append(token[0].lower())
    
    return (vbs, nouns)

###########

def get_noun_hypernym(noun, hypernym_graph:Graph) -> str:

    successors = list(hypernym_graph.successors(noun))
    hypernym = ""
    if len(successors) == 0:
        raise ValueError('No hypernym for the noun ' + noun)
    else:
        hypernym = successors[0]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    return hypernym

def split_list_into_chunks_of_n_elements(list_, n):
    # looping till length l
    for i in range(0, len(list_), n): 
        yield list_[i:i + n]

def transform_annotated_sentence_to_tuples_of_token_annotation(ann_sentence): 
    #Example: Put/VB the/DT scissors/NNS on/IN the/DT table/NN ./.
    tokens = ann_sentence.split(" ")
    list_of_tuples_of_tokens_with_annotations = [tuple(token.rsplit("/")) for token in tokens]
    
    return list_of_tuples_of_tokens_with_annotations

def transform_dependencies_strings(dependencies):
    #input like: 'root(ROOT-0, Take-1)\ndet(pot-4, a-2)\namod(pot-4, clean-3)\ndobj(Take-1, pot-4)\ncase(cupboard-7, from-5)\ndet(cupboard-7, the-6)\nnmod:from(Take-1, cupboard-7)'
    #output like: ['root(ROOT-0, Take-1)', 'det(pot-4, a-2)', 'amod(pot-4, clean-3)', 'dobj(Take-1, pot-4)', 'case(cupboard-7, from-5)', 'det(cupboard-7, the-6)', 'nmod:from(Take-1, cupboard-7)']
    transformed_deps  = dependencies.split("\n")
    return transformed_deps

def transform_dep_strings_to_triples(dependencies_strings):
    '''
    this method extracts the relationships and delivers rel(index_ob1, index_ob1),
    where the index is the position of the token in the sentence
    '''
    tuples_of_dep_obj1_obj2 = []

    for dep_str in dependencies_strings:
        # the format is like 'det(office-2, The-1)'
        parts_dep_index = dep_str.split("(",1) #output like ['det','office-2, The-1'))
        dep_type = parts_dep_index[0]
        dep_objects_index = parts_dep_index[1][:-1].split(", ")#splits 'office-2, The-1' into ["office-2","The-1"]
        #The [:-1] call is to eliminate the last bracket ) 
        obj_1_idx =  dep_objects_index[0].rpartition('-')[2]
        obj_2_idx =  dep_objects_index[1].rpartition('-')[2]
        tuples_of_dep_obj1_obj2.append((dep_type, int(obj_1_idx), int(obj_2_idx)))

    return tuples_of_dep_obj1_obj2

def remove_root_relation(list_of_dep_triples):
    #TODO: maybe remove this function? 
    #input like [('root', 0, 1), ('det', 3, 2), ('dobj', 1, 3), ('case', 6, 4), ('det', 6, 5), ('nmod:from', 1, 6)]
    return list(filter(lambda x: x[0]!='root', list_of_dep_triples))

def filter_dobj_indobj_prop_relations(list_of_relation_triples_for_sents):
    '''
    filters:
    direct objects relations (dobj_rels)
    indirect objects relations (indobj_rels)
    property relations (prop_rels), a property being for instance "green", "small", etc.
    verb relations without an object
    '''

    dobj_rels=[]
    indobj_rels = []
    prop_rels =[]

    for sent in list_of_relation_triples_for_sents:
        for dep_triple in sent: #triple such as ('nsubj', ('gave', 'VBD', 2), ('She', 'PRP', 1))
            #lower_case the verb
            dep_triple = (dep_triple[0], (dep_triple[1][0].lower(), dep_triple[1][1], dep_triple[1][2]), (dep_triple[2][0].lower(), dep_triple[2][1], dep_triple[2][2]))
            if is_dobj_relation(dep_triple):
               dobj_rels.append(dep_triple)
            if is_indobj_relation(dep_triple):
               indobj_rels.append(dep_triple)
            if is_property_relation(dep_triple):
               prop_rels.append(dep_triple)
            
    prop_rels = list(set([("property", dep_triple[1], dep_triple[2]) for dep_triple in prop_rels]))

    return dobj_rels, indobj_rels, prop_rels

def filter_dobj_indobj_prop_vbnoobj_relations_sentencewise(list_of_relation_triples_for_sents):
    
    dobj_rels_sentencewise=[]
    indobj_rels_sentencewise = []
    prop_rels_sentencewise =[]
    vb_no_obj_rels_sentencewise = []

    verbs_from_dobj_rels_sentencewise = []
    verbs_from_indobj_rels_sentencewise = []
    verbs_from_prop_rels_sentencewise = []
    verbs_from_no_obj_rels_sentencewise = []

    
    for sent in list_of_relation_triples_for_sents:
        
        dobj_rels_sentence = []
        indobj_rels_sentence = []
        prop_rels_sentence = []
        no_obj_rels_sentence = []

        verbs_from_dobj_rels_sentence = []
        verbs_from_indobj_rels_sentence = []
        verbs_from_prop_rels_sentence = []
        verbs_from_no_obj_rels_sentence = []

        for dep_triple in sent: #triple such as ('nsubj', ('gave', 'VBD', 2), ('She', 'PRP', 1))
            if is_dobj_relation(dep_triple):
               dobj_rels_sentence.append(dep_triple)
               verbs_from_dobj_rels_sentence.extend(extract_verbs_from_dep_triple(dep_triple))
            if is_indobj_relation(dep_triple):
               indobj_rels_sentence.append(dep_triple)
               verbs_from_indobj_rels_sentence.extend(extract_verbs_from_dep_triple(dep_triple))
            if is_property_relation(dep_triple):
               prop_rels_sentence.append(dep_triple)  
               verbs_from_prop_rels_sentence.extend(extract_verbs_from_dep_triple(dep_triple))   
            if is_no_obj_relation(dep_triple):
               no_obj_rels_sentence.append(dep_triple)
               verbs_from_no_obj_rels_sentence.extend(extract_verbs_from_dep_triple(dep_triple))

        prop_rels_sentence = [("property", dep_triple[1], dep_triple[2]) for dep_triple in prop_rels_sentence]

        dobj_rels_sentencewise.append(dobj_rels_sentence)
        indobj_rels_sentencewise.append(indobj_rels_sentence)
        prop_rels_sentencewise.append(prop_rels_sentence)
        vb_no_obj_rels_sentencewise.append(no_obj_rels_sentence)

        verbs_from_dobj_rels_sentencewise.append(list(set(verbs_from_dobj_rels_sentence)))
        verbs_from_indobj_rels_sentencewise.append(list(set(verbs_from_indobj_rels_sentence)))
        verbs_from_prop_rels_sentencewise.append(list(set(verbs_from_prop_rels_sentence)))
        verbs_from_no_obj_rels_sentencewise.append(list(set(verbs_from_no_obj_rels_sentence)))

    # we assign shorter variable names for a better code readability
    a = verbs_from_dobj_rels_sentencewise
    b = verbs_from_indobj_rels_sentencewise
    c = verbs_from_prop_rels_sentencewise

    #some of the verbs in the no_obj_relations might occur in other relations such as indobj or dobj
    #for that reason we have to remove them 

    for idx, sent_with_no_obj_verbs in enumerate(verbs_from_no_obj_rels_sentencewise):
        verbs_from_no_obj_rels_sentencewise[idx] = [
        (RELATION_VERB_NO_OBJ, verb_triple) for verb_triple in sent_with_no_obj_verbs
        if verb_triple not in a[idx] 
        and verb_triple not in b[idx] 
        and verb_triple not in c[idx]]

    #some of the relationships in no_obj_rels_sentence might contain verbs which already exist in the 
    #dobj and in the indobj relationships in the sentence
    #we remove such verbs
    #verbs_without_objects_sentencewise = 

    return dobj_rels_sentencewise, indobj_rels_sentencewise, prop_rels_sentencewise, verbs_from_no_obj_rels_sentencewise 

def is_dobj_relation(dep_as_triple):
    #triple such as ('nsubj', ('gave', 'VBD'), ('She', 'PRP'))
    dep_name = dep_as_triple[0]
    
    return dep_name == "dobj"

def is_indobj_relation(dep_as_triple):
    #triple such as ('nsubj', ('gave', 'VBD'), ('She', 'PRP'))
    dep_name = dep_as_triple[0]

    return ("nmod:" in dep_name and ("poss" not in dep_name and "tmod" not in dep_name)) and dep_as_triple[1][1] in ["VB","VBP","VBZ"]

def is_property_relation(dep_as_triple):
    #triple such as ('nsubj', ('gave', 'VBD'), ('She', 'PRP'))
    dep_name = dep_as_triple[0]
    is_adjective_modifier = dep_as_triple[2][1] in ADJECTIVE_TAGS #JJ pos-tag means adjective
   
    return (dep_name == "amod" or dep_name == "nsubj") and is_adjective_modifier

def is_no_obj_relation(dep_as_triple):
    # dep_astriple like: ('root', ('.', '.', 9), ('take', 'VB', 0))
    dep_name = dep_as_triple[0]
    dep_head_part_of_speech = dep_as_triple[1][1]
    dep_tail_part_of_speech = dep_as_triple[2][1] 
    contains_verb = dep_head_part_of_speech in ["VB","VBZ","VBP"] or dep_tail_part_of_speech in ["VB","VBZ","VBP"]
    if ("dobj" not in dep_name and "nmod" not in dep_name) and contains_verb :
        return True
    else:
        return False        
   
def is_verb(word):
    return word in VERB_TAGS

def is_noun(word_token):

    return word_token in NOUN_TAGS

def is_verb_triple(verb_triple):
    #verb_triple like: ('gave', 'VBD', 2)
    return is_verb(verb_triple[1])

def extract_verbs_from_dep_triple(dep_triple):
    # has a format like: ('nsubj', ('gave', 'VBD', 2), ('She', 'PRP', 1))
    # output: ('gave', 'VBD', 2)
    verbs_list = [verb_dep for verb_dep in list(dep_triple) if is_verb_triple(verb_dep) ]
    return verbs_list

def find_max_nested_list_length(lst):
    maxList = max(lst, key = lambda i: len(i))
    maxLength = len(maxList)
      
    return maxList, maxLength


############### START METHODS TO DECAPITALIZE DIFFERENT ENTITIES
## TODO: maybe include this in the parser itself? (as an optional argument lower=True/False)
def remove_capitalization_in_dobj_indobj_rels_sentencewise(dobj_indobj_sentencewise):
    # dobj_indobj_sentencewise is [ [('dobj', (...), (...)), ('dobj', (...), (...))] ] (a list of sentences
    # where each sentence is represented as a list of relations)
    dobj_indobj_rels_sentencewise_decapitalized = []
    for rels_in_sentence in dobj_indobj_sentencewise:
        rels_in_sentence_decap = remove_capitalization_in_dobj_or_indobj_rels(rels_in_sentence)
        dobj_indobj_rels_sentencewise_decapitalized.append(rels_in_sentence_decap)

    return dobj_indobj_rels_sentencewise_decapitalized

def remove_capitalization_in_dobj_or_indobj_rels(dobj_rels):
    #first word in a dobj or indobj relation is always a verb. If a sentence starts with a verb, it will be capitalized
    #this function removes the capitalization in the verb
    dobj_rels_lower_case = []

    for dobj_rel in dobj_rels:
        rel_name = dobj_rel[0]
        verb = dobj_rel[1]
        noun = dobj_rel[2]
        verb_idx = dobj_rel[1][2]
       
        verb_new = (verb[0].lower(), verb[1], verb_idx)

        dobj_rels_lower_case.append((rel_name, verb_new, noun))

    return dobj_rels_lower_case

def remove_capitalization_in_vbnoobj_rels_sentencewise(vb_noobj_rels_sentences):
    # a single relation is like:[('verbNoObj', ('smile', 'VBP', 2)), ('verbNoObj', ('eat', 'VBP', 0))]
    vbnoobj_rels_sentencewise_lower_case = []

    for rels_in_sentence in vb_noobj_rels_sentences:
        rels_in_sentence_decap = remove_capitalization_in_vbnoobj_rels(rels_in_sentence)
        vbnoobj_rels_sentencewise_lower_case.append(rels_in_sentence_decap)

    return vbnoobj_rels_sentencewise_lower_case

def remove_capitalization_in_vbnoobj_rels(vb_noobj_rels_in_sentence):
    # a single relation is like:[("vbnoobj", ('smile', 'VBP', 2) ), ("vbnoobj", ('eat', 'VBP', 0))]

    vbnoobj_rels_lower_case = []

    for vb_noobj_rel in vb_noobj_rels_in_sentence:
        verb_noobj = vb_noobj_rel[1][0]
        verb_new = (RELATION_VERB_NO_OBJ, (verb_noobj.lower(), vb_noobj_rel[1][1], vb_noobj_rel[1][2]))

        vbnoobj_rels_lower_case.append((verb_new))

    return vbnoobj_rels_lower_case
################# 

def remove_indices_from_annotion_tuple(annotation_tuple):
    # example input ('dobj', ('take', 'VB', 0), ('knife', 'NN', 2))
    return (annotation_tuple[0], annotation_tuple[1][0], annotation_tuple[2][0])

def remove_indices_from_annotion_tuples(annotation_tuples):
    tuples_with_removed_indices = [remove_indices_from_annotion_tuple(annot_tup) for annot_tup in annotation_tuples]
    return tuples_with_removed_indices

def extract_actions_from_annotated_tokens_per_sentence(list_of_annotated_tokens_per_sentence):
    '''
    We call the verbs in present tense "actions"
    
    '''
    verbs_per_sent = []
    verbs_overall = []

    for annot_sent in list_of_annotated_tokens_per_sentence:
        verbs_in_sent = []
        for token_as_tuple in annot_sent:
            verb = token_as_tuple[0]
            pos_tag = token_as_tuple[1]  
            
            if pos_tag == "VB" or pos_tag == "VBZ" or pos_tag == "VBP":# detect different types of verbs (VB, VBP, VBZ)
               verbs_in_sent.append(verb.lower())
        
        verbs_per_sent.append(verbs_in_sent)
        verbs_overall.extend(verbs_in_sent)

    return verbs_per_sent, list(set(verbs_overall))

def extract_preposition_from_indobj_rel(indobj_rel):
    relations_name = indobj_rel[0]
    preposition = relations_name.split("nmod:")[1]
    return preposition

def extract_prepositions_from_indobj_rels(indobj_relations):
    '''
    returns a list of unique preposition names (no duplicates)
    '''
    prepositions_from_indobj_rels = []

    for indobj_rel in indobj_relations:
        preposition = extract_preposition_from_indobj_rel(indobj_rel)
        prepositions_from_indobj_rels.append(preposition)

    return list(set(prepositions_from_indobj_rels)) #return unique prepositions

def extract_properties_from_prop_rels(prop_rels):
    '''
    extracts the adjective (property) JJ, from prop relations
    each relation has a structure like : ('property', ('spoon', 'NN'), ('wooden', 'JJ'))
    '''
    #remove duplicates 
    #!!!
    #removing duplicates might be removed later on if we need to 
    #identify the particular objects
    #!!!
    prop_rels = list(set(prop_rels))
    properties = []
    
    for relation_triple in prop_rels:
        property = relation_triple[2]
        #property[1] is the pos-tag
        #property[0] is the adjective/the word
        if property[1] in ADJECTIVE_TAGS:
           properties.append(property[0])
    
    return properties

def extract_nouns_from_dobj_indobj_rels(dobj_rels, indobj_rels):
    # one relation example: ('dobj', ('Take', 'VB'), ('knife', 'NN'))
    # we need to extract the NNs ( triple[2][0] )
    return list(set([triple[2][0] for triple in dobj_rels + indobj_rels] ))  

############## Extract actions 
#TODO: maybe just put one function? extract_actions_from_obj_rels (DRY principle)
#the extract_vbnoobj_function is, however, different
def extract_actions_from_dobj_rels(dobj_rels):
    # one relation example: ('dobj', ('Take', 'VB'), ('knife', 'NN'))
    # we need to extract the verbs only
    return list(set([triple[1][0] for triple in dobj_rels] ))  

def extract_actions_from_indobj_rels(indobj_rels):
    return list(set([triple[1][0] for triple in indobj_rels] ))  

def extract_actions_from_vbnoobj_rels(vb_no_obj_rels):
    return list(set([triple[0] for triple in vb_no_obj_rels] ))  

def extract_types_of_actions( actions_from_dobj_rels, actions_from_indobj_rels, actions_without_objects):

    acts_with_dobj_and_indobj = list(set.intersection(set(actions_from_dobj_rels), set(actions_from_indobj_rels) ))
    acts_with_dobj_only = [act for act in actions_from_dobj_rels if act not in acts_with_dobj_and_indobj ]
    acts_with_indobj_only = [act for act in actions_from_indobj_rels if act not in acts_with_dobj_and_indobj ]
    acts_without_any_objects = [act for act in actions_without_objects if act not in actions_from_dobj_rels and act not in actions_from_indobj_rels]
    #acts_with_indobj_dobj_or_without_objects = [act for act in actions_all if act in acts_with_dobj_and_indobj and act not in acts_with_indobj_only and act not in acts_without_objects and act not in ]
    actions_which_might_not_have_objects = [act for act in actions_without_objects if act in actions_from_dobj_rels or act in actions_from_indobj_rels]

    return acts_without_any_objects, actions_which_might_not_have_objects, acts_with_dobj_and_indobj, acts_with_dobj_only, acts_with_indobj_only

'''
def create_lst_of_vb_dobj_indobj_prep_sentencewise(dobj_rels_sentwise, indobj_rels_sentwise):

    verb_dobj_indobj_prep_relations_per_sent = []
    for idx, dobjs_in_sent in enumerate(dobj_rels_sentwise):

        verb_dobj_indobj_per_sent = []
        for dobj_rel in dobjs_in_sent:
            is_verb_in_rel = dobj_rel[1][1] in ["VB", "VBZ", "VBP"]
            if is_verb_in_rel:
               verb = dobj_rel[1]
               indobj_rels_sent = indobj_rels_sentwise[idx]
               for indobj_rel in indobj_rels_sent:
                   verb_ind_rel = indobj_rel[1]
                   if verb_ind_rel == verb:
                      verb_dobj_indoj_prep_rel = [(verb, dobj_rel[2], indobj_rel[2]), (extract_preposition_from_indobj_rel(indobj_rel),indobj_rel[2])]
                      verb_dobj_indobj_per_sent.append(verb_dobj_indoj_prep_rel)
        
        verb_dobj_indobj_prep_relations_per_sent.append(verb_dobj_indobj_per_sent)
                   
    return verb_dobj_indobj_prep_relations_per_sent

'''

def create_lst_of_vb_dobj_indobj_prep_props_sentencewise(dobj_rels_sentencewise_with_properties, indobj_rels_sentencewise_with_properties):
    verb_dobj_indobj_prep_relations_per_sent = []
    for idx, dobjs_in_sent in enumerate(dobj_rels_sentencewise_with_properties):

        verb_dobj_indobj_per_sent = []
        for dobj_rel in dobjs_in_sent:
            is_verb_in_rel = dobj_rel[0][1][1] in VERB_TAGS
            if is_verb_in_rel:
               verb = dobj_rel[0][1]
               properties_dobj = dobj_rel[1]
               indobj_rels_sent = indobj_rels_sentencewise_with_properties[idx]
               for indobj_rel in indobj_rels_sent:
                   verb_ind_rel = indobj_rel[0][1]
                   if verb_ind_rel == verb:
                      ind_obj_preposition_part = indobj_rel[0]
                      noun_indobj_rel = indobj_rel[0][2]
                      noun_dobj_rel =  dobj_rel[0][2]
                      preposition = extract_preposition_from_indobj_rel(ind_obj_preposition_part)
                      verb_dobj_indoj_prep_rel = [(verb, noun_dobj_rel, noun_indobj_rel), (preposition, noun_indobj_rel)]
                      properties_indobj = indobj_rel[1]
                      properties_all = properties_dobj + properties_indobj
                      verb_dobj_indoj_prep_rel.append(properties_all)
                      verb_dobj_indobj_per_sent.append(verb_dobj_indoj_prep_rel)

        
        verb_dobj_indobj_prep_relations_per_sent.append(verb_dobj_indobj_per_sent)
                   
    return verb_dobj_indobj_prep_relations_per_sent
'''
def extend_lst_of_vb_dobj_indobj_prep_sentencewise_with_props(vb_dobj_indobj_prep_sentencewise, properties_rels_sentencewise):
    
    add properties to existing list of vb_dobj_indobj_prep_sentencewise
    Intended to be used after create_lst_of_vb_dobj_indobj_prep_sentencewise
    
    lst_of_vb_dobj_indobj_prep_prop_sentencewise = []
    for idx, vb_dobj_indobj_prep_in_sentence in enumerate(vb_dobj_indobj_prep_sentencewise):

        vb_dobj_prep_prop_in_sentence_lst = []
        for vb_dobj_indobj_prep in vb_dobj_indobj_prep_in_sentence:
            prop_candidates = [vb_dobj_indobj_prep[0][1], vb_dobj_indobj_prep[0][2]]
            vb_dobj_prep_prop_in_sentence = vb_dobj_indobj_prep
            prop_list = []
            for property in properties_rels_sentencewise[idx]:
                if property[1] in prop_candidates:
                   prop_list.append((property[2],property[1]))
            
            vb_dobj_prep_prop_in_sentence = vb_dobj_prep_prop_in_sentence + [prop_list]
            vb_dobj_prep_prop_in_sentence_lst.append(vb_dobj_prep_prop_in_sentence)
                   
        lst_of_vb_dobj_indobj_prep_prop_sentencewise.append(vb_dobj_prep_prop_in_sentence_lst)

    return lst_of_vb_dobj_indobj_prep_prop_sentencewise

'''

def extract_dobj_rels_from_vb_dobj_indobj_rel_sentwise(list_verb_dobj_indobj_prep_props_sentencewise):

    dobj_rels_from_vb_dobj_indobj_rel_sentwise = []

    for sentence_with_rel in  list_verb_dobj_indobj_prep_props_sentencewise:
        dobj_rels_from_vb_dobj_indobj_rel= []
        for vb_dobj_indobj_rel in sentence_with_rel:
            rel_ = ('dobj', vb_dobj_indobj_rel[0][0], vb_dobj_indobj_rel[0][1])
            dobj_rels_from_vb_dobj_indobj_rel.append(rel_)

        dobj_rels_from_vb_dobj_indobj_rel_sentwise.append(dobj_rels_from_vb_dobj_indobj_rel)

    return dobj_rels_from_vb_dobj_indobj_rel_sentwise           

def extract_indobj_rels_from_vb_dobj_indobj_rel_sentwise(list_verb_dobj_indobj_prep_props_sentencewise):
    indobj_rels_from_vb_dobj_indobj_rel_sentwise = []

    for sentence_with_rel in  list_verb_dobj_indobj_prep_props_sentencewise:
        indobj_rels_from_vb_dobj_indobj_rel= []
        for vb_dobj_indobj_rel in sentence_with_rel:
            rel_ = ('nmod:'+ vb_dobj_indobj_rel[1][0], vb_dobj_indobj_rel[0][0], vb_dobj_indobj_rel[0][2])
            indobj_rels_from_vb_dobj_indobj_rel.append(rel_)

        indobj_rels_from_vb_dobj_indobj_rel_sentwise.append(indobj_rels_from_vb_dobj_indobj_rel)

    return indobj_rels_from_vb_dobj_indobj_rel_sentwise

#TODO:think of a way to merge both extract_<obj_type> functions into a single one (DRY principle)


def extract_dobj_rels_with_props_existing_outside_vb_dobj_indobj_rels(dobj_rels_and_props_sentencewise, list_verb_dobj_indobj_prep_props_sentencewise, return_sentencewise = False):
     # if return_sentencewise is set, then the function will return a second variable which
    # will contain the dobj outside vb-dobj-indobj relationship sentencewise (a list of length n, where n is the number of sentences) 
    
    # Important: delivers also the properties of the dobj
    # first, extract the dobj_rels from the verb-dobj-indobj relations in list_verb_dobj_indobj_prep_props_sentencewise
    # this will make filtering out the dobj_rels which are not in verb-dobj-indobj rel easier
    dobj_rels_from_vb_dobj_indobj_rel_sentwise = extract_dobj_rels_from_vb_dobj_indobj_rel_sentwise(list_verb_dobj_indobj_prep_props_sentencewise)
    # allocate list for 
    if return_sentencewise:
       dobj_outside_vb_dobj_indobj_rel_sentwise =[[] for _ in range(len(dobj_rels_and_props_sentencewise))]


    #filter out
    dobj_rels_outside_vb_dobj_indobj_rel = []
    for idx, sentence_dobj in enumerate(dobj_rels_and_props_sentencewise):
        if not return_sentencewise:
            for dobj in sentence_dobj:
                if dobj[0] not in dobj_rels_from_vb_dobj_indobj_rel_sentwise[idx]:
                    dobj_rels_outside_vb_dobj_indobj_rel.append(dobj)
        else:
            
            for dobj in sentence_dobj:
                if dobj[0] not in dobj_rels_from_vb_dobj_indobj_rel_sentwise[idx]:
                    dobj_rels_outside_vb_dobj_indobj_rel.append(dobj)
                    dobj_outside_vb_dobj_indobj_rel_sentwise[idx].append(dobj)
            
    
    if return_sentencewise:
        return dobj_rels_outside_vb_dobj_indobj_rel, dobj_outside_vb_dobj_indobj_rel_sentwise
    else:
        return dobj_rels_outside_vb_dobj_indobj_rel
    
def extract_indobj_rels_with_props_existing_outside_vb_dobj_indobj_rels(indobj_rels_sentencewise, list_verb_dobj_indobj_prep_props_sentencewise, return_sentencewise = False):
    # first, extract the indobj_rels from the verb-dobj-indobj relations in list_verb_dobj_indobj_prep_props_sentencewise
    # this will make filtering out the indobj_rels which are not in verb-dobj-indobj rel easier
    indobj_rels_from_vb_dobj_indobj_rel_sentwise = extract_indobj_rels_from_vb_dobj_indobj_rel_sentwise(list_verb_dobj_indobj_prep_props_sentencewise)
    
    if return_sentencewise:
       indobj_outside_vb_dobj_indobj_rel_sentwise =[[] for _ in range(len(indobj_rels_sentencewise))]
    #filter out
    indobj_rels_outside_vb_dobj_indobj_rel = []
    for idx, sentence_indobj in enumerate(indobj_rels_sentencewise):
        if not return_sentencewise:
            for indobj in sentence_indobj:
                if indobj[0] not in indobj_rels_from_vb_dobj_indobj_rel_sentwise[idx]:

                    indobj_vb_obj_part = indobj[0]
                    preposition = extract_preposition_from_indobj_rel(indobj_vb_obj_part)
                    vb = indobj_vb_obj_part[1]
                    obj = indobj_vb_obj_part[2]
                    props = indobj[1]
                    indobj_rel_new = ((vb, obj),(preposition, obj), props)
                    indobj_rels_outside_vb_dobj_indobj_rel.append(indobj_rel_new)
        else:
            for indobj in sentence_indobj:
                if indobj[0] not in indobj_rels_from_vb_dobj_indobj_rel_sentwise[idx]:

                    indobj_vb_obj_part = indobj[0]
                    preposition = extract_preposition_from_indobj_rel(indobj_vb_obj_part)
                    vb = indobj_vb_obj_part[1]
                    obj = indobj_vb_obj_part[2]
                    props = indobj[1]
                    indobj_rel_new = ((vb, obj),(preposition, obj), props)
                    indobj_rels_outside_vb_dobj_indobj_rel.append(indobj_rel_new)
                    indobj_outside_vb_dobj_indobj_rel_sentwise[idx].append(indobj_rel_new)
    
    if return_sentencewise:
        return indobj_rels_outside_vb_dobj_indobj_rel, indobj_outside_vb_dobj_indobj_rel_sentwise
    else:
        return indobj_rels_outside_vb_dobj_indobj_rel

########## removing index information from tuples
# TODO: merge all functions into one which just considers the type of relation beaing passed
def remove_idx_and_tag_from_dobj_props_rels(dobj_existing_outside_vb_dobj_indobj_rels):

    dobj_rels_noidx = [remove_idx_dobj_props_rel(dobj_prop_rel) for dobj_prop_rel in dobj_existing_outside_vb_dobj_indobj_rels]

    return dobj_rels_noidx

def remove_idx_dobj_props_rel(dobj_prop_rel):
    # ( ('dobj', ('take', 'VB', 0), ('sponge', 'NN', 2) ) [('property', ('cupboard', 'NN', 3), ('big', 'JJ', 2))] )
    #
    dobj_part = dobj_prop_rel[0]
    dobj_rel_name = dobj_part[0]
    dobj_rel_vb = dobj_part[1][0]
    dobj_rel_noun = dobj_part[2][0]
    props_part = dobj_prop_rel[1] # this is a list!
    props_part_noidx = [remove_idx_and_tag_from_prop_rel(prop) for prop in props_part]
    
    return [[dobj_rel_name, dobj_rel_vb, dobj_rel_noun], props_part_noidx]

def remove_idx_and_tag_from_indobj_props_rels(indobj_existing_outside_vb_dobj_indobj_rels):
    
    indobj_rels_noidx = [remove_idx_indobj_prop_rel(indobj_prop_rel) for indobj_prop_rel in indobj_existing_outside_vb_dobj_indobj_rels]

    return indobj_rels_noidx

def remove_idx_indobj_prop_rel(indobj_rel):
    # ( (('wash', 'VB', 0), ('sponge', 'NN', 4)), ('with', ('sponge', 'NN', 4)), [('property', (...), (...))] )
    verb_indobj_part = indobj_rel[0]
    preposition = indobj_rel[1][0]
    props_part = indobj_rel[2]

    vb = verb_indobj_part[0][0]
    indobj = verb_indobj_part[1][0] 
    props_part_noidx = [remove_idx_and_tag_from_prop_rel(prop) for prop in props_part]

    return [[RELATION_INDOBJ, vb, indobj], preposition, props_part_noidx]


def remove_idx_and_tag_from_prop_rel(prop_rel):
    # prop_rel looks like: ('property', ('cupboard', 'NN', 3), ('big', 'JJ', 2))
    rel_name = prop_rel[0]
    noun_part = prop_rel[1]
    noun = noun_part[0]
    adj_part =  prop_rel[2]
    adj = adj_part[0]

    return (rel_name, noun, adj)

def remove_idx_and_tag_from_vb_noobj_rels(vb_no_obj_rels):
    # each element is like: ('look', 'VB', 0)
    # TODO: on 10.05.22 changed to [[RELATION_VERB_NO_OBJ, vb[1][0]]]
    # this is done in order to look like the other relationships later on
    # basically it is a list because we also expect to add properties at some point

    vbs = [[[RELATION_VERB_NO_OBJ, vb[1][0]]] for vb in vb_no_obj_rels ]
    return vbs
    
def remove_idx_and_tag_from_vb_dobj_indobj_prep_props(verb_dobj_indobj_prep_props):
    #(('take', 'VB', 0), ('knife', 'NN', 4), ('counter', 'NN', 8))
    #('from', ('counter', 'NN', 8))
    #[('property', (...), (...)), ('property', (...), (...))]
    vb_dobj_indobj_props_noidx = []

    for rel in verb_dobj_indobj_prep_props:
        vb_dobj_indobj_part = [el[0] for el in rel[0]]
        preposition = rel[1][0]
        props_part = rel[2]
        props = [remove_idx_and_tag_from_prop_rel(prop) for prop in props_part]
        vb_dobj_indobj_props_noidx.append([[VB_DOBJ_INDOBJ_RELATIONSHIP] + vb_dobj_indobj_part, preposition, props])
    
    return vb_dobj_indobj_props_noidx


######################## FUNCTIONS FOR LANGUAGE GROUNDING



def create_grounded_verb_dobj_indobj_triples(verb_dobjs_indobjs_per_sentence, hypernym_graph_obj: Graph):
    
    grounded_verb_dobj_indobj_per_sentence = []

    for verb_dobj_indobj_sent in verb_dobjs_indobjs_per_sentence:
        
        grounded_verb_dobj_indobj_triples_in_sent = []
        for verb_dobj_indobj_triple in verb_dobj_indobj_sent: # a triple looks like ('Take', 'VB', 0), ('knife', 'NN', 2), ('counter', 'NN', 5)
            #verb_triple_as_list = list(verb_dobj_indobj_triple[0]) # ('Take', 'VB', 0)
            dobj_triple_as_list = list(verb_dobj_indobj_triple[1]) # ('knife', 'NN', 2)
            indobj_triple_as_list = list(verb_dobj_indobj_triple[2]) # ('counter', 'NN', 5)
            
            dobj_triple_as_list[0] = get_noun_hypernym(dobj_triple_as_list[0], hypernym_graph_obj) #change the first elements
            indobj_triple_as_list[0] = get_noun_hypernym(indobj_triple_as_list[0], hypernym_graph_obj)

            grounded_verb_dobj_indobj_triple = (verb_dobj_indobj_triple[0], tuple(dobj_triple_as_list), tuple(indobj_triple_as_list))
            grounded_verb_dobj_indobj_triples_in_sent.append(grounded_verb_dobj_indobj_triple)
        
        grounded_verb_dobj_indobj_per_sentence.append(grounded_verb_dobj_indobj_triples_in_sent)

    return grounded_verb_dobj_indobj_per_sentence

################################### causal relations 

def list_of_causal_rels_dict_to_source_target_pairs(causual_rels):
    # a dict is {'cause': 'wash', 'effect': 'cut', 'lag': 1, 'p_val': 2.123552583602068e-188}
    source_target_pairs = []
    for dict_caus_rel in causual_rels:
        pair = [dict_caus_rel.get('cause'), dict_caus_rel.get('effect')]
        if pair not in source_target_pairs:
           source_target_pairs.append(pair)
    
    return source_target_pairs

######################  list operations
def remove_dups_from_embedded_lists(list_of_lists):
    # filter out the empty lists
    list_of_lists = [ls for ls in list_of_lists if ls !=[] ]
    # list_of_lists : [ [ ["example, "example"] ] ]
    list_of_lists_new = []
    for idx, lst in enumerate(list_of_lists):
        if lst not in list_of_lists[:idx]:
            list_of_lists_new.append(lst)

    return list_of_lists_new

def remove_dups_from_list_of_lists(list_of_lists):

    idx_to_remove = []
    for ind, lst in enumerate(list_of_lists):
        if ind in idx_to_remove:
           continue
        else:
            for scnd_ind, scnd_lst in enumerate(list_of_lists[ind+1:], ind+1): 
                if Counter(scnd_lst) == Counter(lst):
                   idx_to_remove.append(scnd_ind)

    list_of_lists_wo_dups = [i for j, i in enumerate(list_of_lists) if j not in idx_to_remove]               
    
    return list_of_lists_wo_dups

def annotated_token_tuples_contain_verb(annotated_token_tuples):

    for annot_tuple in annotated_token_tuples:
        part_of_speech = annot_tuple[1]
        if "VB" in part_of_speech or "VBZ" in part_of_speech or "VBP" in part_of_speech  :
            return True

    return False

########### BEGIN EXTRACTING FROM SENTENCEWISE ############

def extract_obj_relations_as_list_from_sentencewise(rel_sentencewise):
    rel = []
    [rel.extend(rel_sent) for rel_sent in rel_sentencewise if rel_sent]

    return rel

def extract_properties_for_dobj_or_indobj_rels_sentencewise(dobj_rels_sentencewise, prop_rels_sentencewise):
    # dobj_rels_sentencewise like: [ [('dobj', ('take', 'VB', 0), ('knife', 'NN', 4))] ]
    # each sentence is a list of dobj tuples where the object is the 3rd element (see ("knife","NN", 4) above)
    dobj_prop_rels_sentencewise = []
    for sent_idx, dobj_rel_sent in enumerate(dobj_rels_sentencewise):
        dobj_props_sentence = []
        for dobj_rel in dobj_rel_sent:
            noun = dobj_rel[2] 
            prop_rels = [prop_rel for prop_rel in prop_rels_sentencewise[sent_idx] if noun in prop_rel]
            dobj_props_sentence.append((dobj_rel, prop_rels))

        dobj_prop_rels_sentencewise.append(dobj_props_sentence)
    
    return dobj_prop_rels_sentencewise


def write_to_file(filepath, text):
    with open(filepath, "w") as f:
         f.write(text)

def read_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    return content

if __name__ == "__main__":

    a = 1
    b = 1

"""
if __name__ == "__main__":
    
    list_of_lists_with_duplicates = [['cut', 'put'],['cut', 'put'], ['cut', 'put', 'take'], ['cut', 'take'], ['cut', 'take', 'put'], ['cut', 'wash'], ['put', 'take'],['cut', 'put'],['cut', 'put'], ['put', 'cut', 'take']]
    a = remove_dups_from_list_of_lists(list_of_lists_with_duplicates)

    [[[...]], [[...]], [[...]], [[...]], [[...]], [[...]], [[...]]]
    0:
    test_lst = [[['verbNoObj', 'whisk']], [['verbNoObj', 'whisk']],[['verbNoObj', 'is']],[['verbNoObj', 'stir']],[['verbNoObj', 'are']],[['verbNoObj', 'are']],[['verbNoObj', 'let']]]
"""