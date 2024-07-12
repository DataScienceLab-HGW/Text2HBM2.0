'''
Currently our tool uses the Wordnet ontology to find types definitions (needed for the pddl).
However, it makes sense to let the users define types with their corresponding instances.
We call these user-defined types "known types" and the instances "known instances".

In order to use such known entities, there is an optional parameter which has to be set in the
CLI-version of the tool upon execution. The argument called "domain_knowledge_file" has to contain
the path to the python file where the known entities are defined as two dictionary variables:

KNOWN_TYPES_INSTANCES: {"type_name":["instance1", "instance2"]}
TYPE_HIERARCHY : consists of multiple n-tuples. 
Example: (alcohol, liquid, ingredient) means that "ingredient


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

'''

from collections import namedtuple

Instance = namedtuple("Inst","txt tag") 

'''
KNOWN_TYPES_INSTANCES = {}
KNOWN_VERBS = []
TYPE_HIERARCHY = []
'''

'''
KNOWN_TYPES_INSTANCES = {"ingredient":[""],
                         "liquid":[Instance("water", "NN")],
                         "powder_ingredient":[Instance("baking powder","NN")],
                         "weight_measurements":[Instance("ounces","NNS"),
                                                Instance("ounce","NN"),
                                                Instance("kilogram","NN"),
                                                Instance("kilograms","NN"),
                                                Instance("gram","NN"),
                                                Instance("grams","NNS"),
                                                Instance("pound","NN"),Instance("pounds","NNS")],
                         "uttensil":[Instance("kitchen knife","NN")]
                         }
'''

KNOWN_TYPES_INSTANCES = {"ingredient":[Instance("onion","NN"),
                                       Instance("oil","NN")],
                          
                         "kitchen utensil":[Instance("red_knife","NN"),
                                            Instance("pot","NN")],
                         "liquid_ingredient":[Instance("milk","NN"), Instance("water","NN")],
                         "powder_ingredient":[Instance("baking_soda","NN"), Instance("pudding_powder","NN")]                   
                        }
KNOWN_VERBS = [Instance("turn on","VB"), Instance("turn off","VB")]

TYPE_HIERARCHY = [["ingredient","powder_ingredient"],["ingredient","liquid_ingredient"]]
