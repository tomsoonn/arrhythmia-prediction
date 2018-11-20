from .helpers import PipeObject
from .time_series import TimeSeries


class BeatFinder(PipeObject):
    """
    Cuts general TimeSeries into chunks representing beats.
    """

    def __init__(self, frequency, beat_len):
        """

        :param frequency: frequency of found beats
        :param beat_len: length of produced TimeSeries representing beats
        """
        super().__init__()
        self.series = TimeSeries([], frequency)

    def extend(self, series):
        """
        Extend TimeSeries used to find beats.

        :param series: TimeSeries to extend.
        :return: length of current time series
        """
        # TODO Resolve interpolation issues
        self.series.append(series, None)

    def find(self):
        """
        Finds beats in TimeSeries created by calling extend.

        :return: list of TimeSeries representing found beats
        """
        # TODO Implement
        return []

    def find_trim(self):
        """
        Finds beats in TimeSeries created by calling extend and trims it to remove them from internal TimeSeries.

        :return: list of TimeSeries representing found beats
        """
        # TODO Implement
        return []

    def compute(self, value):
        self.extend(value)
        return self.find_trim()


class IntervalSplitter(PipeObject):
    """
    Cuts general TimeSeries into intervals with constant duration.
    """

    def __init__(self, frequency, interval, padding):
        """

        :param frequency: Frequency of produced intervals.
        :param interval: Length of produced intervals.
        :param padding: Distance between starts of produced intervals.
        """
        super().__init__()
        self.interval = interval
        self.padding = padding
        self.series = TimeSeries([], frequency)

    def extend(self, series):
        self.series.append(series, None)

    def find_trim(self):
        result = []
        # TODO Prettify this
        print(self.series.points)
        while len(self.series) >= self.interval:
            found_series = self.series[:self.interval]
            self.series = self.series[self.padding:]
            result.append(found_series)
        return result

    def compute(self, value):
        self.extend(value)
        return self.find_trim()
