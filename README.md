# Structural queries


## API

- UniProt: https://www.uniprot.org/help/programmatic_access
- RCSB PDB: https://www.rcsb.org/pages/webservices
- PDBe: https://www.ebi.ac.uk/pdbe/pdbe-rest-api
- AlphaFoldDB: https://alphafold.ebi.ac.uk/api-docs
- ESM Atlas: https://esmatlas.com/about#api


## Packages

- biopython: https://biopython.org
- foldseek: https://foldseek.com
- foldcomp: https://github.com/steineggerlab/foldcomp
- rcsbsearchapi: https://rcsbsearchapi.readthedocs.io


## TODOS

- [ ] Pipeline:
    - [ ] Human/Drosophila proteins
    - [ ] grouped by UniProt id
    - [ ] only CryoEM
    - [ ] sorted by date
    - [ ] only membrane proteins
    - [ ] resolution < 3.5A
    - [ ] check protein coverage -> 1. resolved cytosolic domain or 2. good quality of other domains and alphafold prediction of extracellular domain
    - [ ] check for keywords / gene ontology terms
    - [ ] check for strcutural similarity against known and predicted structures
- [ ] Check agains GO Blacklist


Residue limit -> 512 resdiues
Biosafety concern -> only PDB entries allowed

Pre-selection pipeline:
- crop to 512 residues
- do 12 designs and then extend
- hotspots - hydrophobic patches, first run without hotspots and then close in on hotspots
