import wfdb
import os

def get_mitdb():
    record_names = wfdb.get_record_list('mitdb')
    wfdb.dl_database('mitdb', os.getcwd() + '/download/mitdb')
    records = [wfdb.rdrecord('download/mitdb/' + record_name) for record_name in record_names]
    record_signals = [np.sum(record.p_signal, 1) for record in records]
    annotations = [wfdb.rdann('download/mitdb/' + record_name, 'atr') for record_name in record_names]
    annotations_data = [(annotation.sample, annotation.symbol) for annotation in annotations]