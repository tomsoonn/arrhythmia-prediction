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

    def __eq__(self, other):
        if isinstance(other, BeatType):
            return other.symbol == self.symbol
        if isinstance(other, str):
            return other == self.symbol
        return False

    def __hash__(self) -> int:
        return hash(self.symbol)


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

    def __call__(self, value):
        """
        Helper function providing functional API for PipeObject's.
        Should work exactly the same as push_value(value).
        """
        self.push_value(value)


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
    def __init__(self, first, last):
        super().__init__()
        self.head = first
        self.last = last

    def set_next(self, pipe):
        self.last.set_next(pipe)

    def push_value(self, value):
        self.head.push_value(value)


class PipelineBuilder:
    def __init__(self, pipes=None):
        self.pipes = pipes if pipes is not None else []

    def append_one(self, pipe):
        self.pipes.append(pipe)

    def build(self):
        previous = self.pipes[0]
        for pipe in self.pipes[1:]:
            previous.set_next(pipe)
            previous = pipe
        first = self.pipes[0]
        last = self.pipes[-1]
        return Pipeline(first, last)
