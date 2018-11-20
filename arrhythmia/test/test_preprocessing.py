from arrhythmia.model.helpers import FunctionPipe
from arrhythmia.model.preprocessing import IntervalSplitter
from arrhythmia.model.time_series import TimeSeries


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
