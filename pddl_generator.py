from typing import Tuple
from typing import List
import itertools
import utils
import relationship_types as rel_types
from relation import VbDobjRelationWithProperties, VbDobjIndobjRelationWithProperties, VbNoobjRelation, VbIndObjRelationWithProperties
import output_formats
import networkx

#GENERAL TODO: maybe define some parsed annotations such as "dobj" into CONSTANTS and replace them in the code?

PREDEFINED_TYPES_LIST = ["act - process"]
PREDEFINED_CONSTANTS_TYPES_DICT = {"ACTION":"act"}
GLOBAL_WHITESPACE_REPLACEMENT = "_"
PROPERTY_PREDICATE_PREFIX = "is"# e.g. isBlue, isGreen
SUFFIX_EXECUTED_ACTION = "-executed"
SUFFIX_EXECUTING_EFFECT_ACTION = "-executing" # for the predicates in the effects
SUFFIX_DOBJ_TEMPLATE = "Dobj"
SUFFIX_INDOBJ_TEMPLATE = "IndObj"
SUFFIX_NOOBJ_TEMPLATE = "NoObj"
SUFFIX_DOBJ_INDOBJ = SUFFIX_DOBJ_TEMPLATE + SUFFIX_INDOBJ_TEMPLATE

HYPERNYM_GRAPH_INITIAL_NODE = "entity" # in wordnet entity is the initial node

################ BEGIN types definitions functions 

def search_for_types_recursively(hypernym_graph, start_node_name, found_ordered_types, rec_depth = 0):
	successors = list(hypernym_graph.successors(start_node_name))
	successor = None
	if len(successors)>0:
		successor = successors[0]
	else:
		return found_ordered_types
	if rec_depth == 0:
		found_ordered_types.append(successor)
	new_rec_depth = rec_depth + 1
	predecessors = list(hypernym_graph.predecessors(successor))
	if len(predecessors)>1:
		found_ordered_types.append(successor)
		return search_for_types_recursively(hypernym_graph, successor, found_ordered_types, rec_depth = new_rec_depth)
	else:
		return search_for_types_recursively(hypernym_graph, successor, found_ordered_types, rec_depth = new_rec_depth)

def format_type_word_replacing_whitespace(type_word, whitespace_repl = GLOBAL_WHITESPACE_REPLACEMENT):
	type_word = type_word.replace(" ", whitespace_repl)

	return type_word

################ END types definitions functions


################ BEGIN subtemplates 

def add_property(action : str, list_of_properties : List[Tuple[str,str]])->str:
    """
    list of properties example: [("from","table")]

	addProperty :: String -> [(String,String)] -> String
	addProperty _ [] = ""
	addProperty a ((d,e):xs)
		 | a /= e = "(property-" ++ d ++ " ?" ++ e ++ ")\n \t \t \t" ++ addProperty a xs
		 | otherwise = "(property-" ++ d ++ ")\n \t \t \t" ++ addProperty a xs

	"""
    if len(list_of_properties) == 0:
       return ""
    else:
       template = ""
       for prop in list_of_properties:
           if  action != prop[1]:
               template = template + "(property-" + prop[0] + " ?" + prop[1] + ")\n \t \t \t"
           else:
               template = "(property-" + prop[0] + ")\n \t \t \t"
    return template   
		
################ END subtemplates

################ BEGIN predicates generation
# TODO MAY, 2022

def transform_action_rel_tuples_to_objects(action_rel_tuple_list, rel_type):
	list_rels = []
	if rel_type == rel_types.DOBJ_RELATIONSHIP:
		list_rels = [VbDobjRelationWithProperties(rel[0], rel[1]) for rel in action_rel_tuple_list ]
	if rel_type == rel_types.INDOBJ_RELATIONSHIP:
		list_rels = [VbIndObjRelationWithProperties(rel[0], rel[1], rel[2]) for rel in action_rel_tuple_list ]
	if rel_type == rel_types.VBNOOBJ_RELATIONSHIP:
		list_rels = [VbNoobjRelation(rel[0]) for rel in action_rel_tuple_list ]
	if rel_type == rel_types.VB_DOBJ_INDOBJ_RELATIONSHIP:
		list_rels = [VbDobjIndobjRelationWithProperties(rel[0], rel[1], rel[2]) for rel in action_rel_tuple_list ]	
	
	return list_rels

