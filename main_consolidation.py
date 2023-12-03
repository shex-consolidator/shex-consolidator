from shex_consolidator.consolidator import consolidate_files

def complete_with_zeros(target_str: str, lenght: int):
    while len(target_str) < lenght:
        target_str = "0" + target_str
    return target_str

if __name__ == "__main__":
    # template = r"C:\Users\Dani\datasets\shex-consolidator\pdb_100000_split\pdbsubset_1124\result__"
    # files = []
    # for i in range(90):
    #     files.append(template + complete_with_zeros(str(i), 2))
    # for i in range(749):
    #     files.append(template + "9" + complete_with_zeros(str(i), 3))

    n_results = 7
    split_size = 137
    files = []
    template = r"C:\Users\Dani\OneDrive - Universidad de Oviedo\papers\yasunori\datasets\t0_split_results\t0_split_{}\result_{}"
    for i in range(1,n_results + 1):
        files.append(template.format(split_size, i))
    consolidate_files(files, f"shex_results/result_pdb_{split_size}_files_t0.shex", 0)
    print("Done!")