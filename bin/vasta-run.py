#! /usr/bin/env python

import copy, numpy, argparse

import vasta

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--vcf_file",required=True,help="the path to a single VCF file")
    parser.add_argument("--genbank_file",default="H37Rv.gbk",help="the genbank file of the H37Rv M. tuberculosis wildtype_gene_collection genome")
    options = parser.parse_args()

    reference=vasta.Genome(genbank_file=options.genbank_file)

    sample=copy.deepcopy(reference)

    filename=options.vcf_file

    sample.apply_vcf_file(filename=filename)

    sample.save_fasta(sample.vcf_folder+"/"+sample.name+".fasta",compression="gzip")

    # sample.save_array(sample.vcf_folder+"/"+sample.name+".npy")

    # sample.save_hdf5(sample.vcf_folder+"/"+sample.name+".hdf5")

    # difference = reference - sample
    #
    # print(len(difference))
    #
    # print(difference[:10])
