import os
import numpy as np

from .. import data


def list_data():
    """
    lists all built-in data files
    """
    path = data.__path__[0]

    return os.listdir(path)


def get_filepath(filename):
    """
    get selected data file
    """
    filepath = os.path.join(data.__path__[0], filename)

    return filepath


def get_data(filename, **kwargs):
    """
    get selected data file
    """
    filepath = os.path.join(data.__path__[0], filename)

    return np.genfromtxt(filepath, **kwargs)
