# DNA-doh

DNA-doh has three goals:

1.  Learn how to structure and develop a medium-sized Python project.
2.  Explore design options for a typical data analysis project.
3.  Have fun learning more about Python and programming.

DNA-doh includes the core features of pipelines used to correlate variations in genotypes and phenotypes,
such as downloading datasets, reconstructing individual genomes, finding statistical correlations, and reporting results.
It also includes the essential features of a robust Python project,
including task automation, unit tests, style checking, and embedded documentation.
Contributions are welcome:
please contact the authors, file an issue, or submit a pull request if you'd like to get involved.
(Please note that all contributors are required to abide by our [Code of Conduct](./CODE_OF_CONDUCT.md).)

## Overview

We want to demonstrate how correlate variations in people's genes with variations in their phenotypes
(i.e., their physical characteristics).
To do this we need data describing individuals
whose physical differences correlate with differences in their genes.
We could subset real data from a source like the [UK Biobank](https://www.ukbiobank.ac.uk/),
but (a) there are privacy concerns and intellectual property restrictions
and (b) that data is very complex.
Instead,
DNA-doh synthesizes simple datasets that include specific variations.

## Software

-   `cache.py`: provide a local cache of remote files.
    -   `cache.py` can use a directory on the local file system as a source of files
        as well as an actual remote filestore.
-   `synthesize.py`: synthesize genotypes and phenotypes.
    -   Run `python dnadoh/synthesize.py --help` for options.
-   `assemble.py`: assemble a set of synthesized files as dataframes to organize the mutations observed in each individual.
    -   Data could be synthesized in this format directly,
        but one of DNA-doh's goals is to reproduce the steps in production data pipelines.
-   `analyze.py`: Creates visualizations and does simple statistical tests.
    -   Looks at the distribution of a continuous measured phenotype
        based on each base observed at locations that have been mutated
    -   Performs a t-test testing whether the mean of the measured phenotype differs
        based on the base that is observed at that location
    -   Results are displayed on the local webpage spun up by Dash

To test synthesis and assembly:

```bash
# Synthesize data using saved parameters.
$ python dnadoh/synthesize.py --parameters data/example-parameters.json

# List the files produced by synthesis.
$ ls temp*
temp-overall.csv        temp-parameters.json
temp-phenotypes.csv     temp-pid000001.csv
temp-pid000002.csv      temp-pid000003.csv
temp-reference.json

# Analyze the mutated locations (assembles the data under the hood)
$ python dnadoh/analyze.py --input_stem temp
```