def generate_domain_and_problem_files(actions_no_obj_rels = None, 
												actions_dobj_rels = None,
											    actions_indobj_rels = None,
												actions_dobj_indobj_rels = None,
												causal_relations = None,
												constants = None,
												hypernym_graph = None,
												property_relations = None,
												domain_problem_name = None,
												path_domain_file = None,
												path_problem_file = None,
												output_format = None):

	types = []
	predicates = []
	predicates_executed_actions = []
	predicates_effects = []
	functions = []
	activity_id_templates = []

	executed_actions_for_goal_definition = []

	action_templates = []

	actions_no_obj_rels = transform_action_rel_tuples_to_objects(actions_no_obj_rels, rel_type = rel_types.VBNOOBJ_RELATIONSHIP)
	actions_dobj_rels = transform_action_rel_tuples_to_objects(actions_dobj_rels, rel_type = rel_types.DOBJ_RELATIONSHIP)
	actions_indobj_rels = transform_action_rel_tuples_to_objects(actions_indobj_rels, rel_type = rel_types.INDOBJ_RELATIONSHIP)
	actions_dobj_indobj_rels = transform_action_rel_tuples_to_objects(actions_dobj_indobj_rels, rel_type = rel_types.VB_DOBJ_INDOBJ_RELATIONSHIP)
	
	activity_id_idx = 0

	for action_no_obj in actions_no_obj_rels:
		#increase the activity-id (it starts by idx 1)
		activity_id_idx += 1

		#action_no_obj is a list such as [["vbNoobj", "eat"]]
		#TODO: actions without objects should have properties (for example adverbs such as slowly, thoroughly)
		preconditions, effects = find_preconditions_effects_from_a_caus_rel_list_of_dicts(action_no_obj, causal_relations )
		template_action_noobj, precondition_properties_types_templates, effect_properties_types_templates, current_action_executed_predicate, exec_actions_constants, exec_effects_predicates, str_activity_name_id = generate_template_for_action_no_obj_and_extract_global_predicates_for_types_and_constants(action_no_obj, preconditions, effects, constants, hypernym_graph, output_format, activity_id_idx)
		
		activity_id_templates.append(str_activity_name_id)

		predicates.append(precondition_properties_types_templates)
		predicates.append(effect_properties_types_templates)

		predicates_effects.extend(exec_effects_predicates)
		predicates_executed_actions.append(current_action_executed_predicate) # needed to put the string into a list so that we can join() the predicates easier later on
		action_templates.append(template_action_noobj)
		executed_actions_for_goal_definition.append(exec_actions_constants)
	
	for action_with_dobj in actions_dobj_rels:
		#increase the activity-id (it starts by idx 1)
		activity_id_idx += 1

		preconditions, effects = find_preconditions_effects_from_a_caus_rel_list_of_dicts(action_with_dobj, causal_relations )
		template_action_dobj, precondition_properties_types_templates, effect_properties_types_templates, current_action_executed_predicate, exec_actions_constants, exec_effects_predicates, str_activity_name_id = generate_template_for_action_dobj_and_extract_global_predicates_for_types_and_constants(action_with_dobj, preconditions, effects, constants, hypernym_graph, output_format, activity_id_idx) 
		
		activity_id_templates.append(str_activity_name_id)

		predicates.append(precondition_properties_types_templates)
		predicates.append(effect_properties_types_templates)
		predicates_executed_actions.append(current_action_executed_predicate)

		predicates_effects.extend(exec_effects_predicates)
		
		action_templates.append(template_action_dobj)
		executed_actions_for_goal_definition.append(exec_actions_constants)

	for action_with_indobj in actions_indobj_rels:
		#increase the activity-id (it starts by idx 1)
		activity_id_idx += 1

		preconditions, effects = find_preconditions_effects_from_a_caus_rel_list_of_dicts(action_with_indobj, causal_relations )
		template_action_indobj, precondition_properties_types_templates, effect_properties_types_templates, current_action_executed_predicate, exec_actions_constants, exec_effects_predicates, str_activity_name_id = generate_template_for_action_indobj_and_extract_global_predicates_for_types_and_constants(action_with_indobj, preconditions, effects, constants, hypernym_graph, output_format, activity_id_idx)
		
		activity_id_templates.append(str_activity_name_id)

		predicates.append(precondition_properties_types_templates)
		predicates.append(effect_properties_types_templates)
		predicates_executed_actions.append(current_action_executed_predicate)
		
		predicates_effects.extend(exec_effects_predicates)

		action_templates.append(template_action_indobj)
		executed_actions_for_goal_definition.append(exec_actions_constants)

	for action_dobj_indobj in actions_dobj_indobj_rels:
		#increase the activity-id (it starts by idx 1)
		activity_id_idx += 1

		preconditions, effects = find_preconditions_effects_from_a_caus_rel_list_of_dicts(action_dobj_indobj, causal_relations )
		template_action_dobj_indobj, precondition_properties_types_templates, effect_properties_types_templates, current_action_executed_predicate, exec_actions_constants, exec_effects_predicates, str_activity_name_id = generate_template_for_action_dobj_indobj_and_extract_global_predicates_for_types_and_constants(action_dobj_indobj, preconditions, effects, constants, hypernym_graph, output_format, activity_id_idx)
		
		activity_id_templates.append(str_activity_name_id)

		predicates.append(precondition_properties_types_templates)
		predicates.append(effect_properties_types_templates)
		predicates_executed_actions.append(current_action_executed_predicate)
		
		predicates_effects.extend(exec_effects_predicates)

		action_templates.append(template_action_dobj_indobj)
		executed_actions_for_goal_definition.append(exec_actions_constants)

	predicates_effects = list(set(predicates_effects))
	predicates_executed_actions = list(set(predicates_executed_actions))
	predicates = utils.remove_dups_from_embedded_lists(predicates)

	if property_relations == [] and output_format == output_formats.PDDL:
		predicates.append(["(isInit)"])

	################### TODO: implement it clean (currently only a test!)
	
	domain_title_template = generate_domain_title_template(domain_problem_name, output_format)
	types_templates, constant_type_templates = create_types_and_constants_templates(constants, hypernym_graph)
	# concatenate all types of predicates
	predicates_templates = merge_lists_of_predicates_and_create_template(predicates, predicates_executed_actions, predicates_effects)
	action_templates = "\n".join(action_templates)
	domain_txt_to_file = "".join([domain_title_template, types_templates, predicates_templates, action_templates, "\n)" ])
	
	write_file(file_name = path_domain_file, text_to_write = domain_txt_to_file)
	
	# for the problem file
	problem_title_template = generate_problem_title_template(domain_problem_name)
	problem_objects = constant_type_templates

	problem_predicates = None
	if property_relations == [] and output_format == output_formats.PDDL:
		problem_predicates= generate_initial_problem_predicates_when_no_properties()
	else:
		problem_predicates= generate_initial_problem_predicates_with_constants(property_relations, activity_id_templates)
	
	   	
	problem_goal = generate_problem_goal_template(executed_actions_for_goal_definition) # we first set the goal to be the completion of all actions
	problem_txt_to_file = "".join([problem_title_template, problem_objects, problem_predicates, problem_goal])
	write_file(file_name = path_problem_file, text_to_write = problem_txt_to_file)
	

	print("Predicates generated")

