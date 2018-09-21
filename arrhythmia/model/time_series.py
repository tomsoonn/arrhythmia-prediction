import math


def linear_interpolation(input_data, target_size):
    """
    Function performing linear interpolation.

    :param input_data: array of input values to interpolate
    :param target_size: size of target array
    :return: array of interpolated values
    """
    input_size = len(input_data)
    output_data = []
    ratio = input_size / target_size
    running_sum = 0.0
    for i in range(target_size):
        low_ii = math.floor(running_sum)
        high_ii = min(math.ceil(running_sum), len(input_data) - 1)

        high_c = running_sum - low_ii
        low_c = 1 - high_c
        result = input_data[low_ii] * low_c + input_data[high_ii] * high_c
        output_data.append(result)
        running_sum += ratio
    return output_data


class TimeSeries:
    """
    Discrete list of values occurring at certain frequency.
    """
    def __init__(self, points, frequency):
        self.points = points
        self.frequency = frequency

    def convert(self, target_frequency, interpolation):
        """
        Converts TimeSeries into one with different frequency, using specified interpolation method.

        :param target_frequency: frequency of new TimeSeries
        :param interpolation: callable performing operation: in_points, target_size -> out_points
                              , interpolating "in_points" into "out_points" of size "target_size"
        :return: new TimeSeries representing the same values at different frequency
        """
        target_size = len(self.points) * target_frequency / self.frequency
        target_size = math.ceil(target_size)
        new_data = interpolation(self.points, target_size)
        return TimeSeries(new_data, target_frequency)

    def append(self, other, interpolation):
        """
        Appends contents of other TimeSeries. If other has different frequency than this TimeSeries,
        it uses interpolation to convert it.

        :return: this TimeSeries
        """
        other_ = other
        if other.frequency != self.frequency:
            other_ = other.convert(self.frequency, interpolation)

        # TODO Implement
        return self

    def __len__(self):
        return len(self.points)

    def __getitem__(self, i):
        return self.points[i]
