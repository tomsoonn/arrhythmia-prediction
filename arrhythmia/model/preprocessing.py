import numpy as np
from scipy import fftpack
from scipy.signal import decimate

from .helpers import Layer


class IntervalSplitter(Layer):
    """
    Cuts general TimeSeries into intervals with constant duration.
    """

    def __init__(self, interval):
        """

        :param interval: Length of produced intervals.
        """
        super().__init__()
        self.interval = interval

    def compute(self, value):
        result = []
        if len(value) >= self.interval:
            result.append(value[len(value) - self.interval:])
        return result


def standard_normalization(values):
    """
    Normalize values to achieve mean = 0 and standard deviation = 1
    :param values: Numpy array of values to normalize
    :return: Numpy array of normalized values
    """
    mean = values.mean()
    std = values.std()
    return (values - mean) / std


class StandardNormalizer(Layer):
    """
    Normalizer performing standard normalization, that is:
    x' = (x - mean(x)) / std(x)
    Output values should have mean close to 0 and standard deviation close to 1.
    Does not change the length of input sequences.
    """
    def compute(self, value):
        return [standard_normalization(value)]


class NoiseRemover(Layer):
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
        filtered = self.remove_noise(value)
        return [filtered]


def downsample(values, ratio):
    return decimate(values, ratio)


class Downsampler(Layer):
    def __init__(self, original_frequency, target_frequency):
        super().__init__()
        self.original_frequency = original_frequency
        self.target_frequency = target_frequency

    def compute(self, value):
        # print('Before downsampling: ', points)
        ratio = self.original_frequency // self.target_frequency
        downsampled = downsample(value, ratio)
        # print('After downsampling: ', downsampled)
        return [downsampled]
