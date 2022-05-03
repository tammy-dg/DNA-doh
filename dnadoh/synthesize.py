"""Synthesize data."""

import csv
import random
import sys
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


def random_genomes(length, num_genomes, num_mutations):
    """Generate a set of genomes with specified number of point mutations.

    1.  Create a reference genome.
    2.  Generate `num_genomes` copies.
    3.  Pick `num_mutations` distinct locations.
    4.  Introduce mutations using `SNP_PROBS` as weights.
    """
    assert 0 <= num_mutations <= length

    # Reference genomes and specific genomes to modify.
    reference = random_sequence(length)
    individuals = [reference] * num_genomes

    # Locations for SNPs.
    locations = random.sample(list(range(length)), num_mutations)

    # Introduce mutations.
    for loc in locations:
        individuals = _mutate_all(reference, individuals, loc)

    # Return reference genome and actual genomes.
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
        person.weight = truncate(random.gauss(mean, std_dev), 1)


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
    person.weight = truncate(1.1 * person.weight, 1)


def _other_bases(seq, loc):
    """Create a list of bases minus the one in the sequence at that location."""
    return list(set(DNA) - {seq[loc]})


# --------------------------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------------------------


def truncate(num, digits):
    """Truncate a number to the specified number of fractional digits."""
    scale = 10**digits
    return int(scale * num) / scale


def write(people):
    """Write people as CSV."""
    if not people:
        return
    headings = people[0].dict().keys()
    writer = csv.DictWriter(sys.stdout, fieldnames=headings)
    writer.writeheader()
    for person in people:
        writer.writerow(person.dict())


# --------------------------------------------------------------------------------------
# Main driver
# --------------------------------------------------------------------------------------


if __name__ == "__main__":
    length = int(sys.argv[1])
    num_genomes = int(sys.argv[2])
    num_mutations = int(sys.argv[3])

    random.seed(int(sys.argv[4]))

    genomes = random_genomes(length, num_genomes, num_mutations)

    pg = PersonGenerator()
    people = [pg.make(genomes.reference, i) for i in genomes.individuals]
    adjust_all(genomes, people, adjust_weight)

    write(people)
