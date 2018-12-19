import numpy as np
from scipy import fftpack

from arrhythmia.model.helpers import FunctionLayer
from arrhythmia.model.preprocessing import IntervalSplitter, NoiseRemover, StandardNormalizer

# Precision of floating point comparisons
epsilon = 1e-6


def disabled_test_interval():
    # Given:
    # Select two second samples each starting one second after previous
    frequency = 60
    interval = 2 * 60
    total = 4 * 60 + 1

    splitter = IntervalSplitter(interval)
    points = list(range(total))
    # Push values in two series
    series1 = np.array(points[:10])
    series2 = np.array(points[10:])

    # Use function pipe to report results
    results = []

    def set_results(v):
        nonlocal results
        results.append(v)

    endp = FunctionLayer(set_results)
    splitter.set_next(endp)

    # Calculate expected values manually
    expected = []
    for start in range(0, total - interval + 1):
        expected.append(points[start:start + interval])

    # When:
    splitter.push_value(series1)
    splitter.push_value(series2)

    # Then:
    assert len(results) == len(expected)
    for result, expect in zip(results, expected):
        assert np.all(result == expect)


def test_standard_normalizer():
    # Given:
    # Create random sequence of uniform values from interval [0, 1)
    length = 100
    random_uniform = np.random.rand(length)
    # Create the normalizer to test
    normalizer = StandardNormalizer()
    # Helper pipe to save the result
    result = None

    def set_result(v):
        nonlocal result
        result = v

    endp = FunctionLayer(set_result)
    # Connect normalizer to ending pipe
    normalizer.set_next(endp)

    # When:
    normalizer.push_value(random_uniform)

    # Then:
    # Length of output sequence should be the same as input sequence
    assert len(result) == length
    # Mean should be zero
    assert abs(result.mean()) < epsilon
    # Standard deviation should be zero
    assert abs(result.std() - 1.0) < epsilon


def test_noise_remover():
    # Given:
    # Create signal with low frequencies, here sinus noised with high frequency
    time_step = 0.02
    period = 5.
    time_vec = np.arange(0, 20, time_step)
    noisy_sinus = (np.sin(2 * np.pi / period * time_vec) + 0.5 * np.random.randn(time_vec.size))

    def get_peak_freq(values):
        sig_fft = fftpack.fft(values)
        power = np.abs(sig_fft)
        sample_freq = fftpack.fftfreq(values.size, d=1)
        pos_mask = np.where(sample_freq > 0)
        freqs = sample_freq[pos_mask]
        min_freq = freqs[power[pos_mask].argmax()]
        return min_freq

    peak_freq_original = get_peak_freq(noisy_sinus)
    # Create the remover to test
    frequency = peak_freq_original + 0.01
    noise_remover = NoiseRemover(1, frequency)
    # Helper pipe to save the result
    result = None

    def set_result(v):
        nonlocal result
        result = v

    endp = FunctionLayer(set_result)
    # Connect noise remover to ending pipe
    noise_remover.set_next(endp)
    # When:
    noise_remover.push_value(noisy_sinus)

    # Then:
    # Result should be set
    assert result is not None
    peak_freq_ts = get_peak_freq(result)
    # Min frequency of new signal should be higher or equal to noise remover parameter
    assert peak_freq_ts >= frequency
    # Length of output sequence should be the same as input sequence
    assert len(result) == len(noisy_sinus)
