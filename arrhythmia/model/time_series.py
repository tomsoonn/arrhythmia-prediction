

class TimeSeries:
    """
    Discrete list of values occurring at certain frequency.
    """
    def __init__(self, points, frequency):
        self.points = points
        self.frequency = frequency

    def convert(self, target_frequency, interpolation):
        """
        Converts TimeSeries into one with different frequency, using specified interpolation method.

        :param target_frequency: frequency of new TimeSeries
        :param interpolation:
        :return: new TimeSeries representing the same values at different frequency
        """
        # TODO Implement
        pass

    def append(self, other, interpolation):
        """
        Appends contents of other TimeSeries. If other has different frequency than this TimeSeries,
        it uses interpolation to convert it.

        :return: this TimeSeries
        """
        other_ = other
        if other.frequency != self.frequency:
            other_ = other.convert(self.frequency, interpolation)

        # TODO Implement
        return self

    def __len__(self):
        return len(self.points)
