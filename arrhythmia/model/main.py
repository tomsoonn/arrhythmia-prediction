import numpy as np
import matplotlib.pyplot as plt

from keras.layers import Input, Dense
from keras.models import Model

from arrhythmia.experimental.mitdb import get_records, full_ds
from arrhythmia.model.time_series import TimeSeries


def build_model():
    inputs = Input(shape=(300,))
    x = Dense(5, activation='relu')(inputs)
    x = Dense(3, activation='relu')(x)
    outputs = Dense(1, activation='relu')(x)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='sgd', loss='mean_squared_error', metrics=['accuracy'])
    return model


def get_data_from_records(records, frequency):
    record_signals = [record[0].p_signal[:, 0] for record in records]
    ann_samples = [record[1] for record in records]
    ann_beat_types = [record[2] for record in records]

    time_series = []
    for record_signal in record_signals:
        time_serie = TimeSeries(record_signal, frequency)
        time_series.append(time_serie)

    return time_series, ann_samples, ann_beat_types


def main():
    records = get_records(full_ds)
    time_series, ann_samples, ann_beat_types = get_data_from_records(records, 360)  # mitdb data frequency is 360

    samples = []
    ex_output = []
    for record_index, record in enumerate(records):
        sig_len = len(time_series)
        ad1 = ann_samples[record_index]
        ad2_tmp = ann_beat_types[record_index]

        ad1 = np.asarray(ad1)
        ad2_tmp = np.asarray(ad2_tmp)

        ad2 = np.zeros_like(ad1, dtype='float32')
        for j in range(ad2.shape[0]):
            ad2[j] = 0. if ad2_tmp[j].symbol == 'N' else 1.

        # idk why not working, replaced by cutting first and last element
        # indices = np.logical_and(150 <= ad1, ad1 < sig_len - 149)
        # ad2 = ad2[indices]
        # ad1 = ad1[indices]
        ad2 = ad2[1:-1]
        ad1 = ad1[1:-1]

        for j in range(ad1.shape[0]):
            start = ad1[j] - 150
            end = ad1[j] + 150
            samples.append(time_series[record_index].points[start:end])
            ex_output.append(ad2[j])

    samples = np.asarray(samples)
    ex_output = np.asarray(ex_output)
    ex_output = np.expand_dims(ex_output, axis=1)

    model = build_model()
    model.fit(samples, ex_output, batch_size=100, epochs=2)

    plt.plot(samples[0])
    plt.plot(samples[1])
    plt.show()


if __name__ == '__main__':
    main()
