#!/usr/bin/python
import subprocess, re, shutil, os, random, argparse, gzip
from pathlib import Path
from tabularcompare import Comparison
import search_tools as st
from itertools import chain
import yaml

def compare(folder1, folder2, yaml):
    print ("blah")

def compareFile(file1, file2, ids, columns):    
    folder1 = st.importToDataFrame(file1)[ids + columns]
    folder2 = st.importToDataFrame(file2)[ids + columns]
    cmp = Comparison(folder1, folder2, join_columns=ids)
    return cmp

def main(folder1, folder2, yaml_path):

    with open(yaml_path, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader).get("files")

    results = []

    for file in data:
        file1 = st.findFiles(file.get("path"), target_directory = folder1)
        if (len(file1) > 1): raise LookupError(f"Duplicate files found in folder: {file1}")
        
        file2 = st.findFiles(file.get("path"), target_directory = folder2)
        if (len(file2) > 1): raise LookupError(f"Duplicate files found in folder: {file2}")
        
        ids = [item.strip() for item in file.get("id").split(',')]
        cols = [item.strip() for item in file.get("columns").split(',')]

        cmp = compareFile(file1[0], file2[0], ids, cols).diverging_subset()
        if not cmp.empty: results.append(cmp)

        print("test")

    print("blah")


def file_choices(choices,fname):
    ext = os.path.splitext(fname)[1][1:]
    if ext not in choices:
       parser.error("file doesn't end with one of {}".format(choices))
    return fname

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
