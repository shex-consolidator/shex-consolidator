from shex_consolidator.experimentation.schema_comparator import compare_shex_files
from shex_consolidator.experimentation.csv_formatter import json_to_csv


if __name__ == "__main__":
    # json_result = compare_shex_files(file_path2=r"C:\Users\Dani\datasets\shex-consolidator\pdb_single_file\single_file_pdb.shex",
    #                                  file_path1=r"C:\Users\Dani\repos_git\consolidator-shex\shex_consolidator\result_pdb_100000_v3.shex")

    # n_files = 137
    instances_cap = 27800

    json_result = compare_shex_files(
        file_path1=r"C:\Users\Dani\datasets\shex-consolidator\pdb_single_file\single_file_t0_pdb.shex",
        # file_path2=r"C:\Users\Dani\repos_git\consolidator-shex\result_pdb_100000_v4.shex")
        # file_path2=r"C:\Users\Dani\repos_git\consolidator-shex\shex_results\result_pdb_{}_files_t0.shex".format(n_files))
        file_path2=r"C:\Users\Dani\OneDrive - Universidad de Oviedo\papers\yasunori\datasets\t0_samp_results\t0_sampling_results\instances_cap_{}_pdb_t0.shex".format(instances_cap))

    # json_to_csv(file_path="comparison_eukaryota_mesozoa_100000_v4.csv",
    #             file_title="Comparison between classic and consolidation approaches "
    #                         "for the file in {} using a {} line split".format(
    #                  "https://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf.xz",
    #                  100000),
    #             json_stats=json_result)

    # json_to_csv(file_path="cmp_results\\comparison_eukaryota_mesozoa_{}_files_t0.csv".format(n_files),
    #             file_title="Comparison between classic and consolidation approaches "
    #                        "for the file in {} using a {} line split, and {} threshold".format(
    #                 "https://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf.xz",
    #                 n_files*100000,
    #                 0),
    #             json_stats=json_result)

    json_to_csv(file_path="cmp_results\\comparison_eukaryota_mesozoa_instances_cap_{}_t0.csv".format(instances_cap),
                file_title="Comparison between classic and sampling approaches "
                           "for the file in {} using a {} instances per shape sample and {} threshold".format(
                    "https://ftp.uniprot.org/pub/databases/uniprot/current_release/rdf/uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf.xz",
                    instances_cap,
                    0),
                json_stats=json_result)