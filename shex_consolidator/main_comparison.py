from experimentation.schema_comparator import compare_shex_files
# import json



json_result = compare_shex_files(file_path2=r"C:\Users\Dani\datasets\shex-consolidator\pdb_single_file\single_file_pdb.shex",
                                 file_path1=r"C:\Users\Dani\repos_git\consolidator-shex\shex_consolidator\result_pdb_100000.shex")

print(json_result)