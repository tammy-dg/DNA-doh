"""Assemble data for analysis."""

import csv
import json

import pandas as pd
import util


def read_data(stem):
    """Assemble data from a set of files."""
    reference = _read_reference_genome(stem)
    phenotypes = _read_raw_phenotypes(stem)
    variants, genomes = _read_genomes(stem, reference["genome"], phenotypes)
    phenotypes["genome"] = genomes
    return reference, variants, phenotypes


def _read_genomes(stem, reference, raw_phenotypes):
    """Read variant data and combine with reference to create genome."""
    variants = None
    genomes = []
    for pid in raw_phenotypes["pid"]:
        filename = util.filename_person(stem, pid)
        temp = pd.read_csv(filename)
        temp["pid"] = pid

        if variants is None:
            variants = temp
        else:
            variants = pd.concat([variants, temp])

        genome = list(reference)
        for _, row in temp.iterrows():
            genome[row["loc"] - 1] = row["base"]
        genomes.append("".join(genome))

    return variants, genomes


def _read_raw_phenotypes(stem):
    """Return raw phenotype data as list of dictionaries."""
    filename = util.filename_phenotypes(stem)
    return pd.read_csv(filename)


def _read_reference_genome(stem):
    """Read reference genome (sequence plus mutation location(s))."""
    filename = util.filename_reference_genome(stem)
    with open(filename, "r") as reader:
        return json.load(reader)


if __name__ == "__main__":
    import sys

    reference, variants, phenotypes = read_data(sys.argv[1])
    print(reference)
    print(variants)
    print(phenotypes)
