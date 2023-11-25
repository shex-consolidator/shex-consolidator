import os
import argparse
import sys
from shexer.shaper import Shaper
from shexer.consts import NT, MIXED_INSTANCES


def complete_with_zeros(str_number, lenght):
    while len(str_number) < lenght:
        str_number = "0" + str_number
    return str_number

def groups_of_files(files, size_group):
    tmp = []
    for a_path in files:
        tmp.append(a_path)
        if len(tmp) == size_group:
            yield tmp
            tmp = []
    if len(tmp) > 0:
        yield tmp

def run(base_input_dir,
        out_path_template,
        namespaces,
        list_of_file_groupings):
    in_files = []
    for i in range(90):
        suffix = complete_with_zeros(str(i), 2)
        in_files.append(base_input_dir + suffix)
    for i in range(749):
        suffix = "9" + complete_with_zeros(str(i), 3)
        in_files.append(base_input_dir + suffix)



    for a_target_number in list_of_file_groupings:
        print("--\n"*3, f"Starting computation of {a_target_number} groupings\n", "--\n"*3)
        counter = 1
        for a_group in groups_of_files(in_files,a_target_number):
            print("Going for", a_group[0])
            # suffix = a_group[0][a_group[0].rfind("_"):]
            shaper = Shaper(graph_list_of_files_input=a_group,
                            all_classes_mode=True,
                            input_format=NT,
                            namespaces_dict=namespaces.copy(),
                            disable_exact_cardinality=True,
                            detect_minimal_iri=True,
                            # compression_mode="gz",
                            instances_report_mode=MIXED_INSTANCES)

            # Verbose active mode, so one can check in which stage is the execution, some raw numbers
            # about shapes and instances computed, and also execution times

            # This acceptance_threshold filters any information observed in less than 5% of the
            # instances of any class.
            shaper.shex_graph(output_file=out_path_template.format(a_target_number, counter),
                              verbose=True,
                              acceptance_threshold=0)
            counter += 1

    print("Done!")

if __name__ == "__main__":
    ############### CONFIGURATION ###############

    # parser = argparse.ArgumentParser()
    # parser.add_argument('-i', '--input', help='Specify the input directory')
    # parser.add_argument('-o', '--output', help='Specify the output file')
    # args = parser.parse_args()
    # if args.input:
    #    base_input_dir = args.input
    # else:
    #    print('Specify the input directory.', file=sys.stderr)
    #    sys.exit(-1)
    # if args.output:
    #    out_path = args.output
    # else:
    #    out_path = "__STD_OUT__"
    # Directory with the wikipathways dump (content unzipped). the process will recursively look
    # for any ttl file in this folder or any of this subfolders, and it will merge it in a single
    # graph

    # output shex file

    # namespace-prefix pair to be used in the results
    namespaces_dict = {"http://purl.org/dc/terms/": "dc",
                       "http://rdfs.org/ns/void#": "void",
                       "http://www.w3.org/2001/XMLSchema#": "xsd",
                       "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
                       "http://purl.org/pav/": "pav",
                       "http://www.w3.org/ns/dcat#": "dcat",
                       "http://xmlns.com/foaf/0.1/": "foaf",
                       "http://www.w3.org/2002/07/owl#": "owl",
                       "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
                       "http://www.w3.org/2004/02/skos/core#": "skos",
                       }
    ############### EXECUTION ###############

    run(base_input_dir="/home/danif/datasets/pdb_part_",
        out_path_template="/home/danif/datasets/results/pdbsubset_1124/t0_split_{}/result_{}",
        namespaces=namespaces_dict,
        list_of_file_groupings=[22,45,77,91,114,137])
