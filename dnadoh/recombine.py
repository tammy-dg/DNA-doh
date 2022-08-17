"""Recombination of the genomes of two people
to produce a third person. Other features are
averaged with some noise.
"""

from typing import List
from .synthesize import PersonGenerator, Person

def recombine(
    person1: Person,
    person2: Person,
    reference_genome: str,
    pid: str,
    recombination_prob: List[float],
    recombination_loci: List[int]
    ) -> Person:
    """Recombine two genomes"""
    # Error checking
    assert len(recombination_loci) == len(recombination_prob)
    assert len(person1.genome) == len(person2.genome)
    assert all(recombination_loci >= 0 & recombination_loci < len(person1.genome))
    assert all(recombination_prob <= 1 & recombination_prob >= 0)

    # Initializing
    genome1 = person1.genome
    genome2 = person2.genome

    # If the index 0 is not in the list of recombination loci
    # Add it to initialize recombination by selecting either genome
    # with equal probability
    if 0 not in recombination_loci:
        recombination_loci = [0] + recombination_loci
        recombination_prob = [0.5] + recombination_prob
    # Adding the last coordinate of the dna to provide an end index
    # for the last segment that can be recombined
    if len(genome1) not in recombination_loci:
        recombination_loci = recombination_loci + [len(genome1)]
        recombination_prob = recombination_prob + [0]

    ## Ordering
    ordered_prob = [prob for _, prob in sorted(zip(recombination_loci, recombination_prob))]
    ordered_loci = sorted(recombination_loci)

    # Recombining genomes
    recombination_genome = []
    for i, loc in enumerate(ordered_loci[:-1]):
        genome_seg = _choose_one([1, 2], [ordered_prob[i], (1 - ordered_prob[i])])
        recombination_genome.append(
            genome1[loc:ordered_loci[(i + 1)]] if genome_seg == 1 else genome2[loc:ordered_loci[(i + 1)]]
        )
    recombination_genome = "".join(recombination_genome)

    # Generate a new person with the recombinant genome
    person_generator = PersonGenerator()
    person3 = person_generator.make(reference_genome, recombination_genome, pid)
    return person3
