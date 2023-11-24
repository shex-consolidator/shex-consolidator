from shex_consolidator.experimentation.schema_comparator import compare_shex_files
from shex_consolidator.experimentation.csv_formatter import json_to_csv


if __name__ == "__main__":
    # json_result = compare_shex_files(file_path2=r"C:\Users\Dani\datasets\shex-consolidator\pdb_single_file\single_file_pdb.shex",
    #                                  file_path1=r"C:\Users\Dani\repos_git\consolidator-shex\shex_consolidator\result_pdb_100000_v3.shex")

    json_result = compare_shex_files(
        file_path2=r"C:\Users\Dani\datasets\shex-consolidator\pdb_single_file\single_file_pdb.shex",
        file_path1=r"C:\Users\Dani\repos_git\consolidator-shex\result_pdb_11_files_half_gb.shex")
        # file_path1=r"C:\Users\Dani\datasets\shex-consolidator\pdb_11_split\instances_cap_3100_pdb.shex")

    json_to_csv(file_path="comparison_eukaryota_mesozoa_11_files.csv",
                file_title="Comparison between classic and consolidation approaches "
                            "for the file in {} using a {} line split".format(
                     "https://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf.xz",
                     1100000),
                json_stats=json_result)

    # json_to_csv(file_path="comparison_eukaryota_mesozoa_instances_cap_3100.csv",
    #             file_title="Comparison between classic and sampling approaches "
    #                        "for the file in {} using a {} instances per shape sample".format(
    #                 "https://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf.xz",
    #                 3100),
    #             json_stats=json_result)