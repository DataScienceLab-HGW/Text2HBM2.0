#!/bin/bash
python3 text2HBM_CLI.py plan_extraction -coref_resolution -l -gr ./test_plan_extraction/graph/ -pdir ./test_plan_extraction/pddl/ -dname test -stparser_dir ./stanford-parser-full-2018-02-27/ -in ./test_plan_extraction/input/t_in.txt -f pddl
