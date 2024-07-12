'''
The stanford parser does not always produce the correct output (for instance, verbs not being recognised as such)
This script contains methods which apply additional rules to the parsing result in order to make the parsing better.

Some of the rules are the ones described in: https://acl-bg.org/proceedings/2017/RANLP%202017/pdf/RANLP106.pdf
A Simple Model for Improving the Performance of the Stanford Parser for Action Detection in Textual Instructions, autohr: Kristina Y. Yordanova

'''
#from ast import Str
import utils

NO_VERB_RULE = "no-verb-rule"
PAST_TENSE_RULE = "past-tense-rule"
NOUN_RULE = "noun-rule"
ALL_PARSER_CORR_RULES = "all-rules"
ALL_RULES = [NO_VERB_RULE, NOUN_RULE, PAST_TENSE_RULE]

RULES_TYPES = [NO_VERB_RULE, PAST_TENSE_RULE, NOUN_RULE, ALL_PARSER_CORR_RULES]

### correction rules functions 
def apply_no_verb_rule(tagged_sentence_pos):
    # the rule: if the sentence does not contain a verb,
    # mark the first word(token)
    
    verb_tags_with_delimiter = ["/"+vtag for vtag in utils.VERB_TAGS]
    verb_in_sentence = any(substring in tagged_sentence_pos for substring in verb_tags_with_delimiter)
    
    if verb_in_sentence:
       return tagged_sentence_pos
    else:
        print("Before applying 'no verb rule' to: ")
        print(tagged_sentence_pos)
        print("After applying 'no verb rule': ")
        tokenized_sentence = tagged_sentence_pos.split(" ")
        first_token_with_pos = tokenized_sentence[0]
        first_with_pos_splitted = first_token_with_pos.split("/")
        tokenized_sentence[0] = first_with_pos_splitted[0]+"/"+utils.VERB_PRESENT_TENSE_TAG
        tagged_sentence = " ".join(tokenized_sentence)
        print(tagged_sentence)
    
        return tagged_sentence

def apply_past_tense_rule(tagged_sentence_pos):
    '''
    Rule 2 (Past tense rule) Given a sentence S such
    that S := (W, T ) where W := (w1, . . . , wn) is
    the set of words in S and T := (t1, . . . , tn) the
    corresponding POS-tags with n being the order of
    appearance of the word in S. If t1 := VBD, where
    VBD denotes past tense verbs, then replace t1 :=
    VBD with t1 := verb.
    '''

    tokenized_sentence = tagged_sentence_pos.split(" ")
    first_token_with_pos = tokenized_sentence[0]
    first_token_pos_splitted = first_token_with_pos.split("/")# 0 index = verb , 1 index = tag
    if first_token_pos_splitted[1] == utils.VERB_PAST_TENSE_TAG:
       tokenized_sentence[0] = first_token_pos_splitted[0] + "/" + utils.VERB_PRESENT_TENSE_TAG

    tagged_sentence = " ".join(tokenized_sentence)

    return tagged_sentence

def apply_noun_rule(tagged_sentence_pos):
    '''
    noun rule: Given a sentence S such that
    S := (W, T ) where W := (w1, . . . , wn) is the
    set of words in S and T := (t1, . . . , tn) the corre-
    sponding POS-tags with n being the order of ap-
    pearance of the word in S. If t1 := noun and t2 :=
    verb, then assign t1 := verb and t2 := noun. If
    t1 := noun and t2 := ¬verb, assign t1 := verb.
    '''

    tokenized_sentence = tagged_sentence_pos.split(" ")
    first_token_with_pos = tokenized_sentence[0]
    snd_token_with_pos = tokenized_sentence[1]

    first_with_pos_splitted = first_token_with_pos.split("/")
    snd_with_pos_splitted = snd_token_with_pos.split("/")

    if first_with_pos_splitted[1] in utils.NOUN_TAGS and snd_with_pos_splitted[1] in utils.VERB_TAGS:
       tokenized_sentence[0] = first_with_pos_splitted[0] + "/" + "VB"
       tokenized_sentence[1] = snd_with_pos_splitted[0] + "/" + "NN"
    
    tagged_sentence = " ".join(tokenized_sentence)

    return tagged_sentence


RULES_FUNCTION_DICT = {NO_VERB_RULE: apply_no_verb_rule,
                       PAST_TENSE_RULE:apply_past_tense_rule,
                       NOUN_RULE:apply_noun_rule,
                      }

def apply_correction_rule_on_multiple_sentences(parsed_sentences_with_pos, rule):
    
    new_sentences = []

    for tagged_sentence_dependencies in parsed_sentences_with_pos:
        correction_rule_function = RULES_FUNCTION_DICT.get(rule)
        new_sentence = correction_rule_function(tagged_sentence_dependencies)
        new_sentences.append(new_sentence)
    
    return new_sentences 

def apply_correction_rules(rules, parsed_sentences_with_pos):
    '''
    parsed_sentences_with_pos: a list of parsed sentences. Each parsed sentence contains POS tags
    Example:
    ['line/NN baking/VBG s...per/NN ./.']
    rules: a user-input string which
    '''
    if ALL_PARSER_CORR_RULES in rules:
       rules = ALL_RULES

    new_sents = parsed_sentences_with_pos

    for rule in rules:
        new_sents = apply_correction_rule_on_multiple_sentences(new_sents, rule)

    return new_sents

def create_dict_pos_token_idx(sentence):
    token_pos_dict = {}
    tokens = sentence[0].split(" ")
    for idx, token in enumerate(tokens):
        token_parts = token.split('/')# a token such as adjust/VB
        token_text = token_parts[0]
        token_pos = token_parts[1]
        token_with_idx = (token_text, idx)
        if token_pos not in token_pos_dict.keys():
            token_pos_dict[token_pos] = [token_with_idx]
        else:
            token_pos_dict[token_pos].append(token_with_idx) 
    
    return token_pos_dict

