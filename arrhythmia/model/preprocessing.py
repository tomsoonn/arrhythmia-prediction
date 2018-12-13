import numpy as np
from scipy import fftpack

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
        while len(self.series) >= self.interval:
            found_series = self.series[:self.interval]
            self.series = self.series[self.padding:]
            result.append(found_series)
        return result

    def compute(self, value):
        self.extend(value)
        return self.find_trim()


class StandardNormalizer(PipeObject):
    """
    Normalizer performing standard normalization, that is:
    x' = (x - mean(x)) / std(x)
    Output values should have mean close to 0 and standard deviation close to 1.
    Does not change the length of input sequences.
    """
    @staticmethod
    def normalize(values):
        """
        Normalize values to achieve mean = 0 and standard deviation = 1
        :param values: Numpy array of values to normalize
        :return: Numpy array of normalized values
        """
        mean = values.mean()
        std = values.std()
        return (values - mean) / std

    def compute(self, value):
        points = value.points
        normalized = self.normalize(points)
        return [TimeSeries(normalized, value.frequency)]


class NoiseRemover(PipeObject):
    """
    Removes noise from signal by applying Fast Fourier Transformation,
    removing low frequencies and restore signal with inverse FFT
    """

    def __init__(self, frequency):
        """

        :param frequency: frequency below which frequencies will bye removed
        """
        super().__init__()
        self.frequency = frequency

    def remove_noise(self, values):
        sig = values
        sig_fft = fftpack.fft(sig)
        sample_freq = fftpack.fftfreq(sig.size, d=1)

        high_freq_fft = sig_fft.copy()
        high_freq_fft[np.abs(sample_freq) < self.frequency] = 0
        filtered_sig = fftpack.ifft(high_freq_fft)
        return filtered_sig

    def compute(self, value):
        points = value.points
        filtered = self.remove_noise(points)
        return [TimeSeries(filtered, value.frequency)]
