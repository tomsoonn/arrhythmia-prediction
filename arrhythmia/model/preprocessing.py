import numpy as np
from scipy import fftpack
from scipy.signal import decimate

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
        self.series = TimeSeries([])

    def extend(self, series):
        """
        Extend TimeSeries used to find beats.

        :param series: TimeSeries to extend.
        :return: length of current time series
        """
        self.series.append(series)

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

    def __init__(self, interval, padding):
        """

        :param interval: Length of produced intervals.
        :param padding: Distance between starts of produced intervals.
        """
        super().__init__()
        self.interval = interval
        self.padding = padding
        self.series = TimeSeries([])

    def extend(self, series):
        self.series.append(series)

    def find_trim(self):
        result = []
        if len(self.series) >= self.interval:
            found_series = self.series[len(self.series) - self.interval:]
            result.append(found_series)
        self.series = TimeSeries([])
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
        return [TimeSeries(normalized)]


class NoiseRemover(PipeObject):
    """
    Removes noise from signal by applying Fast Fourier Transformation,
    removing low frequencies and restore signal with inverse FFT
    """

    def __init__(self, frequency, lower_bound):
        """

        :param frequency: frequency below which frequencies will bye removed
        """
        super().__init__()
        self.frequency = frequency
        self.lower_bound = lower_bound

    def remove_noise(self, values):
        sig = values
        sig_fft = fftpack.rfft(sig)
        sample_freq = fftpack.fftfreq(sig.size, d=(1 / self.frequency))

        high_freq_fft = sig_fft.copy()
        high_freq_fft[np.abs(sample_freq) < self.lower_bound] = 0
        filtered_sig = fftpack.irfft(high_freq_fft).real
        return filtered_sig

    def compute(self, value):
        points = value.points
        filtered = self.remove_noise(points)
        return [TimeSeries(filtered)]


def downsample(values, ratio):
    return decimate(values, ratio)


class Downsampler(PipeObject):
    def __init__(self, original_frequency, target_frequency):
        super().__init__()
        self.original_frequency = original_frequency
        self.target_frequency = target_frequency

    def compute(self, value):
        points = value.points
        # print('Before downsampling: ', points)
        ratio = self.original_frequency // self.target_frequency
        downsampled = downsample(points, ratio)
        # print('After downsampling: ', downsampled)
        return [TimeSeries(downsampled)]
