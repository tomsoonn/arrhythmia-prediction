import numpy as np

import os

import keras.backend as K

from keras.models import load_model

from arrhythmia.model.helpers import Layer, SequenceBuilder
from arrhythmia.model.preprocessing import IntervalSplitter, StandardNormalizer, Downsampler, NoiseRemover


class NNPredictor(Layer):
    def __init__(self, network):
        super().__init__()
        self.network = network

    def compute(self, value):
        # We expand first axis, because network expects input of size
        # batch_num x input_size
        # In our case "value" has "input_size" elements and our "batch_num" will always be 1.
        nn_input = np.expand_dims(value, axis=0)
        return [self.network.predict(nn_input)[0]]


def precision(y_true, y_pred):
    '''Calculates the precision, a metric for multi-label classification of
    how many selected items are relevant.
    '''
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision


def recall(y_true, y_pred):
    '''Calculates the recall, a metric for multi-label classification of
    how many relevant items are selected.
    '''
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall


def fbeta_score(y_true, y_pred, beta=1):
    '''Calculates the F score, the weighted harmonic mean of precision and recall.
    This is useful for multi-label classification, where input samples can be
    classified as sets of labels. By only using accuracy (precision) a model
    would achieve a perfect score by simply assigning every class to every
    input. In order to avoid this, a metric should penalize incorrect class
    assignments as well (recall). The F-beta score (ranged from 0.0 to 1.0)
    computes this, as a weighted mean of the proportion of correct class
    assignments vs. the proportion of incorrect class assignments.
    With beta = 1, this is equivalent to a F-measure. With beta < 1, assigning
    correct classes becomes more important, and with beta > 1 the metric is
    instead weighted towards penalizing incorrect class assignments.
    '''
    if beta < 0:
        raise ValueError('The lowest choosable beta is zero (only precision).')

    # If there are no true positives, fix the F score at 0 like sklearn.
    if K.sum(K.round(K.clip(y_true, 0, 1))) == 0:
        return 0

    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    bb = beta ** 2
    fbeta_score = (1 + bb) * (p * r) / (bb * p + r + K.epsilon())
    return fbeta_score


def fmeasure(y_true, y_pred):
    '''Calculates the f-measure, the harmonic mean of precision and recall.
    '''
    return fbeta_score(y_true, y_pred, beta=1)


class NNetwork:
    def __init__(self, name, filename, desc):
        self.name = name
        self.filename = filename
        self.desc = desc

    def load(self):
        path = os.path.join(os.path.dirname(__file__), 'nn_files', self.filename)
        k_model = load_model(path, custom_objects={'precision': precision, 'recall': recall, 'fmeasure': fmeasure})
        return NNPredictor(k_model)


# List of available neural networks
networks = [NNetwork('', 'mlp_conv_1_window5_2.hdf5', '')]


class PredictionEngine:
    def __init__(self, name, layers):
        self.name = name
        self.layers = layers

    def build(self):
        builder = SequenceBuilder()
        for l in self.layers:
            builder.append_one(l)
        return builder.build()


# List of available engines
engines = [
    PredictionEngine('convolutional', [
        IntervalSplitter(360*60*5),
        Downsampler(360, 60),
        NoiseRemover(60, 0.5),
        StandardNormalizer(),
        networks[0].load()])
]


def create_prediction_engine(engine):
    return engine.build()
