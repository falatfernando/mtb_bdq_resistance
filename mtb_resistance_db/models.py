from sqlalchemy import Column, Integer, String, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class ReferenceGenome(Base):
    __tablename__ = 'reference_genome'
    id = Column(Integer, primary_key=True)
    genome_type = Column(String)
    chromosome = Column(String)
    position = Column(Integer)
    base = Column(String)

class GeneAnnotation(Base):
    __tablename__ = 'ref_genome_annotation'
    id = Column(Integer, primary_key=True)
    genome_type = Column(String)
    gene_name = Column(String)
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    strand = Column(String)
    product = Column(String)

    # Add an index on gene_name and start_pos for faster lookups
    __table_args__ = (
        Index('ix_gene_annotation_gene_name', 'gene_name'),
        Index('ix_gene_annotation_start_pos', 'start_pos')
    )

class SampleGenome(Base):
    __tablename__ = 'sample_genome'
    id = Column(Integer, primary_key=True)
    genome_type = Column(String)
    sample_name = Column(String)
    chromosome = Column(String)
    position = Column(Integer)
    base = Column(String)
    reference_id = Column(Integer, ForeignKey('reference_genome.id'))
    reference = relationship('ReferenceGenome')