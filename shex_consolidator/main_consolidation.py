from shex_consolidator import consolidate_files

def complete_with_zeros(target_str: str, lenght: int):
    while len(target_str) < lenght:
        target_str = "0" + target_str
    return target_str

if __name__ == "__main__":
    template = r"C:\Users\Dani\datasets\shex-consolidator\pdb_100000_split\pdbsubset_1124\result__"
    files = []
    for i in range(90):
        files.append(template + complete_with_zeros(str(i), 2))
    for i in range(749):
        files.append(template + "9" + complete_with_zeros(str(i), 3))
    # for path in files:
    #     print(path)
    consolidate_files(files, "result_pdb_100000_v3.shex", 0.05)
    print("Done!")