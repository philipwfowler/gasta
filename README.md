This provides a simple single Python class, Genome, that stores the nucleotide sequence internally as a Numpy array for speed and convenience.

A simple script, `vasta-run.py` shows how you can instantiate the class using a GenBank file and then, by applying the SNPs in a VCF file, re-create the original genome (ignoring INDELS), and then save the resulting FASTA file. 

Philip Fowler
23 May 2019
