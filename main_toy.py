template = r"C:\Users\Dani\datasets\shex-consolidator\pdb_100000_split\pdbsubset_1124\result__"

def complete_with_zeros(target_str: str, lenght: int):
    while len(target_str) < lenght:
        target_str = "0" + target_str
    return target_str


files = []
for i in range(90):
    files.append(template + complete_with_zeros(str(i), 2))
for i in range(749):
    files.append(template + "9" + complete_with_zeros(str(i), 3))

guilty_ones = set()
for a_path in files:
        with open(a_path, "r") as in_file:
            for a_line in in_file:
                if "weso-s:" in a_line:
                    guilty_ones.add(a_path)
                    print(a_path)
                    break

print(len(guilty_ones))
