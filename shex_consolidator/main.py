from shex_consolidator import consolidate_files

if __name__ == "__main__":
    template = r"C:\Users\Usuario\repos_git\shex-consolidator\examples\pdb_subset{}.shex"
    files = [template.format(i) for i in range(10)]
    consolidate_files(files, "result.shex")
    print("Done!")