def generate_domain_title_template(domain_name, output_format):

	requirements_tmpl = ""
	if output_format == output_formats.PDDL:
		requirements_tmpl = "\n \n \t \t" +\
			"( :requirements" +\
			"\n \t \t " + ":strips" +\
			"\n \t \t " + ":negative-preconditions" +\
			"\n \t \t " + ":equality" +\
			"\n \t \t " + ":typing" +\
			"\n \t \t " + ":adl" +\
			"\n \t \t" + ")"+\
			"\n \t \t"
	templ = "(define (domain " + domain_name + " )" +\
			requirements_tmpl
	
	return templ

def generate_problem_title_template(domain_name):

	templ = "(define (problem " + domain_name + " )" +\
		    "\n \t \t" +\
			"(:domain " + domain_name + " )" + "\n"

	return templ

def generate_problem_goal_template(predicates_executed_actions):
	predicates_executed_actions = ["("+ p + ")" for p in predicates_executed_actions]
	indent_and_predicate = "\n \t \t \t"
	indent_goal_predicates = "\n \t \t \t \t"
	start_templ = "\n \t \t" + "(:goal" + indent_and_predicate + "(and " + indent_goal_predicates
	problem_goals = indent_goal_predicates.join(predicates_executed_actions)
	goal_definition = start_templ + problem_goals + indent_and_predicate + ")" +"\n \t \t)" + "\n)"

	return goal_definition

def generate_initial_problem_predicates_with_constants(all_property_relations, activity_id_templates):
	'''
	in the problem file we generate the initial predicates by using the properties which
	occur in the text. 
	TODO: this does not take into account dynamic properties!
	'''
	if None in activity_id_templates:
		activity_id_templates = [""]

	template_init = "\n\n \t \t(:init "
	indent = "\n \t \t"
	indent_predicates = "\n \t \t \t"

	template_init = template_init + indent
	
	prop_const_predicates = []

	for property_rel in all_property_relations:
		property_adjective = property_rel[2][0]
		property_noun = property_rel[1][0] # this is a constant in the pddl domain
		prop_predicate = PROPERTY_PREDICATE_PREFIX + property_adjective.capitalize()
		prop_const_predicate ="(" + prop_predicate + " " + property_noun + ")"
		prop_const_predicates.append(prop_const_predicate)

	comment_activity_ids = indent_predicates + "#activity ids for observations"
	if activity_id_templates == []:
		comment_activity_ids = ""

	template_init = template_init +indent_predicates + \
				    indent_predicates.join(prop_const_predicates) +\
				    indent_predicates +\
				    comment_activity_ids +\
				    indent_predicates +\
				    indent_predicates.join(activity_id_templates)+\
					indent + ")" 

	return template_init

def generate_initial_problem_predicates_when_no_properties():
	# when there are no properties, we can't generate
	# initial state predicates in the problem file
	# that is why we can just create a dummy state called "Init"
	# and a predicate isInit which is always true
	
	template_init = "\n\n \t \t(:init "
	indent = "\n \t \t"
	indent_predicates = "\n \t \t \t"
	template_init = template_init + indent
	template_init = template_init +indent_predicates + \
				    "(isInit)"+\
					indent + ")" 
	
	return template_init

def create_types_and_constants_templates(consts, hypernym_graph):
	
	indentation_title = "\n \t \t"
	indentation_entities = "\n \t \t \t"
	types_templates = []
	constants_types_templates = []
	for c in consts:
		c_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(c, hypernym_graph))
		types_templates.append(c_type)
		constants_types_templates.append(c + " - " + c_type)
	
	types_templates = list(set(types_templates))
	constants_types_templates = list(set(constants_types_templates))


	types_templates = indentation_title +\
					  "(:types" +\
					  indentation_entities +\
					  (indentation_entities).join(types_templates)+\
					  indentation_title + ")" +\
					  indentation_title
	
	consts_types_template = indentation_title +\
							"(:objects" +\
						    indentation_entities +\
							(indentation_entities).join(constants_types_templates)+\
							indentation_title + ")"
	
	return types_templates, consts_types_template

