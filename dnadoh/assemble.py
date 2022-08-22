"""Assemble data for analysis."""

import csv
import json
import argparse

import pandas as pd
import util

from sklearn.utils import shuffle


def read_combined(options):
    """Assemble data from a set of files."""
    stem = options.input_stem

    reference = read_reference_genome(stem)
    phenotypes = _read_phenotypes(stem)

    variants = _read_genomes(stem, phenotypes)
    variants = variants.rename(columns={"base": "alternate"})
    variants["reference"] = variants.apply(
        lambda x: reference["genome"][x["location"] - 1], axis=1
    )
    # re-arrange columns as convention is for reference to come before alternate
    new_cols = ["location", "reference", "alternate", "pid"]
    variants = variants[new_cols]

    if options.isolate_families:
        phenotypes, variants = _isolate_families(phenotypes, variants, options)

    combined = pd.merge(phenotypes, variants, on="pid", how="outer")
    return combined


def read_reference_genome(stem):
    """Read reference genome (sequence plus mutation location(s))."""
    filename = util.filename_reference_genome(stem)
    with open(filename, "r") as reader:
        return json.load(reader)snipp


def _read_genomes(stem, raw_phenotypes):
    """Read variant data and combine with reference to create genome."""
    variants = None
    genomes = []
    for pid in raw_phenotypes["pid"]:
        filename = util.filename_person(stem, pid)
        temp = pd.read_csv(filename)
        temp["pid"] = pid
        variants = temp if (variants is None) else pd.concat([variants, temp])
    return variants


def _read_phenotypes(stem):
    """Return raw phenotype data as list of dictionaries."""
    filename = util.filename_phenotypes(stem)
    return pd.read_csv(filename)

def _isolate_families(phenotypes, variants, options):
    phenotypes = shuffle(phenotypes, random_state = options.seed) # shuffling order prevents biasing which duplicate is retained
    phenotypes = phenotypes.drop_duplicates(subset="family_id")
    variants = variants[variants["pid"].isin(phenotypes["pid"])]
    return phenotypes, variants


def parse_args():
    """Get command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_stem", type=str, default=None, help="input path/file stem"
    )
    parser.add_argument(
        "--isolate_families", type=bool, default=True, help="true/false - enforce only one individual per family ID"
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="RNG seed"
    )
    options = parser.parse_args()
    assert options.input_stem is not None, "must specify an input path/file stem"
    return options


if __name__ == "__main__":
    import sys
    options = parse_args()
    combined = read_combined(options)
    print(combined)
    combined.to_csv("testoutput.csv", index=False)
