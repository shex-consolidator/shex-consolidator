from shex_consolidator.experimentation.schema_comparator import compare_shex_files
from shex_consolidator.experimentation.csv_formatter import json_to_csv


if __name__ == "__main__":
    json_result = compare_shex_files(file_path2=r"C:\Users\Dani\datasets\shex-consolidator\pdb_single_file\single_file_pdb.shex",
                                     file_path1=r"C:\Users\Dani\repos_git\consolidator-shex\shex_consolidator\result_pdb_100000_v2.shex")

    json_to_csv(file_path="comparison_eukaryota_mesozoa_100000split.csv",
                file_title="Comparison between classic and consolidation approahces "
                            "for the file in {} using a {} line split".format(
                     "https://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf.xz",
                     100000),
                json_stats=json_result)