def merge_lists_of_predicates_and_create_template(predicates_tuples, predicates_strings, predicates_list_formatted):
	
	# remove predicates from the string-format predicates 
	predicates_strings = list(set(predicates_strings)) 

	# we first add ( ) to the predicates 
	predicates_strings_with_brackets = ["("+pred +")" for pred in predicates_strings]
	predicates_strings_with_brackets.extend(predicates_list_formatted)
	#define indentations and template
	indentation = "\n \t \t"
	indentation_predicates = "\n \t \t \t"
	pred_begin = "(:predicates"
	merged_lists_preds = list(itertools.chain.from_iterable(predicates_tuples))
	#remove duplicates
	merged_lists_preds = list(set(merged_lists_preds))

	predicates_template = indentation +\
						  pred_begin +\
						  indentation_predicates +\
						  indentation_predicates.join(merged_lists_preds) +\
						  indentation_predicates +\
						  (indentation_predicates).join(predicates_strings_with_brackets) +\
						  indentation + ")" +\
						  indentation

	return predicates_template

def write_file(file_name, text_to_write):
	with open(file_name, 'a+', encoding='utf-8') as f:
    	 f.write(text_to_write)

def test_write(a = "output_pddl.txt", text = None):
	with open(a, 'a+', encoding='utf-8') as f:
    	 f.write(text)

def generate_preconditions_templates_for_actions_types_and_constants(action, preconditions, constants, hypernym_graph):

	precondition_properties_types_templates = []
	precondition_properties_constants_templates = []
	precondition_actions_templates = []

	for precond in preconditions:
		if isinstance(precond, VbDobjRelationWithProperties):
			act = precond.get_verb()
			dobj = precond.get_dobj()
			dobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(dobj, hypernym_graph))
			properties = precond.get_properties()

			properties_templates_with_types, properties_templates_with_constants = convert_properties_to_predicates_with_types_and_constants(properties, hypernym_graph)
			precond_action_predicate_name = act + dobj_type.capitalize()  + SUFFIX_EXECUTED_ACTION 
			precond_action_predicate_template = "(" + precond_action_predicate_name +" " + dobj + ")"
			
			precondition_properties_types_templates.extend(properties_templates_with_types)
			precondition_properties_constants_templates.extend(properties_templates_with_constants)
			precondition_actions_templates.append(precond_action_predicate_template)			
		
		if isinstance(precond, VbDobjIndobjRelationWithProperties):
			act = precond.get_verb()
			dobj = precond.get_dobj()
			indobj = precond.get_indobj()
			dobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(dobj, hypernym_graph))
			indobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(indobj, hypernym_graph))
			preposition = precond.get_preposition()

			properties = precond.get_properties()
			#precondition_properties.append([generate_property_predicate_template(prop, hypernym_graph) for prop in properies])
			
			properties_templates_with_types, properties_templates_with_constants = convert_properties_to_predicates_with_types_and_constants(properties, hypernym_graph)
			precond_action_predicate_name = act + dobj_type.capitalize() + preposition.capitalize() + indobj_type.capitalize() + SUFFIX_EXECUTED_ACTION 
			precond_action_predicate_template = "(" + precond_action_predicate_name + " " + dobj + " " + indobj + ")"
			
			precondition_properties_types_templates.extend(properties_templates_with_types)
			precondition_properties_constants_templates.extend(properties_templates_with_constants)
			precondition_actions_templates.append(precond_action_predicate_template)

		if isinstance(precond, VbIndObjRelationWithProperties):
			act = precond.get_verb()
			indobj = precond.get_indobj()
			indobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(indobj, hypernym_graph))
			preposition = precond.get_preposition()

			properties = precond.get_properties()
			#precondition_properties.append([generate_property_predicate_template(prop, hypernym_graph) for prop in properies])
			
			properties_templates_with_types, properties_templates_with_constants = convert_properties_to_predicates_with_types_and_constants(properties, hypernym_graph)
			precond_action_predicate_name = act + preposition.capitalize() + indobj_type.capitalize() + SUFFIX_EXECUTED_ACTION 
			precond_action_predicate_template = "(" + precond_action_predicate_name + " " + indobj + ")"
			
			precondition_properties_types_templates.extend(properties_templates_with_types)
			precondition_properties_constants_templates.extend(properties_templates_with_constants)
			precondition_actions_templates.append(precond_action_predicate_template)

		if isinstance(precond, VbNoobjRelation):
			act = precond.get_verb()
			precond_action_predicate_name = act + SUFFIX_NOOBJ_TEMPLATE + SUFFIX_EXECUTED_ACTION 
			precond_action_predicate_template = "(" + precond_action_predicate_name + ")"
			precondition_actions_templates.append(precond_action_predicate_template)


	return precondition_properties_types_templates, precondition_properties_constants_templates, precondition_actions_templates

