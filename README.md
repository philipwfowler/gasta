This provides a simple single Python class, Genome, that stores the nucleotide sequence internally as a Numpy array for speed and convenience.

A simple script, `vasta-run.py` shows how you can instantiate the class using a GenBank file and then, by applying the SNPs in a VCF file, re-create the original genome (ignoring INDELS), and then save the resulting FASTA file. 

```
$ ls examples/01/
01.vcf

$ vasta-run.py --vcf_file examples/01/01.vcf --genbank_file config/H37rV_v3.gbk 

$ $ ls examples/01/
01.fasta.gz      01.vcf

$ gunzip examples/01/01.fasta.gz 
$ less examples/01/01.fasta 
>NC_000962.3|Mycobacterium tuberculosis H37Rv|01
ttgaccgatgaccccggttcaggcttcaccacagtgtggaacgcggtcgtctccgaacttaacggcgaccctaaggttgacgacggacccagcagtgatgctaatctcagcgctccgctgacccctcagcaaagggcttggctcaatctcgtccagccat..
```

Philip Fowler
23 May 2019
