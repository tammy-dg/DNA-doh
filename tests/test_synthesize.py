"""Test data synthesis."""

from unittest.mock import patch

from pytest import fixture

from dnadoh.synthesize import DNA, GenomeParams, rand_gene, rand_chromosomes, rand_genome


@fixture
def params():
    return GenomeParams(
        num_chromosomes=1,
        min_num_genes=1,
        max_num_genes=1,
        min_num_variants=0,
        max_num_variants=0,
        min_gene_len=1,
        max_gene_len=1
    )


def test_rand_gene_fixed_length():
    gene = rand_gene(3)
    assert len(gene) == 3
    assert all(base in DNA for base in gene)


def test_rand_gene_variable_length():
    for i in range(10):
        gene = rand_gene(3, 5)
        assert 3 <= len(gene) <= 5
        assert all(base in DNA for base in gene)


def test_rand_gene_forced_length():
    with patch("dnadoh.synthesize.random.randint", return_value=5):
        gene = rand_gene(3, 5)
        assert len(gene) == 5
        assert all(base in DNA for base in gene)


def test_rand_chromosomes_minimal_length(params):
    c = rand_chromosomes(params)
    assert len(c) == 2
    assert (len(c[0]) == 1) and (len(c[0][0]) == 1)
    assert (len(c[1]) == 1) and (len(c[1][0]) == 1)


def test_rand_chromosomes_correct_gene_length(params):
    params.min_gene_len = params.max_gene_len = 3
    c = rand_chromosomes(params)
    assert (len(c[0]) == 1) and (len(c[0][0]) == 3)
    assert (len(c[1]) == 1) and (len(c[1][0]) == 3)


def test_rand_chromosomes_correct_num_genes(params):
    params.min_num_genes = params.max_num_genes = 3
    c = rand_chromosomes(params)
    assert (len(c[0]) == 3) and all((len(x) == 1) for x in c[0])
    assert (len(c[1]) == 3) and all((len(x) == 1) for x in c[1])


def test_rand_chromosomes_correct_num_variants(params):
    params.min_num_variants = params.max_num_variants = 1
    with patch("dnadoh.synthesize.rand_gene", side_effect=["A", "T"]):
        c = rand_chromosomes(params)
        assert c[0][0] != c[1][0]


def test_rand_genome_correct_num_chromosomes(params):
    params.num_chromosomes = 3
    g = rand_genome(params)
    assert len(g) == 3