def generate_effects_templates_for_actions_types_and_constants(action, effects, constants, hypernym_graph):
	'''
	TODO: At the moment this function looks  almost the same way as the function
	generate_preconditions_templates_for_actions_types_and_constants does
	Both functions have not been merged since we don't know at this stage how 
	different the generation of the effects predicates could be when adding counters, etc.
	'''

	effect_properties_types_templates = []
	effect_properties_constants_templates = []
	effect_actions_templates = []
	effect_actions_predicates_with_obj_types = []

	for effect in effects:
		if isinstance(effect, VbDobjRelationWithProperties):
			act = effect.get_verb()
			dobj = effect.get_dobj()
			dobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(dobj, hypernym_graph))
			properties = effect.get_properties()

			properties_templates_with_types, properties_templates_with_constants = convert_properties_to_predicates_with_types_and_constants(properties, hypernym_graph)
			
			#effect_action_predicate_name = act + dobj_type.capitalize() + SUFFIX_EXECUTING_EFFECT_ACTION  
			#effect_action_predicate_template = "(" + effect_action_predicate_name +" " + dobj + ")"

			#effect_action_predicate_with_type = "(" + effect_action_predicate_name +" ?o - " + dobj_type + ")"
			#effect_actions_predicates_with_obj_types.append(effect_action_predicate_with_type)
			
			effect_properties_types_templates.extend(properties_templates_with_types)
			effect_properties_constants_templates.extend(properties_templates_with_constants)
			#effect_actions_templates.append(effect_action_predicate_template)			
		
		if isinstance(effect, VbDobjIndobjRelationWithProperties):
			act = effect.get_verb()
			dobj = effect.get_dobj()
			indobj = effect.get_indobj()
			dobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(dobj, hypernym_graph))
			indobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(indobj, hypernym_graph))
			preposition = effect.get_preposition()

			properties = effect.get_properties()
			#effect_properties.append([generate_property_predicate_template(prop, hypernym_graph) for prop in properies])
			
			properties_templates_with_types, properties_templates_with_constants = convert_properties_to_predicates_with_types_and_constants(properties, hypernym_graph)
			#effect_action_predicate_name = act + dobj_type.capitalize() + preposition.capitalize() + indobj_type.capitalize() + SUFFIX_EXECUTING_EFFECT_ACTION
			#effect_action_predicate_template = "(" + effect_action_predicate_name + " " + dobj + " " + indobj + ")"
			
			#effect_action_predicate_with_type = "(" + effect_action_predicate_name +" ?o - " + dobj_type + " ?i - " + indobj_type +")"
			#effect_actions_predicates_with_obj_types.append(effect_action_predicate_with_type)

			effect_properties_types_templates.extend(properties_templates_with_types)
			effect_properties_constants_templates.extend(properties_templates_with_constants)
			#effect_actions_templates.append(effect_action_predicate_template)

		if isinstance(effect, VbIndObjRelationWithProperties):
			act = effect.get_verb()
			indobj = effect.get_indobj()
			indobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(indobj, hypernym_graph))
			preposition = effect.get_preposition()

			properties = effect.get_properties()
			#effect_properties.append([generate_property_predicate_template(prop, hypernym_graph) for prop in properies])
			
			properties_templates_with_types, properties_templates_with_constants = convert_properties_to_predicates_with_types_and_constants(properties, hypernym_graph)
			#effect_action_predicate_name = act + preposition.capitalize() + indobj_type.capitalize() + SUFFIX_EXECUTING_EFFECT_ACTION
			#effect_action_predicate_template = "(" + effect_action_predicate_name + " " + indobj + ")"

			#effect_action_predicate_with_type = "(" + effect_action_predicate_name + " ?i - " + indobj_type +")"
			#effect_actions_predicates_with_obj_types.append(effect_action_predicate_with_type)
			
			effect_properties_types_templates.extend(properties_templates_with_types)
			effect_properties_constants_templates.extend(properties_templates_with_constants)
			#effect_actions_templates.append(effect_action_predicate_template)

		if isinstance(effect, VbNoobjRelation):
			act = effect.get_verb()
			#effect_action_predicate_name = act + SUFFIX_NOOBJ_TEMPLATE + SUFFIX_EXECUTING_EFFECT_ACTION
			#effect_action_predicate_template = "(" + effect_action_predicate_name + ")"
			#effect_actions_templates.append(effect_action_predicate_template)

			#effect_actions_predicates_with_obj_types.append(effect_action_predicate_template)

	return effect_properties_types_templates, effect_properties_constants_templates, effect_actions_templates, effect_actions_predicates_with_obj_types

def convert_properties_to_predicates_with_types_and_constants(properies_relations, hypernym_graph):
	#returns two lists properties_template_with_types, properties_template_with_constants
	properties_template_with_constants= []
	properties_template_with_types = []

	for property_rel in properies_relations:
		property_adjective = property_rel[2]
		property_noun = property_rel[1] # this is a constant in the pddl domain
		prop_predicate = PROPERTY_PREDICATE_PREFIX + property_adjective.capitalize() 
		object_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(property_noun, hypernym_graph))
		prop_predicate_template_with_constant = "("+ prop_predicate + " " + property_noun + ")"	
		prop_predicate_template_with_type = "("+ prop_predicate + " ?o - " + object_type + ")"
		
		properties_template_with_constants.append(prop_predicate_template_with_constant)
		properties_template_with_types.append(prop_predicate_template_with_type)

	return 	properties_template_with_types, properties_template_with_constants

