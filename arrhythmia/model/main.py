import wfdb
import os

import numpy as np
import matplotlib.pyplot as plt

from keras.layers import Input, Dense
from keras.models import Model


def build_model():
    inputs = Input(shape=(300,))
    x = Dense(5, activation='relu')(inputs)
    x = Dense(3, activation='relu')(x)
    outputs = Dense(1, activation='relu')(x)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='sgd', loss='mean_squared_error', metrics=['accuracy'])
    return model


def main():
    record_names = wfdb.get_record_list('mitdb')
    wfdb.dl_database('mitdb', os.getcwd() + '/download/mitdb')
    records = [wfdb.rdrecord('download/mitdb/' + record_name) for record_name in record_names]
    record_signals = [np.sum(record.p_signal, 1) for record in records]
    annotations = [wfdb.rdann('download/mitdb/' + record_name, 'atr') for record_name in record_names]
    annotations_data = [(annotation.sample, annotation.symbol) for annotation in annotations]
    samples = []
    ex_output = []
    for i, record in enumerate(records):
        sig_len = record.sig_len
        ad1, ad2_tmp = annotations_data[i]
        ad2 = np.zeros_like(ad1, dtype='float32')
        for j in range(ad2.shape[0]):
            ad2[j] = 0. if ad2_tmp[j] == 'N' else 1.
        indices = np.logical_and(150 <= ad1, ad1 < sig_len - 149)
        ad2 = ad2[indices]
        ad1 = ad1[indices]
        for j in range(ad1.shape[0]):
            start = ad1[j] - 150
            end = ad1[j] + 150
            samples.append(record_signals[i][start:end])
            ex_output.append(ad2[j])
    samples = np.asarray(samples)
    ex_output = np.asarray(ex_output)
    ex_output = np.expand_dims(ex_output, axis=1)

    model = build_model()
    model.fit(samples, ex_output, batch_size=100, epochs=2)
    plt.plot(samples[0])
    plt.plot(samples[1])







if __name__ == '__main__':
    main()