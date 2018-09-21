class BeatType:
    """
    Represents beat type in EKG.
    """

    def __init__(self, symbol, name):
        """

        :param symbol: short symbol to identify beat type
        :param name: full name of this beat type
        """
        self.symbol = symbol
        self.name = name


beat_types = [BeatType('N', 'Normal beat'), BeatType('SVEB', 'Supraventricular ectopic beat'),
              BeatType('VEB', 'Ventricular ectopic beat'), BeatType('F','Fusion'),
              BeatType('Q', 'Unknown beat')]


class PipeObject:
    """
    Abstract class representing computation layer.
    More generally it can be viewed as pipe that gets values pushed to it and
    after performing some transformation on it it pushes to next pipe in line.
    Additionally this class has been extended to allow multiple PipeObject's as next in line.

    # TODO Add abstract class support to prevent this from being instantiated
    """
    def __init__(self):
        self.next = []

    def set_next(self, next_pipe):
        """
        Set next PipeObject['s] in line to push computation results to.

        :param next_pipe: PipeObject or list of them that are next in "pipeline"
        :return:
        """
        if type(next_pipe) is list:
            self.next = next_pipe
        else:
            self.next = [next_pipe]

    def compute(self, value):
        """
        Abstract method representing calculations from value -> [result].
        Keep in mind return of this value should be list, if you want single result return list with one element.
        This allow for more flexibility in each implementation and allows result to be
        of list type itself (eg. int -> [[int]]).

        Override this method to perform your own computations.

        :param value: input of this PipeObject
        :return: list of computation results
        """
        return []

    def push_value(self, value):
        """
        Push values as next to perform computation on and send results further.

        :param value: object to perform calculations on
        """
        results = self.compute(value)
        for result in results:
            for next in self.next:
                next.push_value(result)


class FunctionPipe(PipeObject):
    """
    General function PipeObject, performs computation by calling passed function.
    """
    def __init__(self, func):
        """
        :param func: function of type value -> result that will be used to perform computation
        """
        super().__init__()
        self.func = func

    def compute(self, value):
        return [self.func(value)]


class Pipeline(PipeObject):
    def __init__(self, first=None):
        super().__init__()
        self.head = first
        if first: self.set_next(first)

    def compute(self, value):
        return [value]

    def append_one(self, pipe):
        if not self.next:
            self.set_next(pipe)
            self.head = pipe
        else:
            self.head.set_next(pipe)
            self.head = pipe
        return self

    def split(self, pipes):
        if not self.next:
            self.set_next(pipes)
        pipelines = [Pipeline(first=pipe) for pipe in pipes]
        self.head.set_next(pipelines)
        return pipelines
