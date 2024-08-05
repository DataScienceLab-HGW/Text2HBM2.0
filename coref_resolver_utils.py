from coref_resolver import CorefResolver
import utils
import os

def run_coref_resolution_prestep_to_path(input_text_full_path):
    coref_resolver_obj = CorefResolver()

    text = utils.read_file(input_text_full_path)

    directory = os.path.dirname(input_text_full_path)
    current_filename_without_extension = os.path.basename(input_text_full_path).split(".")[0]


    new_filename = current_filename_without_extension + '_coref_resolved' '.txt'  # Specify the new filename

    print(f"##### Creating new input file with resolved coreferences on path {new_filename} ... ")

    new_fpath = os.path.join(directory, new_filename)  # Create the new path by joining the directory and new filename

    text_resolved = coref_resolver_obj.resolve_corefs_text(text)

    utils.write_to_file(new_fpath, text_resolved)
    print(f"##### Corefs resolved at {new_filename} done. ")

    return new_fpath