from shex_consolidator.consolidator import consolidate_files

import os


def list_files_in_directory(directory_path):
    # List to store all file names
    file_list = []

    # Iterate over all files and subdirectories in the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Append the full path of each file to the list
            file_list.append(os.path.join(root, file))

    return file_list

def complete_with_zeros(target_str: str, lenght: int):
    while len(target_str) < lenght:
        target_str = "0" + target_str
    return target_str

if __name__ == "__main__":

    files = list_files_in_directory(r"C:\Users\Dani\repos_git\shex-consolidator\test_files_local\uniprotkb_shex.tar")
    template = r"C:\Users\Dani\OneDrive - Universidad de Oviedo\papers\yasunori\datasets\t0_split_results\t0_split_{}\result_{}"
    consolidate_files(files, f"shex_results/uniprot_unif.shex", 0)
    print("Done!")