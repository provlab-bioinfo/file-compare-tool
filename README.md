
# file-compare-tool
 [![Lifecycle: WIP](https://img.shields.io/badge/lifecycle-WIP-yellow.svg)](https://lifecycle.r-lib.org/articles/stages.html#experimental) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/provlab-bioinfo/hnoss/issues) [![License: GPL3](https://img.shields.io/badge/license-GPL3-lightgrey.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html) [![minimal Python version: 3.10](https://img.shields.io/badge/Python-3.10-6666ff.svg)](https://www.python.org/) [![Package Version = 0.0.1](https://img.shields.io/badge/Package%20version-0.0.1-orange.svg?style=flat-square)](https://github.com/provlab-bioinfo/file-compare-tool/blob/main/NEWS) [![Last-changedate](https://img.shields.io/badge/last%20change-2025--Oct--07-yellowgreen.svg)](https://github.com/provlab-bioinfo/file-compare-tool/blob/main/NEWS)

## Introduction

This package aids in comparing files, and is designed for validating pipeline updates at APL.

## Table of Contents

- [Introduction](#introduction)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [Input](#input)
- [Output](#output)
- [Workflow](#workflow)
- [References](#references)

## Dependencies

See [environment.yml](environment.yml) and [requirements.txt](requirements.txt) for package dependancies.

## Installation

Install with pip:

```bash
$ pip install git+https://github.com/provlab-bioinfo/file-compare-tool
```

Access in python:

```python
>>> import file_compare_tool
```

## Input
- ```--folder1```: Path to the first folder<br>
- ```--folder2```: Path to the second folder<br>
- ```--yaml```: Path to the YAML config file. Must be of type ```.yml``` or ```.yaml``` and use the following format:
    ```yaml
    metadata:
    title: [Title for the report]
    folder1_name: [Version number of original tool]
    folder2_name: [Version number of updated tool]
    files: 
    - path: [Glob search string for the desired file]
        id: [Columns to merge on]
        columns: [Columns to compare]
        stripID: [True/False]
    - path: [Additional files to compare]
        ...
    ```

## Output

#### Example output for comparing COVID analysis pipelines
```
Comparison for COVID analysis update.
v1.1.3 ==> v1.1.4

/**/all_data/*_nextclade.tsv
seqName      qc.overallStatus
 70_S70 {good} --> {mediocre}
 71_S71  {mediocre} --> {bad}
 83_S83 {mediocre} --> {good}
 89_S89         {good} --> {}

/**/all_data/*_lineage_report.csv
 taxon                 lineage
40_S40      {AY.27} --> {None}
65_S65      {AY.27} --> {None}
87_S87 {AY.25} --> {B.1.617.2}
89_S89      {AY.74} --> {None}
```