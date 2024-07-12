'''
This module is used when we want to apply domain knowledge to the
original text. The intention behind this is to get results form the Stanford parser
when it gets as an input pre-annotated tokens.

Note:
It is important to mention that when replacing tokens, the case of the text is considered:
We recommend to lowercase the input in order to make sure that all occurrences will be substituted.
See: replace_instance_tokens_in_txt

'''
from utils import read_file, write_to_file
import importlib.util
import sys
import re
from collections import namedtuple

PARSER_TAG_SEPARATOR = "/"

def add_module_dynamically(filepath):
    module_name = "module." + filepath.split(".")[0].split("/")[-1]

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    known_types_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = known_types_module
    spec.loader.exec_module(known_types_module)

    return known_types_module

def add_known_types_to_input_and_get_types_dict_lst(input_filepath_text, known_types_filepath, lowercase:bool):

    known_types_module = add_module_dynamically(known_types_filepath)

    input_text_orig = read_file(input_filepath_text)
    if lowercase:
       input_text_orig = input_text_orig.lower()  

    types_instances:dict = known_types_module.KNOWN_TYPES_INSTANCES
    verbs_instances:list = known_types_module.KNOWN_VERBS
    types_hierarchy:list = known_types_module.TYPE_HIERARCHY
    # we need to replace all "." with "./.", otherwise the parser does not parse the 
    # pre-tagged text correctly 
    # (there might be however an option/parameter for the command of the parser which fixes this) 
    input_text_orig = input_text_orig.replace(".", " ./. ")

    #TODO: validate that KNOWN_TYPES_INSTANCES does not contain empty lists as values
    
    text_with_tagged_types = replace_known_types_in_txt(input_text_orig, types_instances)
    text_with_tagged_verbs_and_types = replace_known_verbs_in_txt(text_with_tagged_types, verbs_instances)
  
    return text_with_tagged_verbs_and_types, types_instances, types_hierarchy

def replace_known_types_in_txt(text:str, known_types_instances:dict):
    # we take the instances

    for type, instances in known_types_instances.items():
        #print(type, instances)
        for instance in instances:
            text = replace_instance_tokens_in_txt(text, instance) 
   
    return text

def replace_known_verbs_in_txt(text:str, known_verbs:list):
    for verb in known_verbs:
        text = replace_instance_tokens_in_txt(text, verb)
    
    return text

def replace_instance_tokens_in_txt(txt, type_instance):
    '''
    It is important to mention that when replacing tokens, the case of the text is considered:
    It is recommended to lowercase the input (using the text2HBM CLI) in order to make sure that all occurrences will be substituted.
    '''
    # if the instance is a composite word like baking soda
    # we find both tokens in the text, merge them and the result is baking_soda/NN
    txt = remove_multiple_whitespaces(txt)
    tagged_instance = handle_multi_word_instance_text(type_instance.txt) + PARSER_TAG_SEPARATOR + type_instance.tag
    txt_with_tagged_instance = re.sub(r"\b" + re.escape(type_instance.txt) + r"\b", tagged_instance, txt)

    return txt_with_tagged_instance

def handle_multi_word_instance_text(text):
    splitted = text.split(" ")
    if len(splitted)>1:
       return "_".join(splitted)
    else:
       return splitted[0]
    
def remove_multiple_whitespaces(text):
    return  re.sub("[^\S\r\n]+", " ", text)