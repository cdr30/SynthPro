# SynthPro v1.0
SynthPro is a python utility for generating synthetic versions of observed ocean temperature and salinity profiles using output from an ocean general circulation model. For each observed temperature and salinity profile, SynthPro extracts a model analog using a 'nearest-neighbour' algorithm. The default behaviour is for synthetic profiles to be vertically interpolated onto the same depth levels used by the observed profiles and masked accordingly. Alternatively, the user can specify that synthetic profiles are extracted over the full-depth of the model domain.

## Using SynthPro
#### Required python libraries
SynthPro was developed using Python 2.7 and requires the installation of the following python libraries and their associated dependencies: `numpy`, `netCDF4`, `ConfigParser`, `argparse`, `sys`, `shutil`, `os`, `unittest`, `and mpi4py` (optional for running on multiple compute nodes).

#### Cloning the git repository
To retrieve a copy of the SynthPro source code and create a working directory, run the following on the command line: 

```> git clone git@github.com:cdr30/SynthPro.git```

or 

```> git clone https://github.com/cdr30/SynthPro.git```


#### Running SynthPro
SynthPro is invoked from the command line using the `run_synthpro.py` script. Executing this script without any arguments will return an error message that demonstrates the correct usage:

```
> python2.7 run_synthpro.py 
usage: run_synthpro.py [-h] [-d DAY] month year namelist
run_synthpro.py: error: too few arguments
```

The `day`, `month` and `year` arguments are used only to create paths to the correct netcdf files containing observed profiles and model data. No checks are made at run time to ensure that the date and time information within each netcdf file matches the dates used in the file name. The `day` argument is optional, but `month` and `year` must be specified. The namelist argument is a path to an [INI][INI-ref] configuration file containing data paths and other options. An example namelist is available in the `./config` subdirectory and an annotated version is described the section below. Example data files are available within the `./data` subdirectory. 

To ensure that SynthPro is installed correctly, run the following command and check you receive a `Finished!` message on the command line. 

```
> python2.7 run_synthpro.py 01 2010 config/namelist.ini
```

#### Running Synthpro in parallel using openMPI
SynthPro can also be run in a python environment that supports the openMPI framework. In this mode of operation, the model data is divided across a number of different compute nodes allowing SynthPro to be applied to very high-resolution model data without running out of memory. To enable this functionality, the namelist must be edited such that `submit_parallel = True` with `nxcores` and `nycores` specified such that their product is equal to the total number of nodes (`NCORES`) requesteed by openMPI. SynthPro can then be run from the command line as follows:

```
mpirun -n NCORES python2.7 run_synthpro.py 01 2010 config/namelist.ini
```

#### Running tests
Automated testing is currently limited to the `tools` module that contains the fundamental functions for extracting and interpolating data. Unit tests are executed from within the main package directory using the following command:
```
> python2.7 -m unittest discover -b
```


#### Data formats
##### Observed profiles
Observational profiles must be provided in the netcdf format used by the [EN4 database][EN4-ref]. Note that date and time information within the input file is ignored and SynthPro will attempt to extract synthetic versions of all observed profiles. If you are only interested in a limited number of profiles, this file should be pre-processed prior to running SynthPro. 


##### Synthetic profiles
Synthetic profiles are returned in the same netcdf format as the observational data with an additional variable `distance_to_ob` describing the distance on a sphere between the observed latitude/longitude and the chosen model grid-point. Observed profiles that lie more than 2 degrees latitude/longitude from a valid model grid point are specified as missing data.

##### Model data
Model data must be provided in a netcdf format with the following variables and dimensions (variable names can be specied during configuration): `temperature(z, y, x)`, `salinity(z, y, x)`, `latitude(y, x)`, `longitude(y, x)`, `depth(z)`. Latitude and longitude are specifed as two-dimensional fields to support models with irregular horizontal grids (e.g. NEMO). 


### Configuring a `namelist.ini` file
This section provides an annotated examples of a SynthPro namelist congiguration file. 

