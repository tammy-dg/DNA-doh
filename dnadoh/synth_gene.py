"""Synthesize genomic data."""


import random

from pydantic import BaseModel


# Bases.
DNA = "ACGT"

# How many times to try to find a variant allele?
MAX_TRIES = 100

class GenomeParams(BaseModel):
    """Params for genome synthesis."""
    num_chromosomes: int
    min_num_genes: int
    max_num_genes: int
    min_num_variants: int
    max_num_variants: int
    min_gene_len: int
    max_gene_len: int


def rand_gene(min_len, max_len=None):
    """Create a random gene.

    -  If `max_len` is provided, the gene has a random length.
    -  If not, the gene's length is specified by the first argument.
    """
    if max_len is None:
        length = min_len
    else:
        length = random.randint(min_len, max_len)
    return "".join(random.choices(DNA, k=length))


def rand_chromosomes(params):
    """Create a pair of random chromosomes.

    -  Both chromosomes have `num_genes` genes.
    -  `num_variants` of these are different (i.e., alleles).
    -  Each gene has `min_len` <= len(gene) <= `max_len`.
    """
    num_genes = random.randint(params.min_num_genes, params.max_num_genes)
    num_variants = random.randint(params.min_num_variants, params.max_num_variants)
    variant_locs = set(random.sample(list(range(num_genes)), k=num_variants))

    left_chromosome, right_chromosome = [], []
    for i in range(num_genes):
        gene = rand_gene(params.min_gene_len, params.max_gene_len)
        left_chromosome.append(gene)
        if i in variant_locs:
            right_chromosome.append(_rand_allele(gene))
        else:
            right_chromosome.append(gene)

    return (left_chromosome, right_chromosome)


def _rand_allele(gene):
    """Try to generate a random allele of fixed length."""
    for i in range(MAX_TRIES):
        other = rand_gene(len(gene))
        if other != gene:
            return other
    assert other is not None, f"Could not find allele for {gene}"


def rand_genome(params):
    """Create a random genome."""
    return [rand_chromosomes(params) for i in range(params.num_chromosomes)]
