#!/usr/bin/python
import subprocess, re, shutil, os, random, argparse, gzip
from pathlib import Path
import searchTools as st

def compare(folder1, folder2, yaml):
    print ("blah")

def compareFile(file1, file2, id, columns):
   df1 = st.importToDataFrame(file1)[[id] + columns]
   df2 = st.importToDataFrame(file2)[[id] + columns]

def main(args):
    compare(args.folder1, args.folder2, args.yaml)

def file_choices(choices,fname):
    ext = os.path.splitext(fname)[1][1:]
    if ext not in choices:
       parser.error("file doesn't end with one of {}".format(choices))
    return fname

def yaml(p):
    ext = Path(p).suffix
    if (ext.lower() != ".yaml"):
        raise argparse.ArgumentTypeError(f"YAML file does not have the extension '.yaml' (case is ignored): {os.path.basename(p)}.")
    return p
    
def folder(p):
    if not Path.isdir(p):
        raise argparse.ArgumentTypeError(f"Input is not a folder or cannot be found: {p}")
    return p

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--folder1', required=True, type=folder, help="Path to first folder")
    parser.add_argument('-g','--folder2', required=True, type=folder, help="Path to second folder")
    parser.add_argument('-y','--yaml', required=True, type=yaml, help="Path to the config YAML file")
    args = parser.parse_args()
    main(args)
