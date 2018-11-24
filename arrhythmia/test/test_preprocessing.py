import numpy as np

from arrhythmia.model.helpers import FunctionPipe
from arrhythmia.model.preprocessing import IntervalSplitter, StandardNormalizer
from arrhythmia.model.time_series import TimeSeries

# Precision of floating point comparisons
epsilon = 1e-6


def test_interval():
    # Given:
    # Select two second samples each starting one second after previous
    frequency = 60
    interval = 2 * 60
    padding = 60
    total = 4 * 60 + 1

    splitter = IntervalSplitter(frequency, interval, padding)
    points = list(range(total))
    # Push values in two series
    series1 = TimeSeries(points[:10], frequency)
    series2 = TimeSeries(points[10:], frequency)

    # Use function pipe to report results
    results = []

    def set_results(v):
        nonlocal results
        results.append(v.points)

    endp = FunctionPipe(set_results)
    splitter.set_next(endp)

    # Calculate expected values manually
    expected = []
    for start in range(0, total - interval + 1, padding):
        expected.append(points[start:start+interval])

    # When:
    splitter.push_value(series1)
    splitter.push_value(series2)

    # Then:
    assert results == expected


def test_standard_normalizer():
    # Given:
    # Create random sequence of uniform values from interval [0, 1)
    length = 100
    random_uniform = np.random.rand(length)
    # Wrap it into TimeSeries
    ts = TimeSeries(random_uniform, 1)
    # Create the normalizer to test
    normalizer = StandardNormalizer()
    # Helper pipe to save the result
    result = None

    def set_result(v):
        nonlocal result
        result = v

    endp = FunctionPipe(set_result)

    # Connect normalizer to ending pipe
    normalizer.set_next(endp)
    # When:
    normalizer.push_value(ts)
    # Then:
    out_points = result.points
    # Length of output sequence should be the same as input sequence
    assert len(out_points) == length
    # Mean should be zero
    assert abs(out_points.mean()) < epsilon
    # Standard deviation should be zero
    assert abs(out_points.std() - 1.0) < epsilon
