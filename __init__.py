"""
A package for generating synthetic vertical profiles of ocean 
properties using output from an ocean general circulation model.

"""

import sys

from main import main

       
if __name__ == '__main__':
    
    try:
        main()
    except KeyboardInterrupt as err:
        print err
        sys.exit()
