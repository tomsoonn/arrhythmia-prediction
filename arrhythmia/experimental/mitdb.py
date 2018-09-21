"""
Helpers used to handle mitdb arrhythmia database.

Before doing anything related you should execute this file
to download the data base (or use download_mitdb() function).
"""

import os
import wfdb
from ..model.helpers import BeatType

# Little hacky - get the root directory of the project independent of cwd
arrhythmia_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
db_dir = 'download/mitdb/'

data_dir = os.path.join(arrhythmia_root, db_dir)


def download_mitdb():
    wfdb.dl_database('mitdb', data_dir)


ds1 = ['101', '106', '108', '109', '112', '114', '115', '116', '118', '119', '122',
       '124', '201', '203', '205', '207', '208', '209', '215', '220', '223', '230']

ds2 = ['100', '103', '105', '111', '113', '117', '121', '123', '200', '202', '210',
       '212', '213', '213', '219', '221', '222', '228', '231', '232', '233', '234']


def get_record(name):
    record = wfdb.rdrecord(data_dir + name)
    annotation = wfdb.rdann(data_dir + name, 'atr')
    annotation = zip(annotation.sample, annotation.symbol)
    annotation = [(sample, mit_to_aami(symbol)) for sample, symbol in annotation if mit_to_aami(symbol)]
    samples, symbols = zip(*annotation)
    return record, samples, symbols


def get_records(data_set):
    records = [get_record(rn) for rn in data_set]
    return records


mapping = {BeatType('N', 'Normal beat'): {'N', 'L', 'R'},
           BeatType('SVEB', 'Supraventricular ectopic beat'): {'e', 'j', 'A', 'a', 'J', 'S'},
           BeatType('VEB', 'Ventricular ectopic beat'): {'V', 'E'},
           BeatType('F','Fusion'): {'F'},
           BeatType('Q', 'Unknown beat'): {'/', 'f', 'Q'}}


def mit_to_aami(symbol):
    for key, value in mapping.items():
        if symbol in value:
            return key
    return None


if __name__ == '__main__':
    download_mitdb()


