from distutils.core import setup

setup(
    name='SynthPro',
    version='v1.0',
    author='Chris Roberts',
    author_email='chris.roberts@metoffice.gov.uk',
    packages=['synthpro',],
    license='LICENSE.txt',
    url="https://github.com/cdr30/SynthPro",
    data_files = [("data", ["data/20100101__orca025l75.mersea.grid_T.nc",
                            "data/201001__orca025l75.mersea.grid_T.nc",
                            "data/EN.4.1.1.f.profiles.g10.201001.nc",
                            "data/EN.4.1.1.f.profiles.g10.20100101.nc",
                            "data/EN.4.1.1.f.profiles.synthetic.201001.nc"]),
                  ("config", ["config/namelist.ini"])],
    long_description=open('README.txt').read(),
    description='SynthPro is a python utility for generating synthetic versions of observed ocean temperature and salinity profiles using output from an ocean general circulation model',
        install_requires=[
        "numpy",
        "netCDF4",
        "ConfigParser",
        "argparse",
        "sys",
        "shutil",
        "datetime",
        "os",
        "unittest"],
    )
