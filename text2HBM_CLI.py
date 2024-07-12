'''
This is the implementation of the Command Line Interface of the text2HBM tool.
Run plan_extraction to perform plan extraction from textual input (possible output in PDDL or CCBM languages)
Run precondition_effect_extraction to only extract preconditions and effects 
'''


# getting console inputs
import os
import sys
import argparse
from argparse import ArgumentParser, RawDescriptionHelpFormatter as RDHF
#parser correction rules types (names)
from parsing_rules import RULES_TYPES
from  output_formats import OUTPUT_FORMATS

#
import text2HBM


def verify_dir_exists(dir_name):
    if os. path. isdir(dir_name):
        message_ok = "Directory " + dir_name + " is a valid directory! :) "
        print(message_ok)
    else:
        print("The directory " + dir_name + " is not a valid directory!\nPlease, check the path or create a new directory. ")
        sys.exit(1)

def verify_file_exists(file_path):
    if os.path.isfile(file_path):
       message_ok = "The file " + file_path + " exists. "
       print(message_ok)
    else:
       print("The file " + file_path + " does not exist.\nPlease, check the path or create a new file. ")
       sys.exit(1)

def verify_output_format(output_format):
    if output_format in OUTPUT_FORMATS:
       print("Output format set to " + output_format)
    else:
       print(f"The output format {output_format} is not a valid format!")
       sys.exit(1)

def process_corr_rules_input(corr_rules_input):
    '''
    1. verifies that the input is correct (A list of comma separated params)
    2. returns a list of rules
    '''
    #check if only a single rule or many
    corr_rules_input = ''.join(corr_rules_input.split())
    corr_rules = corr_rules_input.split(",")
    print("##### Applying parser correction rules:")
    for rule in corr_rules:
        if rule in RULES_TYPES:
           print(f"Applying parser correction rule: {rule}")
        else:
            print(f"The rule {rule} does not exist.\n Please, check again the rules you gave as parameters. ")
            sys.exit(1)

    return corr_rules



def run_plan_extraction(**parser_args):
    print(parser_args)

    args = parser_args #just a shorter alias
    print("##### Verifying the directories exist: ")

    # assign variables to the passed hyperparams
    save_graph_dir = args["graphdir"]
    save_pddl_dir = args["pddl_dir"]
    input_txt_path = args["input_text_path"]
    stanford_parser_dir = args["stanford_parser_dir"]
    output_format = args["output_format"]
    known_types_file = args["known_types_file"]

    # parser correction rules
    parser_corr_rules = args["parser_corr_rules"]
    parser_corr_rules_list = None
    if parser_corr_rules:
       print(parser_corr_rules)
       parser_corr_rules_list = process_corr_rules_input(parser_corr_rules)

    verify_dir_exists(save_graph_dir)
    verify_dir_exists(save_pddl_dir)
    verify_dir_exists(stanford_parser_dir)
    verify_file_exists(input_txt_path)
    verify_output_format(output_format)

    if known_types_file:
       verify_file_exists(known_types_file)

    lc = args["lower_case"]
    domain_name = args["domain_name"]

    if lc:
        print("##### lower case before parsing activated")
        lower_case_bool = True
    else:
        print("##### No lowercase before parsing activated")
        lower_case_bool = False

    print("#"*100)

    text2HBM.run_text2hbm(input_text_full_path = input_txt_path,\
                 domain_name = domain_name,\
                 pddl_dir = save_pddl_dir,\
                 stanford_parser_dir = stanford_parser_dir,\
                 graphs_dir = save_graph_dir,\
                 lowercase_bool = lower_case_bool,\
                 parser_correction_rules = parser_corr_rules_list,\
                 output_format = output_format,\
                 known_types_file = known_types_file,\
                 #extract_preconditions_effects_only = extract_preconditions_effects_only
                 )

