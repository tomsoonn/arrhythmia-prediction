from ..model.helpers import PipeObject, Pipeline, FunctionPipe, PipelineBuilder


class MulPipe(PipeObject):
    """
    Pipe that performs multiplication of input value by constant passed to constructor.
    """
    def __init__(self, mul):
        super().__init__()
        self.mul = mul

    def compute(self, value):
        return [self.mul * value]


class AddPipe(PipeObject):
    """
    Pipe that performs addition of input value and constant passed to constructor.
    """
    def __init__(self, add):
        super().__init__()
        self.add = add

    def compute(self, value):
        return [self.add + value]


def test_simple_pipes():
    """
    Test simple, manually constructed pipeline, that performs computation:
    (x) -> * 2 -> + 3 -> * 4 -> result
    """
    # Given:
    mul2 = MulPipe(2)
    add3 = AddPipe(3)
    mul4 = MulPipe(4)
    result = -1

    def set_result(v):
        nonlocal result
        result = v

    endp = FunctionPipe(set_result)

    mul2.set_next(add3)
    add3.set_next(mul4)
    mul4.set_next(endp)

    # When:
    mul2(12)

    # Then
    assert(result == (12 * 2 + 3) * 4)


def test_branching_pipes():
    """
    Test manually constructed pipeline, that performs branching computation:
    (x) -> * 2 -> * 4 -> result1
               -> + 3 -> result2
    """
    # Given:
    mul2 = MulPipe(2)
    add3 = AddPipe(3)
    mul4 = MulPipe(4)
    result1 = -1
    result2 = -1

    def set_result1(v):
        nonlocal result1
        result1 = v

    def set_result2(v):
        nonlocal result2
        result2 = v

    endp1 = FunctionPipe(set_result1)
    endp2 = FunctionPipe(set_result2)

    mul2.set_next([mul4, add3])
    mul4.set_next(endp1)
    add3.set_next(endp2)

    # When
    mul2(12)

    # Then
    assert(result1 ==  12 * 2 * 4)
    assert(result2 == 12 * 2 + 3)


def test_straight_pipeline():
    """
    Test straight pipeline constructed using PipelineBuilder class, that performs computation:
    (x) -> * 2 -> + 3 -> * 4 -> result1
    """
    # Given
    result1 = -1

    def set_result1(v):
        nonlocal result1
        result1 = v

    builder = PipelineBuilder()
    builder.append_one(MulPipe(2))
    builder.append_one(AddPipe(3))
    builder.append_one(MulPipe(4))
    builder.append_one(FunctionPipe(set_result1))
    pipeline = builder.build()

    # When
    pipeline(12)

    # Then
    assert (result1 == (12 * 2 + 3) * 4)


def disabled_test_branching_pipeline():
    """
    !!! Test disabled due to current lack of support for branching in builder.

    Test branching pipeline constructed using PipelineBuilder class, that performs branching computation:
    (x) -> * 2 -> + 3 -> * 4 -> result1
                      -> + 9 -> result2
    """
    # Given
    result1 = -1
    result2 = -1

    def set_result1(v):
        nonlocal result1
        result1 = v

    def set_result2(v):
        nonlocal result2
        result2 = v

    builder = PipelineBuilder()
    builder.append_one(MulPipe(2))
    builder.append_one(AddPipe(3))
    pipelines = builder.split([MulPipe(4), AddPipe(9)])
    pipelines[0].append_one(FunctionPipe(set_result1))
    pipelines[1].append_one(FunctionPipe(set_result2))
    pipeline = builder.build()

    # When
    pipeline(12)

    # Then
    assert(result1 == (12 * 2 + 3) * 4)
    assert(result2 == 12 * 2 + 3 + 9)
