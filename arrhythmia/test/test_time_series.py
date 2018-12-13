import math

import pytest

from ..model.time_series import TimeSeries, linear_interpolation
import numpy as np


@pytest.fixture(params=[(60, 6)])
def sinus_ts(request):
    frequency, duration = request.param
    data = []
    points_n = frequency * duration
    for i in range(points_n):
        data.append(math.sin(i / frequency))

    return TimeSeries(data, frequency)


def test_linear_size(sinus_ts):
    """
    Test that linear interpolation doubling the frequency also doubles the number of data points.
    """
    # Given
    frequency_multiple = 2
    target_frequency = sinus_ts.frequency * frequency_multiple

    # When
    result = sinus_ts.convert(target_frequency, linear_interpolation)

    # Then
    assert(len(result) == target_frequency / sinus_ts.frequency * len(sinus_ts))


def test_linear_back(sinus_ts):
    """
    Test that linear interpolation is reversible.
    """
    # Given
    frequency_multiple = 2
    target_frequency = sinus_ts.frequency * frequency_multiple

    # When
    result = sinus_ts.convert(target_frequency, linear_interpolation)
    result = result.convert(sinus_ts.frequency, linear_interpolation)

    # Then
    assert(len(result) == len(sinus_ts))
    assert(np.all(result.points == sinus_ts.points))


def test_slicing():
    """
    Test slicing operator for TimeSeries.
    """
    ts = TimeSeries([1, 2, 3], 1)
    ts2 = ts[:2]
    assert np.all(ts2.points == [1, 2])
