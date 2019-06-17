#! /usr/bin/env python

import copy, numpy, argparse

import vasta

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--vcf_file",required=True,help="the path to a single VCF file")
    parser.add_argument("--genbank_file",default="H37Rv.gbk",help="the genbank file of the H37Rv M. tuberculosis wildtype_gene_collection genome")
    parser.add_argument("--chars_per_line",default=70,type=int,help="the number of characters per line, default=70, must be either a positive integer or None, None means no carriage returns.")
    parser.add_argument("--nucleotides_lowercase",action="store_true",help="write the nucleotides to the FASTA file in lowercase")
    options = parser.parse_args()

    reference=vasta.Genome(genbank_file=options.genbank_file)

    sample=copy.deepcopy(reference)

    filename=options.vcf_file

    sample.apply_vcf_file(filename=filename)

    if options.nucleotides_lowercase==True:
        uppercase=False
    else:
        uppercase=True

    sample.save_fasta(sample.vcf_folder+"/"+sample.name+".fasta",compression="gzip",chars_per_line=options.chars_per_line,nucleotides_uppercase=uppercase)

    # sample.save_array(sample.vcf_folder+"/"+sample.name+".npy")

    # sample.save_hdf5(sample.vcf_folder+"/"+sample.name+".hdf5")

    # difference = reference - sample
    #
    # print(len(difference))
    #
    # print(difference[:10])
