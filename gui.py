
import argparse

from argparse import ArgumentParser, RawDescriptionHelpFormatter as RDHF



def run_1(i):
    print("RUN1")


def run_2(i, c):
    print("RUN2")

def example():
    parser = ArgumentParser(description=__doc__, formatter_class=RDHF)
    subs = parser.add_subparsers()
    subs.required = True
    subs.dest = 'run or test'
    test_parser = subs.add_parser('test', help='Test all servers')
    test_parser.set_defaults(func=run_1)
    test_parser.add_argument('-i', '--id',
                            help='The ID of the server to connect to and run commands',
                            required=True)


    run_parser = subs.add_parser('run', help='Run a command on the given server')
    run_parser.add_argument('-i', '--id',
                            help='The ID of the server to connect to and run commands',
                            required=True)
    run_parser.add_argument('-c', '--command',
                            help='The command to run',
                            required=True)
    run_parser.set_defaults(func=run_2)
    args = parser.parse_args()
    
    print(args.func.__name__)

    if args.func.__name__ == 'run_1':
        all_servers = ['127.0.0.1', '127.0.0.2']
        print(args.id)

        run_1(all_servers)
    else:
        run_2(args.id)



def run_plan_extraction(**parser_args):
    print(parser_args)

    print("a")

def run_precondition_effect_extraction(*parser_args):
    print("b")
    

    


def text2HBM_gui():

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


    precondition_effect_extraction_parser = subs.add_parser('precondition-effect-extraction', help='Extracts precondition-effect rules between actions.')
    precondition_effect_extraction_parser.set_defaults(func = run_precondition_effect_extraction)
    precondition_effect_extraction_parser.add_argument('-s','--extract_preconditions_effects_only',action = "store_true", help='Setting this flag makes text2HBM output only preconditions and effects from the INPUT_TEXT_PATH \n \
                        and stores them in the directory set by -pdir ', required= True)


    args = parser.parse_args()
    #print(args)
    parser_func = args.func.__name__
    #print(args.func.__name__)

    if parser_func == "run_precondition_effect_extraction":
       print(args)
       print("x")
       print(args.graphdir)
       run_precondition_effect_extraction(args)

    else:
       print("x")
       args_dict = args.__dict__
       print(args_dict)
       run_plan_extraction(**args_dict)

if __name__ == "__main__":
    text2HBM_gui()


'''
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Text2HBM 2.0 - a tool to extract plans from texts')
    
    parser.add_argument('-lowerc','--lower_case', action = "store_true", help='Turns the text into lower-case before parsing it which empirically improves the performance of the parser.', required=False)
    parser.add_argument('-parser_corr_rules','--parser_corr_rules', help='Using parser correction rules. The parameter has to be a list of comma-separated rules\
                                                            \n Rules are: "no-verb-rule", "past-tense-rule", "noun-rule", "all-rules". \n The last one combines all. ', required= False)
    parser.add_argument('-known_types_file','--known_types_file', help= 'Use a file with known types and instances definitions (domain knowledge)')
    
    parser.add_argument('-s','--extract_preconditions_effects_only',action = "store_true", help='Setting this flag makes text2HBM output only preconditions and effects from the INPUT_TEXT_PATH \n \
                        and stores them in the directory set by -pdir ', required= False)


    required_args = parser.add_argument_group('Required named arguments')
    required_args.add_argument('-gr','--graphdir', help='Directory to save graphs (graphical representations of the situation model.)', required=True)
    required_args.add_argument('-pdir','--pddl_dir', help='Directory to save pddl problem and domain files.', required=True)
    required_args.add_argument('-dname','--domain_name', help='The name of the domain (scenario). The name is also used as a suffix for the generated\
                         pddl files.', required=True)
    required_args.add_argument('-stparser_dir','--stanford_parser_dir', help='The path of the Stanford Parser being used', required = True)
    required_args.add_argument('-in','--input_text_path', help='The path of the text which text2HBM will transform into pddl.', required = True)
    required_args.add_argument('-f','--output_format', help='Sets the output format to "pddl" or "ccbm" ', required= True)

    #parser.parse_args(["-h"])


    args = vars(parser.parse_args())
    print(vars)

'''