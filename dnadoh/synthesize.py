"""Synthesize data."""

import argparse
import csv
import json
import random
from typing import List, Optional

from pydantic import BaseModel

# --------------------------------------------------------------------------------------
# Genomes
# --------------------------------------------------------------------------------------


DNA = "ACGT"
SNP_PROBS = (0.50, 0.25, 0.13, 0.12)


class GenePool(BaseModel):
    """A set of genomes."""

    # Number of bases in each genome.
    length: int

    # Reference genome without mutations.
    reference: str

    # Individual genomes.
    individuals: List[str]

    # Locations of mutations.
    locations: List[int]

    def __str__(self):
        """Printable representation."""
        return "\n".join(
            [
                f"length: {self.length}",
                f"reference: {self.reference}",
                "individuals:",
                "\n".join(f"- {i}" for i in self.individuals),
                "locations:",
                "\n".join(f"- {loc}" for loc in self.locations),
            ]
        )


def random_sequence(length):
    """Generate a random sequence of bases of the specified length."""
    assert 0 < length
    return "".join(random.choices(DNA, k=length))


def random_genomes(length, num_genomes, num_snps, max_num_other_mutations):
    """Generate a set of genomes with specified number of point mutations.

    1.  Create a reference genome.
    2.  Generate `num_genomes` copies.
    3.  Pick `num_mutations` distinct locations.
    4.  Introduce significant mutations using `SNP_PROBS` as weights.
    5.  Introduce up to `max_num_other_mutations` at other locations (unweighted).
    """
    assert 0 <= num_snps <= length

    # Reference genomes and specific genomes to modify.
    reference = random_sequence(length)
    individuals = [reference] * num_genomes

    # Locations for SNPs.
    locations = random.sample(list(range(length)), num_snps)

    # Introduce significant mutations.
    for loc in locations:
        individuals = _mutate_all(reference, individuals, loc)

    # Introduce other random mutations.
    other_locations = list(set(range(length)) - set(locations))
    individuals = [
        _mutate_other(i, max_num_other_mutations, other_locations) for i in individuals
    ]

    # Return structure.
    return GenePool(
        length=length, reference=reference, individuals=individuals, locations=locations
    )


def _mutate_all(reference, genomes, loc):
    """Introduce mutations at the specified location.

    The base from the reference genome is retained with probability `SNP_PROBS[0]`.
    The order of other bases is randomized and then they are selected according to
    the other probabilities in `SNP_PROBS`.
    """
    candidates = _other_bases(reference, loc)
    bases = [reference[loc]] + random.sample(candidates, k=len(candidates))
    choices = random.choices(bases, weights=SNP_PROBS, k=len(genomes))
    result = []
    for (i, g) in enumerate(genomes):
        result.append(g[:loc] + choices[i] + g[loc + 1 :])
    return result


def _mutate_other(genome, max_num_mutations, locations):
    """Introduce up to `max_num_mutations` at specified locations."""
    num = min(max_num_mutations, len(genome))
    for loc in random.sample(locations, k=num):
        base = random.choice(_other_bases(genome, loc))
        genome = genome[:loc] + base + genome[loc + 1 :]
    return genome


# --------------------------------------------------------------------------------------
# People
# --------------------------------------------------------------------------------------


class Person(BaseModel):
    """An individual person.

    Values marked `Optional` are filled in one at a time.
    """

    # Genome.
    genome: str

    # Age in years.
    age: Optional[int] = None

    # Genetic sex {"F", "M", "O"}.
    gsex: Optional[str] = None

    # Weight in kg.
    weight: Optional[float] = None


class PersonGenerator:
    """Generate a person given a set of parameters."""

    # Minimum and maximum ages in years.
    MIN_AGE = 25
    MAX_AGE = 75

    # Genetic sex and probability of each.
    GSEX = ("F", "M", "O")
    GSEX_PROBS = (0.49, 0.48, 0.03)

    # Mean weight in kg by genetic sex and relative standard deviation of weights.
    WEIGHT_MEANS = {"F": 80.0, "M": 87.0, "O": 84.0}
    WEIGHT_RSD = 0.12

    def __init__(self):
        """Construct generator."""

    def make(self, reference, individual):
        """Generate a new random person."""
        person = Person(genome=individual)
        for meth in (self.make_age, self.make_gsex, self.make_weight):
            meth(person, reference, individual)
        return person

    def make_age(self, person, reference, individual):
        """Generate a random age.

        Ages are selected uniformly within bounds.
        """
        person.age = random.randint(self.MIN_AGE, self.MAX_AGE)

    def make_gsex(self, person, reference, individual):
        """Generate a random genetic sex.

        Genetic sexes are chosen using weighted probabilities.
        """
        person.gsex = random.choices(self.GSEX, weights=self.GSEX_PROBS)[0]

    def make_weight(self, person, reference, individual):
        """Generate a random weight.

        Weights are chosen from a normal distribution based on genetic sex.
        """
        assert person.gsex is not None
        mean = self.WEIGHT_MEANS[person.gsex]
        std_dev = mean * self.WEIGHT_RSD
        person.weight = _truncate(random.gauss(mean, std_dev), 1)


