import math

import pytest

from arrhythmia.model.preprocessing import downsample
from ..model.time_series import TimeSeries
import numpy as np


@pytest.fixture(params=[(60, 6)])
def sinus_ts(request):
    frequency, duration = request.param
    data = []
    points_n = frequency * duration
    for i in range(points_n):
        data.append(math.sin(i / frequency))

    return TimeSeries(data)


def test_linear_size(sinus_ts):
    """
    Test that linear interpolation halving the frequency also doubles the number of data points.
    """
    # Given
    frequency_divide = 2

    # When
    result = downsample(sinus_ts.points, frequency_divide)

    # Then
    assert(len(result) == len(sinus_ts) // frequency_divide)


def test_slicing():
    """
    Test slicing operator for TimeSeries.
    """
    ts = TimeSeries([1, 2, 3])
    ts2 = ts[:2]
    assert np.all(ts2.points == [1, 2])
