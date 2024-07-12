'''
This is the main script which will create a situation model
given an input text file with textual instructions

'''
import parser_subproc as stanford_parser
import initial_situation_model_builder as init_sit_model_builder
import os
import utils
import networkx as nx
import causual_relations_extender as causal_rels
import pddl_generator as pddl
import domain_knowledge_utils as domain_utils
import cause_effect_storage_handler as cause_effect_handler


EXTENSION_GRAPH_FILE = ".dot"

def run_text2hbm(domain_name = None,\
                 input_text_full_path = None,\
                 pddl_dir = None, \
                 stanford_parser_dir = None, \
                 graphs_dir = None,\
                 lowercase_bool = None,\
                 parser_correction_rules = None,\
                 output_format = None,
                 known_types_file = None,
                 extract_preconditions_effects_only = None
                 ):
    
    if extract_preconditions_effects_only:
        print("#### Extracting preconditions and effects only")


    '''
    TODO: when we have the known types we have to
     - mark the instances in the texts with "NN" tags (in that way we can tell the parser that the words are nouns)
     when marking the instances we should also make sure that 
     - extend the hypernym graph (hypernyms of the type instances will be the "known" types from the user-provided file)
     - 
    '''


    par = stanford_parser_dir + "*:" #stanford-parser-full-2018-02-27

    input_file_abs_path = os.path.abspath(input_text_full_path)

    types_instances:dict = None
    types_hierarchy:list = None


    #TODO: add parser_correction_rules param to parse_input_file
    if known_types_file:
    
        known_types_pretagged_input_file_abs_path = input_file_abs_path.split(".")[0] + "_domain_pretagged.txt"
        #notify the user where the pre-tagged file will be stored
        print("#####")
        print("Domain knowledge set by known_types_file will be used. This creates a pre_tagged copy of the input file and will be stored at:\n", known_types_pretagged_input_file_abs_path )
        print("#####")
        #read the whole text file and add domain knowledge
        abs_path_known_types_file = os.path.abspath(known_types_file)
        input_w_domain_knowledge,\
        types_instances,\
        types_hierarchy = domain_utils.add_known_types_to_input_and_get_types_dict_lst(input_file_abs_path, abs_path_known_types_file, lowercase_bool)
        # TODO: the tagged text has to be saved 
        utils.write_to_file(known_types_pretagged_input_file_abs_path, input_w_domain_knowledge)

        parsed_text_input = stanford_parser.parse_input_file(known_types_pretagged_input_file_abs_path, par, lowercase_bool, parser_correction_rules, use_known_types= True)
    else:
        parsed_text_input = stanford_parser.parse_input_file(input_file_abs_path, par, lowercase_bool, parser_correction_rules, use_known_types= False)


    #start the dependency extraction and get graph relations
    # Note that in  we lower-case the textual input, so that confusions regarding lower and upper case can be ignored
    # This should not be confused with the lower-casing step in the parameters of the text2HBM program's Cli
    # which is about lowercasing before using the parser

    list_dep_words_and_ann_sentence_tokens = stanford_parser.create_list_dep_words_and_ann_sentence_tokens(parsed_text_input)
    list_of_annotated_tokens_per_sentence = stanford_parser.create_list_of_annotated_tokens_for_annotated_sentence(parsed_text_input)
    
    dobj_rels_sentencewise, indobj_rels_sentencewise, prop_rels_sentencewise, vb_no_obj_rels_sentencewise = utils.filter_dobj_indobj_prop_vbnoobj_relations_sentencewise(list_dep_words_and_ann_sentence_tokens)
   
    prop_rels = utils.extract_obj_relations_as_list_from_sentencewise(prop_rels_sentencewise)
    
    dobj_rels_sentencewise = utils.remove_capitalization_in_dobj_indobj_rels_sentencewise(dobj_rels_sentencewise)
    indobj_rels_sentencewise = utils.remove_capitalization_in_dobj_indobj_rels_sentencewise(indobj_rels_sentencewise)
    vb_no_obj_rels_sentencewise = utils.remove_capitalization_in_vbnoobj_rels_sentencewise(vb_no_obj_rels_sentencewise)
   
    dobj_rels_sentencewise_with_properties = utils.extract_properties_for_dobj_or_indobj_rels_sentencewise(dobj_rels_sentencewise, prop_rels_sentencewise)
    indobj_rels_sentencewise_with_properties =  utils.extract_properties_for_dobj_or_indobj_rels_sentencewise(indobj_rels_sentencewise, prop_rels_sentencewise)
    #TODO: extract properties for actions without objects?
    
    #create the different kinds of actions together with their properties and the properties of the 
    #objects
    
    list_verb_dobj_indobj_prep_props_sentencewise = utils.create_lst_of_vb_dobj_indobj_prep_props_sentencewise(dobj_rels_sentencewise_with_properties, indobj_rels_sentencewise_with_properties)
   
    # extract the different types of actions and prepare them for type extraction
    dobj_existing_outside_vb_dobj_indobj_rels, dobj_existing_outside_vb_dobj_indobj_rels_sentwise = utils.extract_dobj_rels_with_props_existing_outside_vb_dobj_indobj_rels(dobj_rels_sentencewise_with_properties, list_verb_dobj_indobj_prep_props_sentencewise, return_sentencewise=True)
    indobj_existing_outside_vb_dobj_indobj_rels, indobj_existing_outside_vb_dobj_indobj_rels_sentwise = utils.extract_indobj_rels_with_props_existing_outside_vb_dobj_indobj_rels(indobj_rels_sentencewise_with_properties, list_verb_dobj_indobj_prep_props_sentencewise, return_sentencewise=True)
    vb_no_obj_rels = utils.extract_obj_relations_as_list_from_sentencewise(vb_no_obj_rels_sentencewise)
    verb_dobj_indobj_prep_props = utils.extract_obj_relations_as_list_from_sentencewise(list_verb_dobj_indobj_prep_props_sentencewise)

    #remove the indices and the tags
    #Later in the development we might find out that preserving the indices is important!
    dobj_existing_outside_vb_dobj_indobj_rels_sentwise_noidx = [utils.remove_idx_and_tag_from_dobj_props_rels(sent) for sent in dobj_existing_outside_vb_dobj_indobj_rels_sentwise]
    indobj_existing_outside_vb_dobj_indobj_rels_sentwise_noidx = [utils.remove_idx_and_tag_from_indobj_props_rels(sent) for sent in indobj_existing_outside_vb_dobj_indobj_rels_sentwise] 
    vb_no_obj_rels_sentwise_noidx = [utils.remove_idx_and_tag_from_vb_noobj_rels(sent) for sent in vb_no_obj_rels_sentencewise] 
    vb_dobj_indobj_prep_props_sentwise_noidx = [utils.remove_idx_and_tag_from_vb_dobj_indobj_prep_props(sent) for sent in list_verb_dobj_indobj_prep_props_sentencewise]

    action_dobj_props_noidx = utils.remove_idx_and_tag_from_dobj_props_rels(dobj_existing_outside_vb_dobj_indobj_rels)
    action_indobj_prep_prop_noidx = utils.remove_idx_and_tag_from_indobj_props_rels(indobj_existing_outside_vb_dobj_indobj_rels)
    action_noobj_noidx = utils.remove_idx_and_tag_from_vb_noobj_rels(vb_no_obj_rels)
    action_dobj_indobj_prep_prop_noidx =  utils.remove_idx_and_tag_from_vb_dobj_indobj_prep_props(verb_dobj_indobj_prep_props)

    action_dobj_props_noidx = utils.remove_dups_from_embedded_lists(action_dobj_props_noidx)
    action_indobj_prep_prop_noidx = utils.remove_dups_from_embedded_lists(action_indobj_prep_prop_noidx)
    action_noobj_noidx = utils.remove_dups_from_embedded_lists(action_noobj_noidx)
    action_dobj_indobj_prep_prop_noidx = utils.remove_dups_from_embedded_lists(action_dobj_indobj_prep_prop_noidx)

    # TODO:Lowercase
    verbs_nouns_whole_text = utils.extract_verbs_and_nouns_from_parsed_text(list_of_annotated_tokens_per_sentence, lowercase_bool)
    verbs_whole_text = verbs_nouns_whole_text[0]
    nouns_whole_text = verbs_nouns_whole_text[1]

    # TODO: extract modals!
    if not extract_preconditions_effects_only:

        file_path_hypernym_graph = graphs_dir + "initial_hypernym_graph_" + domain_name + EXTENSION_GRAPH_FILE
        file_path_graph_initial_situation_model = graphs_dir + "initial_situation_model_" + domain_name + EXTENSION_GRAPH_FILE
        ###
        file_path_extended_initial_situation_model = graphs_dir + "initial_situation_model_" + domain_name + EXTENSION_GRAPH_FILE
        file_path_extended_initial_situation_model_with_actions = graphs_dir + "initial_situation_model_with_actions_" + domain_name + EXTENSION_GRAPH_FILE
        file_path_graph_initial_with_actions_and_properties = graphs_dir + "initial_situation_model_with_actions_and_properties_" + domain_name + EXTENSION_GRAPH_FILE
        file_path_graph_with_causal_rels = graphs_dir + "situation_model_with_causal_relations_" + domain_name + EXTENSION_GRAPH_FILE

    #second, create a hypenym hierarchy graph

    hypernym_graph = None
    
    if known_types_file:
    #testing knowledge transfer/merge
        file_merged_domain_knowledge_graph = graphs_dir + "TEST_MERGE_initial_hypernym_graph_" + domain_name + EXTENSION_GRAPH_FILE
        hypernym_graph_domain = init_sit_model_builder.build_initial_hypernym_graph_with_domain_knowledge(input_words = nouns_whole_text,\
                                                                                                        types_instances= types_instances,\
                                                                                                        types_hierarchy = types_hierarchy,\
                                                                                                        graph_export_path = file_merged_domain_knowledge_graph)
        hypernym_graph = hypernym_graph_domain
    else:
        
        hypernym_graph = init_sit_model_builder.build_initial_hypernym_graph(nouns_whole_text) 

        if not extract_preconditions_effects_only:
            nx.drawing.nx_pydot.write_dot(hypernym_graph, file_path_hypernym_graph)
        # the initial model contains only nouns with their hyperonyms (but we search for the most common hypernyms between words in the hierarchy and perform pruning)
    

    
    # TODO: check if it is really a good idea to prune until node which has multiple parents or maybe 
    # leave the intermediate hypenym in the graph
    initial_situation_model = init_sit_model_builder.build_initial_situation_model(nouns_whole_text) 
   
    if not extract_preconditions_effects_only:

       nx.drawing.nx_pydot.write_dot(initial_situation_model, file_path_graph_initial_situation_model)

    # TODO : put all .write_dot calls outside the methods (facilitates w)


    if not extract_preconditions_effects_only:

       file_path_graph_initial_situation_model_with_intermediate_hypernyms =  graphs_dir + "initial_situation_model_with_direct_hypernyms_" + domain_name + EXTENSION_GRAPH_FILE

    initial_situation_model_with_intermediate_hypernym = init_sit_model_builder.build_initial_situation_model_with_intermediate_hypernym(nouns_whole_text, hypernym_graph) 
   
    if not extract_preconditions_effects_only:
       

       nx.drawing.nx_pydot.write_dot(initial_situation_model_with_intermediate_hypernym, file_path_graph_initial_situation_model_with_intermediate_hypernyms)



    dobj_rels, indobj_rels, prop_rels = utils.filter_dobj_indobj_prop_relations(list_dep_words_and_ann_sentence_tokens)
    properties = utils.extract_properties_from_prop_rels(prop_rels)
    
    # create grounded tuples for rule generation
    #grounded_verb_dobj_indobj_tuples = utils.create_grounded_verb_dobj_indobj_triples(verb_dobj_indobj, hypernym_graph)
    
    # the extended model contains the nouns, their hyperonyms and the relationships (extracted from the dependencies)
    relations_in_situation_model = indobj_rels + dobj_rels + prop_rels

    graph_of_all_relationships = causal_rels.create_graph_for_all_relations(relations_in_situation_model)

    extended_model = init_sit_model_builder.unite_graphs(initial_situation_model_with_intermediate_hypernym, graph_of_all_relationships)
    extended_model_with_actions = init_sit_model_builder.add_actions_to_model(extended_model, verbs_whole_text)
    extended_model_with_properties = init_sit_model_builder.add_properties_to_model(extended_model_with_actions, properties)

    
    if not extract_preconditions_effects_only:

        nx.drawing.nx_pydot.write_dot(extended_model, file_path_extended_initial_situation_model)
        nx.drawing.nx_pydot.write_dot(extended_model_with_actions, file_path_extended_initial_situation_model_with_actions)
        nx.drawing.nx_pydot.write_dot(extended_model_with_properties, file_path_graph_initial_with_actions_and_properties)



    vectors_dobj_only = causal_rels.create_vector_representation_of_any_relationship(action_dobj_props_noidx, dobj_existing_outside_vb_dobj_indobj_rels_sentwise_noidx, return_objects = True)
    vector_indobj_only = causal_rels.create_vector_representation_of_any_relationship(action_indobj_prep_prop_noidx, indobj_existing_outside_vb_dobj_indobj_rels_sentwise_noidx, return_objects = True)
    vector_actions_noobj = causal_rels.create_vector_representation_of_any_relationship(action_noobj_noidx, vb_no_obj_rels_sentwise_noidx, return_objects = True)
    vector_action_dobj_indobj = causal_rels.create_vector_representation_of_any_relationship(action_dobj_indobj_prep_prop_noidx, vb_dobj_indobj_prep_props_sentwise_noidx, return_objects = True)


    all_relationships_vectors = dict(list(vectors_dobj_only.items()) +\
                                list(vector_indobj_only.items()) +\
                                list(vector_actions_noobj.items()) +\
                                list(vector_action_dobj_indobj.items()))
                            
    
    # added 02.05.22
    # here we create causal relations between combinations of vb + dobj
    #res_causal_rels_action_dobj, res_causal_rels_action_dobj_all  = causal_rels.calculate_granger_for_actions(dict_act_dobj_rels_vectors)
    res_causal_rels_all, res_causal_rels_all_detailed = causal_rels.calculate_granger_for_actions(all_relationships_vectors)
    cyclic_rels = causal_rels.find_direct_cyclic_causal_relations_in_dict_list(res_causal_rels_all)


    causal_rels_dicts = init_sit_model_builder.convert_causal_relations_objects_list_to_dicts(res_causal_rels_all)
    extended_model_with_caus_rels = init_sit_model_builder.add_causal_rels_to_model(extended_model_with_actions, causal_rels_dicts)
    #causal_rels_as_list_of_source_target_pairs = utils.list_of_causal_rels_dict_to_source_target_pairs(causual_rels)
    
    if not extract_preconditions_effects_only:

        nx.drawing.nx_pydot.write_dot(extended_model_with_caus_rels, file_path_graph_with_causal_rels)
    

    constants_in_txt = nouns_whole_text

    
    if not extract_preconditions_effects_only:
  
        domain_file_path = pddl_dir + domain_name + "_domain.pddl"
        problem_file_path = pddl_dir + domain_name + "_problem.pddl"
        domain_problem_name = domain_name

    if extract_preconditions_effects_only:
        filename_extracted_prec_eff = input_file_abs_path.rsplit(".", 1)[0].split("/")[-1] + "_preconditions_effects" + ".csv"
        for idx_rel, rel in enumerate(res_causal_rels_all):
            cause = rel["cause"]
            effect = rel["effect"]
            cause_effect_handler.store_causal_relations(cause, effect, filename_extracted_prec_eff, pddl_dir, idx_rel, len(res_causal_rels_all))

    if not extract_preconditions_effects_only:

        pddl.generate_domain_and_problem_files(actions_no_obj_rels = action_noobj_noidx ,
                                                        actions_dobj_rels = action_dobj_props_noidx,
                                                        actions_indobj_rels = action_indobj_prep_prop_noidx ,
                                                        actions_dobj_indobj_rels = action_dobj_indobj_prep_prop_noidx,
                                                        causal_relations = res_causal_rels_all ,
                                                        constants = constants_in_txt,
                                                        hypernym_graph = hypernym_graph,
                                                        property_relations = prop_rels,
                                                        domain_problem_name = domain_problem_name,
                                                        path_domain_file = domain_file_path,
                                                        path_problem_file = problem_file_path,
                                                        output_format = output_format
                                                        )


