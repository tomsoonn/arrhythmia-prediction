from .helpers import PipeObject


class Classifier(PipeObject):
    """
    Beat classifier, converts TimeSeries to predicted BeatType.
    """

    def __init__(self):
        super().__init__()

    def classify(self, beat_series):
        """

        :param beat_series: TimeSeries with beat to clasify
        :return: BeatType describing classified beat
        """
        # TODO Implement
        pass

    def compute(self, value):
        return [self.classify(value)]
