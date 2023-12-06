# shex-consolidator


This repository contains code for:
* Merging a set of ShEx schemas into a single one. This new schema consolidates and merges into a single element the shapes associated to the same shape label in the input schemas.
* Comparing the similarity of two ShEx schemas, both at shape and constraint level.

To perform shex consolidation, use the function consolidate_files(list_of_shex_files: list, output_file: str, acceptance_threshold: float), available in the module [shex_consolidator.consolidator](https://github.com/shex-consolidator/shex-consolidator/blob/main/shex_consolidator/consolidator.py). You have a example on how to use this function in the script [main_consolidation](https://github.com/shex-consolidator/shex-consolidator/blob/main/main_consolidation.py). This function expects to receive:
* A list of input files, where each file contains a ShEx schema.
* A disk path to write the resulting schema.
* The minimun support that a constraint should have among the data to be accepted as part of the final schema.

To perform schema comparison, use the funcion compare_shex_files(file_path1: str, file_path2: str), available in the module [shex_consolidator.experimentation.schema_comparator](https://github.com/shex-consolidator/shex-consolidator/blob/main/shex_consolidator/experimentation/schema_comparator.py). This function expects to receive two disk paths, each one containing a ShEx schema. It returns a dict/json object with different statistical information. If you want to serialize this object to a self-explanatory CSV file, you can use the function json_to_csv available in the module [shex_consolidator.experimentation.csv_formatter](https://github.com/shex-consolidator/shex-consolidator/blob/main/shex_consolidator/experimentation/csv_formatter.py). You have an example on how to combine these two funcions in the script [main_comparison](https://github.com/shex-consolidator/shex-consolidator/blob/main/main_comparison.py).


# Experimental results

This repository also contains some experimental results fo consolidating and comparing content from a [UniProt sub-graph](https://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf.xz). Such results can be found in the folders [cmp_results](https://github.com/shex-consolidator/shex-consolidator/tree/main/cmp_results) and [shex_results](https://github.com/shex-consolidator/shex-consolidator/tree/main/shex_results)
