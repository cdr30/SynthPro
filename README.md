# SynthPro
SynthPro is a python utility for generating synthetic versions of observed ocean temperature and salinity profiles using output from an ocean general circulation model. 


## Method
For each observed temperature and salinity profile, SynthProextracts a model analog using a 'nearest-neighbour' algorithm. SynthPro vertically interpolates model data onto observed depths, or optionally, can return profiles extracted over the full-depth of the model domain. 





## Data formats
### Observed profiles
Observational profiles must be provided in the netcdf format used by the [EN4 database][EN4-ref]. Date and time information within the input file is ignored and SynthPro will attempt to extract synthetic versions of all observed profiles.

### Synthetic profiles
Synthetic profiles are returned in the same netcdf format as the observational data with an additional variable `distance_to_ob` describing the distance on a spher

. Profiles that could not be extracted from an equivalent model location are returned as missing data. 

### Model data
distance_to_ob

Ocean model data must be provided in a netcdf format with a depth (z-level) vertical coordinate. 



## Dependencies
SynthPro was developed using Python 2.7 and requires the installation of the following python libraries and their associated dependencies: `numpy`, `netCDF4`, `ConfigParser`, `argparse`, `sys`, `shutil`, `datetime`, `os`, `and mpi4py` (optional for running on multiple compute nodes).

## 

[EN4-ref]: http://www.metoffice.gov.uk/hadobs/en4/download-en4-0-2-g10.html
