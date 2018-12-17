import numpy as np


class TimeSeries:
    """
    Discrete list of values occurring at certain frequency.
    """

    def __init__(self, points, frequency):
        self.points = np.array(points) if isinstance(points, list) else points
        self.frequency = frequency

    def append(self, other):
        """
        Appends contents of other TimeSeries. If other has different frequency than this TimeSeries,
        it uses interpolation to convert it.

        :return: this TimeSeries
        """
        self.points = np.concatenate([self.points, other.points])
        return self

    def __len__(self):
        return len(self.points)

    def __getitem__(self, i):
        return TimeSeries(self.points[i], self.frequency)