def generate_template_for_action_no_obj_and_extract_global_predicates_for_types_and_constants(action, preconditions, effects, constants, hypernym_graph, output_format, activity_id_idx):
	# This function returns a template for an action, predicate for the types and the constants which were contained in the preconditions and effects
	# These predicates look like: "isRed knife" for a constant "knife" and "isRed ?o - edge_tool" for the type of the constant.  
	# We put the generated predicates in the global scope of the pddl domain file under (:predicates ..... )
	# action is like [['verbNoObj', 'smile']]
	# 

	#TODO may 2022, instead of searching in the hypernym graph, just use a dictinary noun -> hypernym
	# this will optimize the speed a bit
	act = action.get_verb()
	precondition_properties_types_templates, precondition_properties_constants_templates, precondition_actions_templates = generate_preconditions_templates_for_actions_types_and_constants(action, preconditions, constants, hypernym_graph)
	preconditions_all = precondition_actions_templates + precondition_properties_constants_templates
	#preconditions_all_string = merge_templates(preconditions, indentation = '')

	#generate the effects

	effect_properties_types_templates, effect_properties_constants_templates, effect_actions_templates, effect_predicates_w_types = generate_effects_templates_for_actions_types_and_constants(action, effects, constants, hypernym_graph)
	effects_all = effect_actions_templates# + effect_properties_constants_templates

	action_name = act + SUFFIX_NOOBJ_TEMPLATE
	current_action_executed_predicate =  action_name + SUFFIX_EXECUTED_ACTION 

	executed_action_with_constants = current_action_executed_predicate #predicates with constants are needed later on when we define the goal in the problem file 

	'''
	removed:
	 "(not taskFinished)"+ \
			   "\n \t \t \t \t" + \
	'''

	str_activity_name_id = None #this comes into the problem.pddl later
	activity_line = ""
	if output_format == output_formats.CCBM:
		activity_line = "\n \t \t \t:observation (setActivity (activity-id {} ))".format(action_name)
		str_activity_name_id = "(= ( activity-id {} ) {})".format(action_name, activity_id_idx)

	action_template = "\n \t \t" +\
			   "(:action " + action_name +\
			   "\n \t \t \t" + \
		       ":parameters ()" +\
			   "\n \t \t \t" +\
			   ":precondition (and"+ \
			   "\n \t \t \t \t" + \
			   "\n \t \t \t \t".join(preconditions_all) +\
			   ")"+\
			   "\n \t \t \t" + \
			   ":effect (and"+ \
			   "\n \t \t \t \t" + \
			   "(" + \
			   current_action_executed_predicate + \
			   ")" +\
			   "\n \t \t \t \t" + \
			   "\n \t \t \t \t".join(effect_actions_templates) +\
			   ")"+\
			   activity_line +\
			   "\n \t \t)"
	return action_template,\
		   precondition_properties_types_templates,\
		   effect_properties_types_templates,\
		   current_action_executed_predicate,\
		   executed_action_with_constants,\
		   effect_predicates_w_types,\
		   str_activity_name_id	   

def generate_template_for_action_dobj_and_extract_global_predicates_for_types_and_constants(action, preconditions, effects, constants, hypernym_graph, output_format, activity_id_idx):

	act = action.get_verb()
	dobj = action.get_dobj()
	dobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(dobj, hypernym_graph))

	precondition_properties_types_templates, precondition_properties_constants_templates, precondition_actions_templates = generate_preconditions_templates_for_actions_types_and_constants(action, preconditions, constants, hypernym_graph)
	preconditions_all = precondition_actions_templates + precondition_properties_constants_templates
	#preconditions_all_string = merge_templates(preconditions, indentation = '')

	#generate the effects

	effect_properties_types_templates, effect_properties_constants_templates, effect_actions_templates, effect_predicates_w_types = generate_effects_templates_for_actions_types_and_constants(action, effects, constants, hypernym_graph)
	effects_all = effect_actions_templates #effect_properties_constants_templates
	
	action_name = act + dobj_type.capitalize()
	predicate_current_action_executed = action_name + SUFFIX_EXECUTED_ACTION # should it have parameters? (?o-type)
	predicate_current_action_executed_with_obj = predicate_current_action_executed + " ?o - " + dobj_type

	executed_action_with_constants = predicate_current_action_executed + " " + dobj #predicates with constants are needed later on when we define the goal in the problem file 

	str_activity_name_id = None #this comes into the problem.pddl later
	activity_line = ""
	if output_format == output_formats.CCBM:
		activity_line = "\n \t \t \t:observation (setActivity (activity-id {} ))".format(action_name)
		str_activity_name_id = "(= ( activity-id {} ) {})".format(action_name, activity_id_idx)
    
	action_template = "\n \t \t" +\
			   "(:action " + action_name +\
			   "\n \t \t \t" + \
		       ":parameters ( ?"+ dobj_type +" - "+ dobj_type + " )" + \
			   "\n \t \t \t" + \
			   ":precondition (and"+ \
			   "\n \t \t \t \t" + \
			   "\n \t \t \t \t".join(preconditions_all) +\
			   ")"+\
			   "\n \t \t \t" + \
			   ":effect (and"+ \
			   "\n \t \t \t \t" + \
			   "(" + predicate_current_action_executed + " ?"+dobj_type + " )" +\
			   "\n \t \t \t \t" + \
			   "\n \t \t \t \t".join(effect_actions_templates) +\
			   ")"+\
			   activity_line +\
			   "\n \t \t)"
	
	return action_template,\
		   precondition_properties_types_templates,\
		   effect_properties_types_templates,\
		   predicate_current_action_executed_with_obj,\
		   executed_action_with_constants,\
		   effect_predicates_w_types,\
		   str_activity_name_id   

