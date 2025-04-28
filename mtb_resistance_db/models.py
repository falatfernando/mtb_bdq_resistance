from sqlalchemy import Column, Integer, String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ReferenceGenome(Base):
    __tablename__ = 'reference_genome'
    
    id = Column(Integer, primary_key=True)
    genome_type = Column(String)
    chromosome = Column(String)
    position = Column(Integer)
    base = Column(String)

    __table_args__ = (
        UniqueConstraint('base', 'position', name='uix_base_position'),     
    )

class ReferenceGenes(Base):
    __tablename__ = 'reference_genes'

    id = Column(Integer, primary_key=True)
    genome_type = Column(String)
    gene_id = Column(String)
    locus_tag = Column(String)
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    strand = Column(String)
    product = Column(String)
    protein_id = Column(String)

    __table_args__ = (
        Index('ix_gene_locus', 'locus_tag'),
    )

class ReferenceProteome(Base):
    __tablename__ = 'reference_proteome'

    id = Column(Integer, primary_key=True)
    genome_type = Column(String)
    protein_id = Column(String)
    fasta_description = Column(String)
    sequence = Column(String)
    length = Column(Integer)
    gene = Column(String)
    locus_tag = Column(String)
    product = Column(String)

class ReferenceExons(Base):
    __tablename__ = 'reference_exons'

    genome_type = Column(String)
    exon_id = Column(Integer, primary_key=True)
    gene_id = Column(String, ForeignKey('reference_genes.gene_id'))
    transcript_id = Column(String)
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    strand = Column(String)
    exon_number = Column(Integer)
    gene = relationship('ReferenceGenes')

class ReferenceRegulatory(Base):
    __tablename__ = 'reference_regulatory'

    id = Column(Integer, primary_key=True)
    genome_type = Column(String)
    genome_position = Column(Integer)
    element_type = Column(String)
    associated_gene = Column(String)
    sequence = Column(String)

# class SNP(Base):
#     __tablename__ = 'snp'

#     snp_id = Column(String, primary_key=True)
#     genome_position = Column(Integer)
#     ref_base = Column(String)
#     alt_base = Column(String)
#     gene_id = Column(String, ForeignKey('reference_genes.gene_id'))
#     variant_type = Column(String)
#     clinical_significance = Column(String)
#     __table_args__ = (Index('ix_snp_position', 'genome_position'),)