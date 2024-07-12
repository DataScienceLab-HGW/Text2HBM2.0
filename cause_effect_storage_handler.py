'''
this script contains methods for storing cause-effects relationships

'''

import csv
import relationship_types


CSV_header = "cause_rel_type;cause_rel_string;cause_rel_verb;cause_rel_dobj;cause_rel_indobj;cause_rel_indobj_prep;effect_rel_type;effect_rel_string;effect_rel_verb;effect_rel_dobj;effect_rel_indobj;effect_rel_indobj_prep"

def create_rel_part_row(rel_obj):

    row_rel_part = ""
    row_part_beginning =  rel_obj.rel_type + ";" + " ".join(rel_obj.relation[1:]) + ";"
    if rel_obj.rel_type == relationship_types.DOBJ_RELATIONSHIP:
       row_rel_part = row_part_beginning + ";".join([rel_obj.verb, rel_obj.dobj, "", ""])
    if rel_obj.rel_type == relationship_types.VB_DOBJ_INDOBJ_RELATIONSHIP:
       row_rel_part = row_part_beginning  + ";".join([rel_obj.verb, rel_obj.dobj, rel_obj.indobj, rel_obj.preposition])
    if rel_obj.rel_type == relationship_types.INDOBJ_RELATIONSHIP:
       row_rel_part = row_part_beginning +";".join([rel_obj.verb, " ", rel_obj.indobj, rel_obj.preposition])
    if rel_obj.rel_type == relationship_types.VBNOOBJ_RELATIONSHIP:
       row_rel_part = row_part_beginning +";".join([rel_obj.verb, "", "", ""])

    return row_rel_part


def store_causal_relations(cause = None, effect = None, filename_extracted_prec_eff = None, pddl_dir = None, idx_rel = None, amount_relations = None):
    #cause and effect variables are lists 

    filepath_cause_effect_rel = pddl_dir + filename_extracted_prec_eff

    #in case that something goes wrong, raise an exception
    if (None in [cause, effect, filename_extracted_prec_eff]):
        raise Exception("No cause, effect or filename provided!!")

    csv_row_part_cause = create_rel_part_row(cause)
    csv_row_part_effect = create_rel_part_row(effect)

    csv_row = csv_row_part_cause + ";" + csv_row_part_effect

    with open(filepath_cause_effect_rel, "a+") as f:
         if idx_rel==0:
            f.write(CSV_header)
            f.write("\n") 
         f.write(csv_row)
         if idx_rel !=amount_relations:
            f.write("\n")