def generate_template_for_action_indobj_and_extract_global_predicates_for_types_and_constants(action, preconditions, effects, constants, hypernym_graph, output_format, activity_id_idx):
	
	act = action.get_verb()
	indobj = action.get_indobj()
	preposition = action.get_preposition()
	indobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(indobj, hypernym_graph))

	precondition_properties_types_templates, precondition_properties_constants_templates, precondition_actions_templates = generate_preconditions_templates_for_actions_types_and_constants(action, preconditions, constants, hypernym_graph)
	preconditions_all = precondition_actions_templates + precondition_properties_constants_templates
	#preconditions_all_string = merge_templates(preconditions, indentation = '')

	#generate the effects

	effect_properties_types_templates, effect_properties_constants_templates, effect_actions_templates, effect_predicates_w_types = generate_effects_templates_for_actions_types_and_constants(action, effects, constants, hypernym_graph)
	effects_all = effect_actions_templates #effect_properties_constants_templates
	
	action_name = act + preposition.capitalize() + indobj_type.capitalize()

	predicate_current_action_executed = action_name + SUFFIX_EXECUTED_ACTION  # should it have parameters? (?o-type)
	predicate_current_action_executed_with_obj = predicate_current_action_executed + " ?o - " + indobj_type

	executed_action_with_constants = predicate_current_action_executed + " " + indobj
	
	str_activity_name_id = None #this comes into the problem.pddl later
	activity_line = ""
	if output_format == output_formats.CCBM:
		activity_line = "\n \t \t \t:observation (setActivity (activity-id {} ))".format(action_name)
		str_activity_name_id = "(= ( activity-id {} ) {})".format(action_name, activity_id_idx)

	action_template = "\n \t \t" +\
			   "(:action " + action_name +\
			   "\n \t \t \t" + \
		       ":parameters ( ?" + indobj_type + " - " + indobj_type + " )" + \
			   "\n \t \t \t" + \
			   ":precondition (and"+ \
			   "\n \t \t \t \t" + \
			   "\n \t \t \t \t".join(preconditions_all) +\
			   ")"+\
			   "\n \t \t \t" + \
			   ":effect (and"+ \
			   "\n \t \t \t \t" + \
			   "(" + predicate_current_action_executed + " ?" + indobj_type + " )" +\
			   "\n \t \t \t \t" +\
			   "\n \t \t \t \t".join(effect_actions_templates) +\
			   ")"+\
			   activity_line +\
			   "\n \t \t)"
	return action_template,\
		   precondition_properties_types_templates,\
		   effect_properties_types_templates,\
		   predicate_current_action_executed_with_obj,\
		   executed_action_with_constants,\
		   effect_predicates_w_types,\
		   str_activity_name_id
	
def generate_template_for_action_dobj_indobj_and_extract_global_predicates_for_types_and_constants(action, preconditions, effects, constants, hypernym_graph, output_format, activity_id_idx):
	
	act = action.get_verb()
	dobj = action.get_dobj()
	indobj = action.get_indobj()
	preposition = action.get_preposition()

	dobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(dobj, hypernym_graph))
	indobj_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(indobj, hypernym_graph))

	precondition_properties_types_templates, precondition_properties_constants_templates, precondition_actions_templates = generate_preconditions_templates_for_actions_types_and_constants(action, preconditions, constants, hypernym_graph)
	preconditions_all = precondition_actions_templates + precondition_properties_constants_templates
	#preconditions_all_string = merge_templates(preconditions, indentation = '')

	#generate the effects

	effect_properties_types_templates, effect_properties_constants_templates, effect_actions_templates, effect_predicates_w_types = generate_effects_templates_for_actions_types_and_constants(action, effects, constants, hypernym_graph)
	effects_all = effect_actions_templates #effect_properties_constants_templates
	
	action_name = act + dobj_type.capitalize() + preposition.capitalize() + indobj_type.capitalize()


	predicate_current_action_executed = action_name + SUFFIX_EXECUTED_ACTION # should it have parameters? (?o-type)
	predicate_current_action_executed_with_obj = predicate_current_action_executed + " ?o - " + dobj_type + " ?p - " + indobj_type

	executed_action_with_constants = predicate_current_action_executed + " " + dobj + " " + indobj

	str_activity_name_id = None #this comes into the problem.pddl later
	activity_line = ""
	if output_format == output_formats.CCBM:
		activity_line = "\n \t \t \t:observation (setActivity (activity-id {} ))".format(action_name)
		str_activity_name_id =  "(= ( activity-id {} ) {})".format(action_name, activity_id_idx)

	action_template = "\n \t \t" +\
			   "(:action " + action_name +\
			   "\n \t \t \t" + \
		       ":parameters ( ?" + dobj_type + " - " + dobj_type + " ?" + indobj_type + " - " + indobj_type + " )" + \
			   "\n \t \t \t" + \
			   ":precondition (and"+ \
			   "\n \t \t \t \t" + \
			   "\n \t \t \t \t".join(preconditions_all) +\
			   ")"+\
			   "\n \t \t \t" + \
			   ":effect (and"+ \
			   "\n \t \t \t \t" + \
			   "(" + predicate_current_action_executed + " ?" + dobj_type + " ?" + indobj_type + " )" +\
			   "\n \t \t \t \t" +\
			   "\n \t \t \t \t".join(effect_actions_templates) +\
			   ")"+\
			   activity_line +\
			   "\n \t \t)"
	
	return action_template, \
		   precondition_properties_types_templates,\
		   effect_properties_types_templates,\
		   predicate_current_action_executed_with_obj,\
		   executed_action_with_constants,\
		   effect_predicates_w_types,\
		   str_activity_name_id