def run_precondition_effect_extraction(**parser_args):
    args = parser_args #just a shorter alias
    print("##### Verifying the directories exist: ")


    precond_effect_dir = args["output_dir_preconditions_effects"]
    input_file = args["source_path"]
    st_parser_dir = args["stanford_parser_directory"]

    verify_dir_exists(precond_effect_dir)
    verify_file_exists(input_file)
    verify_dir_exists(st_parser_dir)



    text2HBM.run_text2hbm(input_text_full_path = input_file,\
                 domain_name = None,\
                 pddl_dir = precond_effect_dir,\
                 stanford_parser_dir = st_parser_dir,\
                 graphs_dir = None,\
                 lowercase_bool = None,\
                 parser_correction_rules = None,\
                 output_format = None,\
                 known_types_file = None,\
                 extract_preconditions_effects_only = True
                 )


    
def text2HBM_cli():

    parser = ArgumentParser(description=__doc__, formatter_class= RDHF)

    subs = parser.add_subparsers()
    subs.required = True

    subs.dest = 'Plan generation or Cause-Effect-extraction only'

    plan_gen_parser = subs.add_parser('plan_extraction', help='Generate plans in PDDL or CCBM given text input.')
    plan_gen_parser.set_defaults(func = run_plan_extraction)

    plan_gen_parser.add_argument('-lowerc','--lower_case', action = "store_true", help='Turns the text into lower-case before parsing it which empirically improves the performance of the parser.', required=False)
    plan_gen_parser.add_argument('-parser_corr_rules','--parser_corr_rules', help='Using parser correction rules. The parameter has to be a list of comma-separated rules\
                                                            \n Rules are: "no-verb-rule", "past-tense-rule", "noun-rule", "all-rules". \n The last one combines all. ', required= False)
    plan_gen_parser.add_argument('-known_types_file','--known_types_file', help= 'Use a file with known types and instances definitions (domain knowledge)')
    
    required_args = plan_gen_parser.add_argument_group('Required named arguments')
    required_args.add_argument('-gr','--graphdir', help='Directory to save graphs (graphical representations of the situation model.)', required=True)
    required_args.add_argument('-pdir','--pddl_dir', help='Directory to save pddl problem and domain files.', required=True)
    required_args.add_argument('-dname','--domain_name', help='The name of the domain (scenario). The name is also used as a suffix for the generated\
                         pddl files.', required=True)
    required_args.add_argument('-stparser_dir','--stanford_parser_dir', help='The path of the Stanford Parser being used', required = True)
    required_args.add_argument('-in','--input_text_path', help='The path of the text which text2HBM will transform into pddl.', required = True)
    required_args.add_argument('-f','--output_format', help='Sets the output format to "pddl" or "ccbm" ', required= True)


    precondition_effect_extraction_parser = subs.add_parser('precondition_effect_extraction', help='Extracts precondition-effect rules between actions.')
    precondition_effect_extraction_parser.set_defaults(func = run_precondition_effect_extraction)
    precondition_effect_extraction_parser.add_argument('-s','--source_path', help='Setting source (path to file) makes text2HBM output store preconditions and effects extracted from the provided file \n \
                        and stores them in the directory set by -pedir ', required= True)
    precondition_effect_extraction_parser.add_argument('-pedir','--output_dir_preconditions_effects', help='The directory to store the extracted precondition-effect pairs ', required= True)
    precondition_effect_extraction_parser.add_argument('-stpar_dir','--stanford_parser_directory', help='The path of the Stanford Parser being used', required = True)



    args = parser.parse_args()
    #print(args)
    parser_func = args.func.__name__
    #print(args.func.__name__)

    if parser_func == "run_precondition_effect_extraction":
    
       args_dict = args.__dict__
       run_precondition_effect_extraction(**args_dict)

    else:
       args_dict = args.__dict__
       run_plan_extraction(**args_dict)


if __name__ == "__main__":
    text2HBM_cli()            
    