def adjust_all(genomes, people, func):
    """Adjust a single value based on an SNP.

    1.  Choose one of the mutation locations at random.
    2.  Select a base other than the one in the reference genome at that location.
    3.  Apply the mutation function to everyone who has that base at that location.
    """
    if not genomes.locations:
        return
    loc = random.choice(genomes.locations)
    candidates = _other_bases(genomes.reference, loc)
    marker = random.choice(list(candidates))
    for person in people:
        if person.genome[loc] == marker:
            func(person)


def adjust_weight(person):
    """Adjust a person's weight upward by 10%."""
    person.weight = _truncate(1.1 * person.weight, 1)


# --------------------------------------------------------------------------------------
# I/O
# --------------------------------------------------------------------------------------


def _write(output_stem, genomes, people):
    """Write people as CSV."""
    assert people
    _write_overall(output_stem, people)
    _write_reference_genome(output_stem, genomes)
    _write_variants(output_stem, genomes, people)
    _write_people(output_stem, people)


def _write_overall(output_stem, people):
    """Write DNA sequences and people for reference."""
    filename = f"{output_stem}-overall.csv"
    headings = people[0].dict().keys()
    with open(filename, "w") as raw:
        writer = csv.DictWriter(raw, fieldnames=headings)
        writer.writeheader()
        for person in people:
            writer.writerow(person.dict())


def _write_reference_genome(output_stem, genomes):
    """Save the reference genome and related information."""
    filename = f"{output_stem}-reference.json"
    data = {"genome": genomes.reference, "locations": list(sorted(genomes.locations))}
    with open(filename, "w") as writer:
        json.dump(data, writer)


def _write_variants(output_stem, genomes, people):
    """Write one variant file per person."""
    width = len(str(len(people)))
    for (pid, person) in enumerate(people):
        pid_str = str(pid).zfill(width)
        filename = f"{output_stem}-pid{pid_str}.csv"
        with open(filename, "w") as raw:
            writer = csv.DictWriter(raw, fieldnames=["loc", "base"])
            writer.writeheader()
            for i in range(len(genomes.reference)):
                if person.genome[i] != genomes.reference[i]:
                    writer.writerow({"loc": i, "base": person.genome[i]})


def _write_people(output_stem, people):
    """Write phenotypic data for people."""
    filename = f"{output_stem}-people.csv"
    headings = people[0].dict()
    del headings["genome"]
    headings["pid"] = 0
    with open(filename, "w") as raw:
        writer = csv.DictWriter(raw, fieldnames=headings)
        writer.writeheader()
        for (pid, person) in enumerate(people):
            details = person.dict()
            del details["genome"]
            details["pid"] = pid
            writer.writerow(details)


# --------------------------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------------------------


def _other_bases(seq, loc):
    """Create a list of bases minus the one in the sequence at that location."""
    return list(set(DNA) - {seq[loc]})


def _truncate(num, digits):
    """Truncate a number to the specified number of fractional digits."""
    scale = 10**digits
    return int(scale * num) / scale


# --------------------------------------------------------------------------------------
# Main driver
# --------------------------------------------------------------------------------------


def main():
    """Main driver."""
    options = parse_args()
    random.seed(options.seed)
    genomes, people = generate(options)
    _write(options.output_stem, genomes, people)


def parse_args():
    """Get command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, help="genome length")
    parser.add_argument("--num_genomes", type=int, help="number of genomes (people)")
    parser.add_argument(
        "--num_mutations", type=int, help="number of significant mutations"
    )
    parser.add_argument(
        "--max_num_other_mutations",
        type=int,
        help="maximum number of other mutations per person",
    )
    parser.add_argument("--seed", type=int, help="RNG seed")
    parser.add_argument("--output_stem", type=str, help="output path/file stem")
    return parser.parse_args()


def generate(options):
    """Generate genomes and people from parameters."""
    genomes = random_genomes(
        options.length,
        options.num_genomes,
        options.num_mutations,
        options.max_num_other_mutations,
    )
    pg = PersonGenerator()
    people = [pg.make(genomes.reference, i) for i in genomes.individuals]
    adjust_all(genomes, people, adjust_weight)
    return genomes, people


if __name__ == "__main__":
    main()
