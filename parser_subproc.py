'''
This script contains functions for different nlp operations such as
verb/noun extraction

For the tags interpretation see: https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
IMPORTANT: https://universaldependencies.org/ (dependencies in stanza)
https://universaldependencies.org/tagset-conversion/en-penn-uposf.html

https://universaldependencies.org/u/dep/ - dependencies of stanford parser 3.9.1

TODO: When the enchanced version of the stanza parser is done, this script should be 
changed to work with stanza

'''

import subprocess
import os
import utils as utils
import matplotlib.pyplot as plt
#include the additional hand-made parsing rules
import parsing_rules
import random

#PATH_STANFORD_PARSER_JAR = "./stanford-parser-full-2018-02-27/stanford-parser.jar"
#PATH_STANFORD_PARSER_MODELS = "./stanford-parser-full-2018-02-27/stanford-parser-3.9.1-models.jar"

def parse_input_file(file_path, parser_path, lowercase_bool, parser_correction_rules = None, use_known_types = None):
    output_format = "typedDependencies,wordsAndTags" # https://gist.github.com/a34729t/2562754
    output_format_params_number = len(output_format.split(","))
    # if the lowercase option is chosen, create a copy of the file where the text is in lower-case
    
    file_path = check_input_lowercase_option(file_path, lowercase_bool)

    print("Parsing "+ file_path)

    '''
    TODO: add the new command in the apply rules method
    Main idea : use external knowledge to tag verbs and nouns and then save the 
    tagged sentence in another text file. pass the new text file to the parser and 
    continue with the text2hbm procedure.
    https://nlp.stanford.edu/software/parser-faq.html#d
    '''
    
    command = create_parser_command(parser_path, output_format, file_path, tagged = use_known_types)
    parser_output_per_sentence = execute_parsing_command(command, output_format_params_number)

    if parser_correction_rules:

       parser_output_sentences_with_pos_only = [sent[0] for sent in parser_output_per_sentence]
       new_sentences_with_tags_as_lists = parsing_rules.apply_correction_rules(parser_correction_rules, parser_output_sentences_with_pos_only)       
       
       input_file_without_ext = file_path.rsplit(".")[0]
       rand_name = "_pos_" + str(random.randint(1000,9999))
       filename_with_tags =  input_file_without_ext + rand_name + ".txt"
       new_tagged_sent_str = "\n".join(new_sentences_with_tags_as_lists)
       utils.write_to_file(filename_with_tags, new_tagged_sent_str)
       command_n = create_parser_command(parser_path, output_format, filename_with_tags, tagged = True)
       parser_output_per_sentence = execute_parsing_command(command_n, output_format_params_number)
        

    return parser_output_per_sentence #output: a list of parsed sentences

def remove_tags_from_parser_output_sentences(sentences_list):
    #this function is intended to be used because of the fact
    #that the parser works better when passing the same sentences once again
    #but considering a proper whitespace
    new_sentences = []
    for sentence in sentences_list:
        tokens = sentence.split(" ")# we get a sequence of tokens in the format word/TAG
        new_sentence = " ".join([token.split("/")[0] for token in tokens])
        new_sentences.append(new_sentence)

    new_sentences_text = "\n".join(new_sentences)

    return new_sentences_text

def execute_parsing_command(command_as_list_of_str, output_format_params_number ):

    command_str = " ".join(command_as_list_of_str)

    parser_process = subprocess.Popen(command_str, shell=True, stdout=subprocess.PIPE)
    parser_output = parser_process.stdout.read().decode("utf-8")
    parser_output_as_list = parser_output.split("\n\n")[:-1] # the last element is an empty list
    parser_output_per_sentence  = list(utils.split_list_into_chunks_of_n_elements(parser_output_as_list, output_format_params_number))

    return parser_output_per_sentence

def create_parser_command(parser_path, output_format, file_path, tagged = False):
    
    if not tagged:
        command =["java -cp",
                parser_path,
                "edu.stanford.nlp.parser.lexparser.LexicalizedParser",
                "-outputFormat",
                output_format,
                "-sentences newline",
                "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz",
                file_path]
    else:
        command = ["java -cp",
                    parser_path,
                    "edu.stanford.nlp.parser.lexparser.LexicalizedParser",
                    "-outputFormat",
                    output_format,
                    "-sentences newline",
                    "-tokenized",
                    "-tagSeparator /",
                    "-tokenizerFactory edu.stanford.nlp.process.WhitespaceTokenizer",
                    "-tokenizerMethod newCoreLabelTokenizerFactory edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz",
                    file_path]

    return command