def generate_property_predicate_template(property_triple, hypernym_graph):
	# property_triple can look like: ("property","cupboard","black")
	property_adjective = property_triple[2]
	property_noun = property_triple[1]
	prop_predicate = PROPERTY_PREDICATE_PREFIX + property_adjective.capitalize() 
	object_type = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(property_noun, hypernym_graph))
	#prop_predicate = prop_predicate + object_type.capitalize()
	prop_predicate_template = "(" + prop_predicate + "(" + " ?o - " + object_type + " )" + ")"	

	return prop_predicate_template

def generate_preconditions_template_action_dobj(action, type_dobj_noun, preconditions, prop_predicates, hypernym_graph, identation = 4):
	# TODO: add as a precondition that the action has not been executed more than X times
	identation_string = "\n" + "\t"*identation
	prec_current_action_not_executed = "( not (" +\
									   action +\
									   SUFFIX_DOBJ_TEMPLATE +\
									   SUFFIX_EXECUTED_ACTION + \
									   " ?o - " + type_dobj_noun + ")" +\
									   ")"
 									   
	template_str_list = [prec_current_action_not_executed] + prop_predicates
	for idx, precond in enumerate(preconditions):
		# the precondition might be a triple or a single action of type string
		if isinstance(precond, str):
			template_str_list.append(precond+SUFFIX_EXECUTED_ACTION)
		else: # is a list ["dobj", "take", "cup"]
			if (precond[0] == "dobj"):
				type_precond_noun = format_type_word_replacing_whitespace(find_type_name_for_noun_using_hypernyms(precond[2], hypernym_graph))
				precondition_executed_action = "( exists " +\
											   "(?o" + str(idx)+"-"+ type_precond_noun + " ) " +\
											   "(" + precond[1]+\
										   	   SUFFIX_DOBJ_TEMPLATE +\
										       SUFFIX_EXECUTED_ACTION + \
										       "(?o" + str(idx)+ "-" + type_precond_noun + " )" +\
											   " )"
				#TODO: 03.05 : modify this so that we can distinguish subjects	
				# add a precondition for the current action (not executed action)						   
				template_str_list.append(precondition_executed_action)
	#add an empty string so that the .join() can put the identation at the beginning as well
	
	final_template = identation_string.join(['', *template_str_list])

	return final_template

def generate_preconditions_template(preconditions, identation = 4):
	identation_string = "\n" + "\t"*identation
	template = ""
	if preconditions:
		template = identation_string.join(preconditions)

	return template
	
def find_preconditions_effects_from_a_caus_rel_list_of_dicts(relation, caus_rel_list_of_dicts):
	preconditions = []
	effects = []
	for cr_dict in caus_rel_list_of_dicts:
		if cr_dict["cause"].to_tuple() == relation.to_tuple():
			effects.append(cr_dict["effect"])
		if cr_dict["effect"].to_tuple() == relation.to_tuple():
			preconditions.append(cr_dict["cause"])
	
	return preconditions, effects


################ END predicates

################ BEGIN hypernym util funtions

def find_type_name_for_noun_using_hypernyms(noun, hypernym_graph):
	#print(noun)
	hypernym = ""

	try:
		successors = list(hypernym_graph.successors(noun))
	except networkx.exception.NetworkXError as err:
		print(f"--- Graphx Error: {err}")
		print(f"--- The detected noun {noun} is not in the hypernym graph, creating new node in the graph..")
		# this case might occur if it is not a noun type, but for instance CD
		# see example sentence "Preheat/VB the/DT oven/NN to/TO 400F/CD ./."
		hypernym = HYPERNYM_GRAPH_INITIAL_NODE
		return hypernym

	if len(successors) == 0:
	# TODO: solve this case - maybe just put a default entity called "entity" (wordnet has that)
		raise ValueError('No hypernym for the noun ' + noun)
	else:
		hypernym = successors[0]
	
	return hypernym

################ END hypernym util functions