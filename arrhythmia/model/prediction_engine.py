import numpy as np

from arrhythmia.model.helpers import PipeObject, PipelineBuilder
from arrhythmia.model.preprocessing import IntervalSplitter, StandardNormalizer


class NNPipe(PipeObject):
    def __init__(self, network):
        super().__init__()
        self.network = network

    def compute(self, value):
        nn_input = value.points
        nn_input = np.expand_dims(nn_input, axis=1)
        return [self.network.predict(nn_input)]


class NNetwork:
    def __init__(self, name, filename, desc):
        self.name = name
        self.filename = filename
        self.desc = desc

    def load(self):
        # TODO Implement after adding any network
        pass


# List of available neural networks
networks = []

# List of available models
models = []


def create_layer(layer):
    layer_type = layer['type']

    if layer_type == 'splitter':
        return IntervalSplitter(**layer['desc'])

    if layer_type == 'normalize':
        return StandardNormalizer()

    # FIXME Throw exception if layer type is not recognized
    return None


def create_model(model_description):
    builder = PipelineBuilder()
    for layer in model_description:
        builder.append_one(create_layer(layer))

    return builder.build()
