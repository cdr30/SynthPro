"""
Rutines to parse command line arguments.

"""

import argparse


def get_args():
    """
    Get arguments from command line.
    
    """
    parser = argparse.ArgumentParser(
        description='Generate synthetic profiles.')
    parser.add_argument(
        'month', type=int, help='Month used in file names.')
    parser.add_argument(
        'year', type=int, help='Year used in file names.')
    parser.add_argument(
        'namelist', type=str, help='Path to namelist.ini')
    parser.add_argument(
        '-d', '--day', type=int, help='Day used in file names.', default=None)
    args = parser.parse_args()

    return args