##### `[obs_profiles]`
```
dir = ./data/                                             ### Directory containing observed profile data.
fpattern = EN.4.1.1.f.profiles.g10.${YYYY}${MM}${DD}.nc   ### File names must match this pattern. 
data_type = EN4                                           ### Profile type - only EN4 is supported. 
temp_var = POTM_CORRECTED                                 ### Netcdf variable name for temperature profiles.
sal_var = PSAL_CORRECTED                                  ### Netcdf variable name for salinity profiles.
depth_var = DEPH_CORRECTED                                ### Netcdf variable name for profile depths.
lat_var = LATITUDE                                        ### Netcdf variable name for profile latitudes.
lon_var = LONGITUDE                                       ### Netcdf variable name for profile longitudes.
```

##### `[synth_profiles]`
```
dir = ./data/                                                  ### Directory to save synthetic profile data.
fpattern = EN.4.1.1.f.profiles.synthetic.${YYYY}${MM}${DD}.nc  ### File pattern for synthetic profile data.
data_type = EN4                                                ### Profile type - only EN4 is supported.
temp_var = POTM_CORRECTED                                      ### Netcdf variable name for temperature profiles.
sal_var = PSAL_CORRECTED                                       ### Netcdf variable name for salinity profiles.
depth_var = DEPH_CORRECTED                                     ### Netcdf variable name for profile depths.
lat_var = LATITUDE                                             ### Netcdf variable name for profile latitudes.
lon_var = LONGITUDE                                            ### Netcdf variable name for profile longitudes.
```

##### `[model_temp]`
```
dir = ./data/                                                  ### Directory containing model data.
fpattern = ${YYYY}${MM}${DD}__orca025l75.mersea.grid_T.nc      ### File pattern for model data. 
maskf = ./data/tmask.nc                                        ### File containing 3D land mask for model data.
model_type = NEMO                                              ### Model type - NEMO should work with other models. 
data_var = votemper                                            ### Netcdf variable name for data .
depth_var = deptht                                             ### Netcdf variable name for depth.
lat_var = nav_lat                                              ### Netcdf variable name for latitude.
lon_var = nav_lon                                              ### Netcdf variable name for longitude.
mask_var = tmask                                               ### Netcdf variable name for data land mask.
mask_mdi = 0                                                   ### Missing data indicator value for land mask.
imin = 0                                                       ### Minimum i-index (to extract sub-region).
imax = 1441                                                    ### Maximum i-index (to extract sub-region).
jmin = 0                                                       ### Minimum j-index (to extract sub-region). 
jmax = 1020                                                    ### Maximum j-index (to extract sub-region). 
```
##### `[model_sal]`
```
dir = ./data/                                                  ### Directory containing model data.
fpattern = ${YYYY}${MM}${DD}__orca025l75.mersea.grid_T.nc      ### File pattern for model data. 
maskf = ./data/tmask.nc                                        ### File containing 3D land mask for model data.
model_type = NEMO                                              ### Model type - NEMO should work with other models. 
data_var = vosaline                                            ### Netcdf variable name for data .
depth_var = deptht                                             ### Netcdf variable name for depth.
lat_var = nav_lat                                              ### Netcdf variable name for latitude.
lon_var = nav_lon                                              ### Netcdf variable name for longitude.
mask_var = tmask                                               ### Netcdf variable name for data land mask.
mask_mdi = 0                                                   ### Missing data indicator value for land mask.
imin = 0                                                       ### Minimum i-index (to extract sub-region).
imax = 1441                                                    ### Maximum i-index (to extract sub-region).
jmin = 0                                                       ### Minimum j-index (to extract sub-region). 
jmax = 1020                                                    ### Maximum j-index (to extract sub-region). 
```

##### `[parallel]`
```
submit_parallel = False          # Boolean flag used to enable parallel jobs using openMPI
nxcores = 2                      # Number of compute nodes used to decompose model grid along x axis.
nycores = 2                      # Number of compute nodes used to decompose model grid along y axis.
```

##### `[options]`
```
use_daily_data  = False          # Boolean flag used to specify use of daily data.
extract_full_depth = False       # Boolean flag used to specify extraction of full-depth profiles.  
print_stdout = True              # Boolean flag used to enable/suppress messages to standard output.
```






[EN4-ref]: http://www.metoffice.gov.uk/hadobs/en4/download-en4-0-2-g10.html
[INI-ref]: https://en.wikipedia.org/wiki/INI_file