def parse_file_with_tagged_tokens(filepath, parser_path ):
    pass

def create_list_dep_words_and_ann_sentence_tokens(list_of_parsed_sentences):
    #each sentence consists of 2 parts (lists)
    # sentence = ['Take/VB a/DT clean/JJ pot/NN from/IN the/DT cupboard/NN ./.' , 'root(ROOT-0, Take-1)\ndet(pot-4, a-2)\namod(pot-4, clean-3)\ndobj(Take-1, pot-4)\ncase(cupboard-7, from-5)\ndet(cupboard-7, the-6)\nnmod:from(Take-1, cupboard-7)'
    # Note that all deps with ROOT are getting removed!
    dep_words_and_ann_sentence_tokens = []
    
    for sentence in list_of_parsed_sentences:
        annotated_sent = sentence[0] # annotations like Take/VB
        dependencies = sentence[1]

        annotated_token_tuples = utils.transform_annotated_sentence_to_tuples_of_token_annotation(annotated_sent)
        list_of_deps = utils.transform_dependencies_strings(dependencies)
        list_of_dep_triples = utils.transform_dep_strings_to_triples(list_of_deps)
        # if the sentence contains only one word and this word is a verb
        # deleting the root might be a problem (we are loosing the dependency root->verb)
        
        #sentence_has_verb = utils.annotated_token_tuples_contain_verb(annotated_token_tuples)

        # check if the sentence has a verb in a relationship which is not a dobj or indobj or property relationship
        # if a root relationship contains a verb, transform it into a verb_no_obj relationship
        '''
        if sentence_has_verb and len(list_of_deps) == 1:
            # this means that the sentence has one root relation with a verb
            # the root has the token index 0 , the verb will have token index 1
            # in our case a triple ("root", idxRoot=0, idxVerb=1)
            verb_tuple = annotated_token_tuples[list_of_dep_triples[0][2]-1] + (list_of_dep_triples[0][2], )
            dep_for_verbs_without_objecs = (RELATION_VERB_NO_OBJ, verb_tuple, verb_tuple ) # artificial relationship VB-VB
            dep_words_and_ann_sentence_tokens.append([dep_for_verbs_without_objecs])
        else:
        '''


        #list_of_dep_triples = utils.remove_root_relation(list_of_dep_triples)
        annotated_token_tuples_with_idx = [el + (idx, ) for idx, el in enumerate(annotated_token_tuples)]
        list_of_dep_words_and_ann_sentence_tokens = [(triple[0], annotated_token_tuples_with_idx[triple[1]-1],annotated_token_tuples_with_idx[triple[2]-1]) for triple in list_of_dep_triples]
        #if the list of dependencies contains a dependency which has a verb
        
        # Lowercase the list of deps
        dep_words_and_ann_sentence_tokens.append(list_of_dep_words_and_ann_sentence_tokens)
        

    return dep_words_and_ann_sentence_tokens


def create_list_of_annotated_tokens_for_annotated_sentence(list_of_parsed_sentences):
    
    annotated_token_tuples = []
    for sentence in list_of_parsed_sentences:
        annotated_sent = sentence[0] # annotations like Take/VB

        annotated_token_tuples.append(utils.transform_annotated_sentence_to_tuples_of_token_annotation(annotated_sent))

    return annotated_token_tuples

def check_input_lowercase_option(input_filepath, lc):
    '''
    checks if the input text file has to be lower-cased (empirically works better with the parser)
    If this the lowercase option is set to True, then a copy of the original file is created with the lower-cased
    version of the text
    
    '''

    if lc:
        lc_filename_with_extension = "lower_case_" + input_filepath.rsplit("/", 1)[-1]
        lc_filepath = input_filepath.rsplit("/", 1)[0] + "/" + lc_filename_with_extension
    
        orig_input_content = ""
        with open(input_filepath, 'r') as f:
            orig_input_content = f.read()

        print("Creating a lower-cased version of the input file " + input_filepath )
        print("New input file " + lc_filepath )

        orig_input_content_lower_case = orig_input_content.lower()
        with open(lc_filepath, 'w') as f:
            orig_input_content = f.write(orig_input_content_lower_case)

        print("New file created successfully!")
        
        return lc_filepath

    else:
        return input_filepath
