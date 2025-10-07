#!/usr/bin/python
import subprocess, re, shutil, os, random, argparse, gzip
from pathlib import Path
from tabularcompare import Comparison
import search_tools as st
from itertools import chain
import yaml

def stripIDs(df, ids):

    print("start")

    for id in ids:
        id_lst = df[id].tolist()
        prefix = os.path.commonprefix(id_lst)
        suffix = os.path.commonprefix([col[::-1] for col in id_lst])[::-1]
        df[id] = df[id].str.removeprefix(prefix)
        df[id] = df[id].str.removesuffix(suffix)

    return df

def getData(glob, dir, ids, cols, stripID = False):
    # Find the file
    file = st.findFiles2(f"{dir}/{glob}")
    if (len(file) > 1): raise LookupError(f"Duplicate files found for '{glob}' in folder '{dir}'")
    if (len(file) < 1): raise LookupError(f"Cannot find file matching '{glob}' in folder '{dir}'")

    # Import the data
    data = st.importToDataFrame(file[0])

    # Check if desired cols are present
    bad_cols = list(set(ids + cols).difference(data.columns))
    if bad_cols: raise KeyError(f"Cannot find cols '{bad_cols}' in '{file}'")

    #if (stripID): 
    data = stripIDs(data, ids)

    return data[ids + cols]

def main(folder1, folder2, yaml_path):

    with open(yaml_path, 'r') as f:
        load = yaml.load(f, Loader=yaml.SafeLoader)        
        metadata = load.get("metadata")
        files = load.get("files")

    results = []

    for file in files:
        ids = [item.strip() for item in file.get("id").split(',')]
        cols = [item.strip() for item in file.get("columns").split(',')]
        data1 = getData(file.get("path"), folder1, ids, cols, file.get("stripID"))
        data2 = getData(file.get("path"), folder2, ids, cols, file.get("stripID"))
        
        # Do the comparison
        cmp = Comparison(data1, data2, join_columns=ids)
        if cmp.intersect_rows().empty: raise IndexError(f"No comparisons found for '{file.get('path')}'. Maybe the IDs do not match?")

        # Extract non-matching data
        cmp = cmp.diverging_subset()
        if not cmp.empty: results.append((file.get("path"),cmp))
            
    generateReport(metadata, results)

def generateReport(metadata, results):

    report = (
        f"{metadata.get('title')}\n"
        f"{metadata.get('folder1_name')} ==> {metadata.get('folder2_name')}"
    )

    if results:
        for result in results:
            report = f"{report}\n\n{result[0]}\n{result[1].to_string(index=False)}"
    else :
        report = f"{report}\nNo errors detected"

    print (report)


def yaml_type(p):
    ext = Path(p).suffix
    if (ext.lower() != ".yaml"):
        raise argparse.ArgumentTypeError(f"YAML file does not have the extension '.yaml' (case is ignored): {os.path.basename(p)}.")
    return p
    
def folder(p):
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
