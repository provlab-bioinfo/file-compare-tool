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

    # Import the data
    data = st.importToDataFrame(file[0])

    # Check if desired cols are present
    bad_cols = list(set(ids + cols).difference(data.columns))
    if bad_cols: raise KeyError(f"Cannot find cols '{bad_cols}' in '{file}'")

    if (stripID): data = stripIDs(data, ids)
    return data[ids + cols]

def main(folder1: str, folder2: str, yaml_path: str):
    """Compares files in two folders to determine any discrepancies
    :param folder1: The path to the first folder
    :param folder2: The path to the second folder
    :param yaml_path: The path to the YAML containing the comparison criteria
    :raises IndexError: If no matching IDs are found
    """
    with open(yaml_path, 'r') as f:
        load = yaml.load(f, Loader=yaml.SafeLoader)        
        metadata = load.get("metadata")
        files = load.get("files")

    results = []

    # Iterate through each desired comparison file
    for file in files:
        ids = [item.strip() for item in file.get("id").split(',')]
        cols = [item.strip() for item in file.get("columns").split(',')]
        data1 = getData(file.get("path"), folder1, ids, cols, file.get("stripID"))
        data2 = getData(file.get("path"), folder2, ids, cols, file.get("stripID"))
        
        # Do the comparison

        tolerance = str(file.get("tolerance"))
        absolute = relative = 0
        if (tolerance != "None"):
            if "%" in tolerance:
                relative = float(tolerance.replace("%", ""))
            else:
                absolute = float(tolerance)

        cmp = Comparison(data1, data2, join_columns=ids, abs_tol = absolute, rel_tol = relative, df1_name='original', df2_name='new')
        if cmp.intersect_rows().empty: raise IndexError(f"No comparisons found for '{file.get('path')}'. Maybe the IDs do not match?")

        # Extract non-matching data
        cmp = cmp.diverging_subset()
        if not cmp.empty: results.append((file.get("path"),cmp))
            
    generateReport(metadata, results)

def generateReport(metadata: str, results: str):
    """Generates the report from the comparison
    :param metadata: The metadata from YAML (title, names)
    :param results: The results from the comparison
    """
    report = (
        f"{metadata.get('title')}\n"
        f"Date: {date.today().strftime('%d %b %Y')}\n"
        f"{metadata.get('folder1_name')} ==> {metadata.get('folder2_name')}\n\n"
        f"-----------------------------\n"
    )

    # Concat the diverging data
    if results:
        for result in results:
            report = f"{report}\n\n{result[0]}\n{result[1].to_string(index=False)}"
    else :
        report = f"{report}\nNo errors detected"

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
    args = parser.parse_args()
    main(args.folder1, args.folder2, args.yaml)
