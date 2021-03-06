#! /usr/bin/env python

import logging, os, gzip, bz2

import numpy

from Bio import SeqIO
import vcf
import h5py
from numba import jit

class Genome(object):

    @jit(nopython=False)
    def __init__(self,genbank_file=None,fasta_file=None):

        '''
        Instantiates a genome object by loading a VCF file and storing the whole genome as a numpy array

        Args:
            genbank_file (str): path to the GenBank file to build the reference genome
            fasta_file (str): path to the FASTA file to build the reference genome
        '''

        assert ((genbank_file is not None) or (fasta_file is not None)), "one of a GenBank file or a FASTA file must be specified!"

        # load the specified GenBank file
        if genbank_file is not None:

            # parse the supplied genbank using BioPython
            GenBankFile=SeqIO.read(genbank_file,"genbank")

            # extract the whole genome sequence (Seq object)
            GenBankFileSeq=GenBankFile.seq

            # set some defaults
            self.genbank_reference=True
            self.name="Reference"
            self.additional_metadata=None

            # store some of the metadata, if it is present
            self.id=GenBankFile.id
            if 'organism' in GenBankFile.annotations.keys():
                self.organism=GenBankFile.annotations['organism']
            if 'sequence_version' in GenBankFile.annotations.keys():
                self.sequence_version=GenBankFile.annotations['sequence_version']
            if 'source' in GenBankFile.annotations.keys():
                self.source=GenBankFile.annotations['source']
            if 'taxonomy' in GenBankFile.annotations.keys():
                self.taxonomy=GenBankFile.annotations['taxonomy']

            # convert and store it internally as a numpy array of single chars
            self.bases=numpy.array(list(GenBankFileSeq.tomutable()),dtype="U1")

        # otherwise there must be a FASTA file so load that instead
        elif fasta_file is not None:

            # check if it is compressed and load it accordingly
            if fasta_file.endswith(".gz"):
                INPUT = gzip.open(fasta_file,'rb')
                header=INPUT.readline().decode()
                nucleotide_sequence=INPUT.read().decode()
            elif fasta_file.endswith(".bz2"):
                INPUT = bz2.open(fasta_file,'rb')
                header=INPUT.readline().decode()
                nucleotide_sequence=INPUT.read().decode()
            else:
                INPUT = open(fasta_file,'r')
                header=INPUT.readline()
                nucleotide_sequence=INPUT.read()

            self.genbank_reference=False

            cols=header[1:].split("|")

            if len(cols)>1:
                self.id=cols[0]
                self.organism=cols[1]
                self.name=cols[2]
                if self.name=="Reference":
                    self.genbank_reference=True
            if len(cols)>3:
                self.additional_metadata=cols[3]

            self.bases=numpy.array(list(nucleotide_sequence))

        # insist that bases are lower case
        self.bases=numpy.char.lower(self.bases)

        # store how many bases are in the genome
        self.length=len(self.bases)

        # and an array of positions, counting from 1
        self.positions=numpy.arange(0,self.length,1)

        # create a string of the genome from the numpy array
        self.genome_string=''.join(self.bases)

    def __repr__(self):

        '''
        Overload the print function to write a summary of the genome.
        '''

        line=""
        if hasattr(self,'id'):
            line+=self.id+"\n"
        if hasattr(self,'organism'):
            line+=self.organism+"\n"
        if not self.genbank_reference:
            line+="Sample: "+self.name+"\n"
        else:
            line+="Reference\n"
        if hasattr(self,'path'):
            line+="Path: "+self.path+"\n"
        line+=str(self.length)+" bases\n"
        line+=self.genome_string[:10]+"...."+self.genome_string[-10:]+"\n"
        return(line)

    # @jit(nopython=False)
    def apply_vcf_file(self,filename=None):

        '''
        Load the VCF file and alter the reference genome to re-create the original genome.

        Args:
            filename (str): path to the VCF file

        '''

        self.genbank_reference=False

        # remember the full path to the VCF file
        self.vcf_file=filename

        # remember the folder path and the name of the passed VCF file
        (self.vcf_folder,self.vcf_filename)=os.path.split(self.vcf_file)

        filestem, file_extension = os.path.splitext(self.vcf_filename)

        self.name=filestem

        self.path=self.vcf_folder

        # open the VCF file
        vcf_reader = vcf.Reader(open(self.vcf_file.rstrip(),'r'))

        for record in vcf_reader:

            # find out the position in the genome
            genome_position=int(record.POS)

            ##FIXME need to add record.FILTER=="PASS" when I get new Clockwork files
            # print(record.FILTER)

            # retrieve the details of the row
            row=record.samples[0]

            # find out the reference bases
            ref_bases=record.REF

            # ..and their length
            length_of_variant=len(record.REF)

            # recreate a string of what we expect the reference to be from the genbank file
            # gbk_bases=''.join(reference_genome[genome_position-1:genome_position-1+length_of_variant])
            # assert ref_bases==gbk_bases

            # homozygous variants
            if row.gt_type==2:

                # find out which is the most likely allele in the list
                gt_after=int(row.gt_alleles[1])

                # and hence the alternate bases
                alt_bases=str(record.ALT[gt_after-1])

                # only alter if is a SNP
                if len(ref_bases)==len(alt_bases):

                    for i in alt_bases:

                        # only make a change if it fits in the list!
                        if genome_position <= self.length:
                            self.bases[genome_position]=i.lower()

                        genome_position+=1

            # het calls
            elif row.gt_type==1:

                self.bases[genome_position]='n'

                genome_position+=1

            # null calls
            elif row['GT']=='./.':

                self.bases[genome_position]='-'

                genome_position+=1

        # create a string of the genome from the numpy array
        self.genome_string=''.join(self.bases)

    @jit(nopython=True)
    def _calculate_difference(ref,alt,pos):

        result=[]
        for (i,j,k) in zip(pos,ref,alt):
            result.append((i,j,k))

        return(result)


    def __sub__(self, other):

        '''
        Overload the subtraction operator so it returns a list of tuples describing the differences between the two genomes.

        '''

        # subtraction only makes sense if the genomes are the same species/length
        # assert self.length==other.length, "the genomes must be the same length!"

        # first store the array of booleans declaring where the arrays are different
        bools_array=self.bases!=other.bases

        ref_array=self.bases[bools_array]

        alt_array=other.bases[bools_array]

        pos_array=self.positions[bools_array]

        result=self._calculate_difference(ref_array,alt_array,pos_array)

        return(result)


    def save_array(self,filename=None):

        '''
        Save the genome as a numpy array

        Args:
            filename (str): path of the output file
        '''

        numpy.save(filename,self.bases)

    def save_hdf5(self,filename=None):

        '''
        Save the genome as a HDF5SUM file (compressed internally using gzip)

        Args:
            filename (str): path of the output file
        '''

        h5f = h5py.File(filename)

        array = self.bases.astype(numpy.string_)

        h5f.create_dataset('genome',data=array,compression='gzip',compression_opts=4)

        h5f.close()

    def _insert_newlines(self, string, every=70):
        '''
        Short private method for inserting a carriage return every N characters.

        Args:
            string (str): the string to insert carriage returns
            every (int): how many characters between each carriage return
        '''

        assert every>0, "every must be an integer greater than zero"

        assert len(string)>1, "string is too short!"

        return '\n'.join(string[i:i+every] for i in range(0, len(string), every))

    def save_fasta(self,filename=None,compression=None,compresslevel=2,additional_metadata=None,chars_per_line=70,nucleotides_uppercase=True):

        '''
        Save the genome as a FASTA file.

        Args:
            filename (str): path of the output file
            compression (str): specify either 'gzip' or 'bzip2'. 'bzip2' is more efficient but 'gzip' is faster. Default is None.
            compresslevel (0-9): the higher the number, the harder the algorithm tries to compress but it takes longer.
            additional_metadata (str): will be added to the header of the FASTA file
            chars_per_line (int): the number of characters per line. Default=70. Must be either a positive integer or None (i.e. no CRs)
        '''

        # check the arguments are well formed
        assert compression in [None,'gzip','bzip2'], "compression must be one of None, gzip or bzip2!"
        assert compresslevel in range(1,10), "compresslevel must be in range 1-9!"
        if chars_per_line is not None:
            assert chars_per_line > 0, "number of characters per line in the FASTA file must be an integer!"

        # check the specified fileextension to see if the FASTA file needs compressing
        if compression=="gzip":
            OUTPUT=gzip.open(filename+".gz",'wb',compresslevel=compresslevel)
        elif compression=="bzip2":
            OUTPUT=bz2.open(filename+".bz2",'wb',compresslevel=compresslevel)
        else:
            OUTPUT=open(filename,'w')

        # create the header line for the FASTA file using "|" as delimiters
        header=">"
        if hasattr(self,'id'):
            header+=self.id+"|"
        if hasattr(self,'organism'):
            header+=self.organism+"|"
        if hasattr(self,'name'):
            header+=self.name
        if additional_metadata is not None:
            header+="|" + additional_metadata
        header+="\n"

        output_string=self._insert_newlines(self.genome_string,every=chars_per_line)
        output_string+="\n"
        if nucleotides_uppercase:
            output_string=output_string.upper()
        else:
            output_string=output_string.lower()

        # write out the FASTA files
        if compression in ['bzip2','gzip']:
            OUTPUT.write(str.encode(header))
            OUTPUT.write(str.encode(output_string))
        else:
            OUTPUT.write(header)
            OUTPUT.write(output_string)

        OUTPUT.close()
