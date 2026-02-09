#!/usr/bin/python
import subprocess, re, shutil, os, random, argparse, gzip
from pathlib import Path
from tabularcompare import Comparison
import search_tools as st
from itertools import chain
import pandas as pd
import yaml
from datetime import date

def stripIDs(df: pd.DataFrame, ids: list[str]):
    """Strips the common prefix and suffix off of ID columns in a dataframe
    :param df: The input dataframe
    :param ids: The ID columns to strip
    :return: Dataframe with stripped columns
    """
    # Iterate through the IDs and remove any common prefix or suffixes
    for id in ids:
        id_lst = df[id].tolist()
        prefix = os.path.commonprefix(id_lst)
        suffix = os.path.commonprefix([col[::-1] for col in id_lst])[::-1]
        df[id] = df[id].str.removeprefix(prefix)
        df[id] = df[id].str.removesuffix(suffix)

    return df

def getData(glob: str, dir: str, ids: list[str], cols:list[str], stripID: bool = False):
    """Finds a file in a specified directory, checks to see if the necessary columns are present, then strips the ID columns for common prefix/suffix
    :param glob: The file to search for
    :param dir: The directory to search in
    :param ids: The ID columns for later merging
    :param cols: The columns to be compared
    :param stripID: Should the ID columns be stripped for common prefix/suffix, defaults to False
    :raises LookupError: If multiple files are found
    :raises LookupError: If no files are found
    :raises KeyError: If necessary columns are not present
    :return: Dataframe containing on the desired data
    """    
    # Find the file
    file = st.findFiles2(f"{dir}/{glob}")
    if (len(file) > 1): raise LookupError(f"Multiple files found for '{glob}' in folder '{dir}'. Please refine search terms.")
    if (len(file) < 1): raise LookupError(f"Cannot find file matching '{glob}' in folder '{dir}'")
    file = file[0]

    # Import the data
    data = st.importToDataFrame(file)

    # Check if desired cols are present
    bad_cols = list(set(ids + cols).difference(data.columns))
    if bad_cols: raise KeyError(f"Cannot find cols '{bad_cols}' in '{file}'")

    if (stripID): data = stripIDs(data, ids)

    return (file, data[ids + cols])

def compare(folder1: str, folder2: str, yamlpath: str, outdir: str = ""):
    """Compares files in two folders to determine any discrepancies
    :param folder1: The path to the first folder
    :param folder2: The path to the second folder
    :param yaml_path: The path to the YAML containing the comparison criteria
    :raises IndexError: If no matching IDs are found
    """
    with open(yamlpath, 'r') as f:
        load = yaml.load(f, Loader=yaml.SafeLoader)        
        metadata = load.get("metadata")
        files = load.get("files")

    results = []

    # Iterate through each desired comparison file
    for file in files:
        ids = [item.strip() for item in file.get("id").split(',')]
        cols = [item.strip() for item in file.get("columns").split(',')]

        file1, data1 = getData(file.get("path"), folder1, ids, cols, file.get("stripID"))
        file2, data2 = getData(file.get("path"), folder2, ids, cols, file.get("stripID"))

        evalBool = lambda b: b == "True"

        ignore_case = evalBool(load.get("ignore_case", 'False'))
        ignore_whitespace = evalBool(load.get("ignore_whitespace", 'False'))
        tolerance = str(file.get("tolerance"))

        # Do the comparison
        absolute = relative = 0
        if (tolerance != "None"):
            if "%" in tolerance:
                relative = float(tolerance.replace("%", ""))
                tolerance = f"\nTolerance ± {relative}%"
            else:
                absolute = float(tolerance)
                tolerance = f"\nTolerance ± {absolute}"
        else:
            tolerance = ""

        cmp = Comparison(data1, data2, join_columns=ids, abs_tol = absolute, rel_tol = relative, df1_name='original', df2_name='new', 
                         ignore_spaces = ignore_whitespace, ignore_case = ignore_case)
        if cmp.intersect_rows().empty: raise IndexError(f"No comparisons found for '{file.get('path')}'. Maybe the IDs do not match?")

        cmp = cmp.diverging_subset()

        # Extract non-matching data
        if cmp.empty: cmp = pd.DataFrame(columns=['No discrepancies found'])
        results.append((f"File 1: {file1}\nFile 2: {file2}\nID: {', '.join(ids)} | Cols: {', '.join(cols)}",cmp.fillna(''),tolerance))
            
    generateReport(metadata, results, outdir)

def generateReport(metadata: str, results: str, outdir: str = ""):
    """Generates the report from the comparison
    :param metadata: The metadata from YAML (title, names)
    :param results: The results from the comparison
    """
    report = (
        f"{metadata.get('title')}\n"
        f"{metadata.get('folder1_name')} ==> {metadata.get('folder2_name')}\n"
        f"Date: {date.today().strftime('%d %b %Y')}\n\n"
        f"-----------------------------"
    )

    # Concat the diverging data
    if results:
        for result in results:
            report = f"{report}\n\n{result[0]}\n{result[1].to_markdown(index=False, tablefmt='rounded_outline')}{result[2]}"
    else :
        report = f"{report}\nNo errors detected"

    if (outdir):
        with open(os.path.join(outdir,"compare_report.txt"), "w") as file:
            file.write(report)
    else:
        print (report)

def yaml_type(p: str):
    """Defines the YAML type
    :param p: The path to the YAML
    :raises argparse.ArgumentTypeError: If input file does not have the type '.yaml' or '.yml'
    :return: The path to the YAML
    """    
    ext = Path(p).suffix
    if (ext.lower() not in [".yaml",".yml"]):
        raise argparse.ArgumentTypeError(f"YAML file does not have the extension '.yaml' (case is ignored): {os.path.basename(p)}.")
    return p
    
def folder(p: str):
    """Defines the folder type
    :param p: The path to the folder
    :raises argparse.ArgumentTypeError: If input file is not a folder
    :return: The path to the folder
    """    
    if not Path.is_dir(Path(p)):
        raise argparse.ArgumentTypeError(f"Input is not a folder or cannot be found: {p}")
    return p

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--folder1', required=True, type=folder, help="Path to first folder")
    parser.add_argument('-g','--folder2', required=True, type=folder, help="Path to second folder")
    parser.add_argument('-y','--yaml', required=True, type=yaml_type, help="Path to the config YAML file")
    parser.add_argument('-o','--outdir', required=False, type=folder, help="Path to output folder for report", default="")
    args = parser.parse_args()
    compare(args.folder1, args.folder2, args.yaml, args.outdir)