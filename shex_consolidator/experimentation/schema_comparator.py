from shex_consolidator.utils.shape_parser import parse_file
from shex_consolidator.model import Schema, Shape

######################## CONSTANTS -- Key definitions for JSON result

_ABS = "absolute_value"
_RATIO = "ratio"

_SHARED_SHAPES = "SHARED_SHAPES"
_SHAPES_ONLY_IN_1 = "SHAPES_ONLY_IN_1"
_SHAPES_ONLY_IN_2 = "SHAPES_ONLY_IN_2"

_TOTAL_NUMBER_OF_CONSTRAINTS = "N_CONSTRAINTS"


_SHAPES_COMPLETELY_EQUAL = "SHAPES_COMPLETELY_EQUAL"
_SHAPES_EQUAL_CONSTRAINT = "SHAPES_EQUAL_CONSTRAINT"
_SHAPES_EQUAL_P_O_PAIRS = "SHAPES_EQUAL_P_O_PAIRS"
_SHAPES_EQUAL_PROPERTY = "SHAPES_EQUAL_PROPERTY"
_SHAPES_DIFFERENT_CONSTRAINTS = "SHAPES_DIFFERENT_CONSTRAINTS"



_CONSTRAINTS_COMPLETELY_EQUAL = "CONSTRAINTS_COMPLETELY_EQUAL"
_CONSTRAINTS_VALIDATION_EQUAL = "CONSTRAINTS_VALIDATION_EQUAL"
_CONSTRAINTS_P_O_EQUAL = "CONSTRAINTS_P_O_EQUAL"
_CONSTRAINTS_PROPERTY_EQUAL = "CONSTRAINTS_PROPERTY_EQUAL"
_CONSTRAINTS_DIFFERENT = "CONSTRAINTS_DIFFERENT"



_CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL = "CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL"
_CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL = "CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL"
_CONSTRAINTS_PER_SHAPE_P_O_EQUAL = "CONSTRAINTS_PER_SHAPE_P_O_EQUAL"
_CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL = "CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL"
_CONSTRAINTS_PER_SHAPE_DIFFERENT = "CONSTRAINTS_PER_SHAPE_DIFFERENT"

########### CONSTANTS -- Key groupings by category

_SHAPE_LIKELINESS_KEYS = [
        _SHAPES_COMPLETELY_EQUAL,
        _SHAPES_EQUAL_CONSTRAINT,
        _SHAPES_EQUAL_P_O_PAIRS,
        _SHAPES_EQUAL_PROPERTY,
        _SHAPES_DIFFERENT_CONSTRAINTS
    ]

_CONSTRAINT_LIKELINESS_KEYS = [
        _CONSTRAINTS_COMPLETELY_EQUAL,
        _CONSTRAINTS_VALIDATION_EQUAL,
        _CONSTRAINTS_P_O_EQUAL,
        _CONSTRAINTS_PROPERTY_EQUAL,
        _CONSTRAINTS_DIFFERENT
    ]

_CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS = [
        _CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL,
        _CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL,
        _CONSTRAINTS_PER_SHAPE_P_O_EQUAL,
        _CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL,
        _CONSTRAINTS_PER_SHAPE_DIFFERENT
    ]


########### Private functions


def _parse_shex_schema(shex_file_path: str) -> Schema:
    prefixes, shapes = parse_file(shex_file_path)
    return Schema(namespaces=prefixes,
                  shapes=shapes)


def _count_shared_shapes(schema1: Schema, schema2: Schema) -> int:
    shared = 0
    for a_shape in schema1.yield_shapes():
        if schema2.contains_shape(a_shape):
            shared += 1
        else:
            a=2
    return shared


def _run_shared_shapes_comparison(schema1: Schema, schema2: Schema, stats_dict: dict) -> None:
    number_of_shapes_shared = _count_shared_shapes(schema1, schema2)
    stats_dict[_SHARED_SHAPES] = number_of_shapes_shared
    stats_dict[_SHAPES_ONLY_IN_1] = schema1.n_shapes - number_of_shapes_shared
    stats_dict[_SHAPES_ONLY_IN_2] = schema2.n_shapes - number_of_shapes_shared


def _init_shape_alikeness_entries(stats_dict: dict) -> None:
    for a_key in _SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key] = {_ABS: 0, _RATIO: 0}


def _are_shapes_completely_equal(shape1: Shape, shape2: Shape) -> bool:
    if shape1.n_constraints != shape2.n_constraints:
        return False
    for a_constraint in shape1.yield_constraints():
        if not shape2.has_completely_equal_constraint(a_constraint):
            return False
    return True


def _are_shapes_constraint_equal(shape1: Shape, shape2: Shape) -> bool:
    if shape1.n_constraints != shape2.n_constraints:
        return False
    for a_constraint in shape1.yield_constraints():
        if not shape2.has_constraint_equal_no_stats(a_constraint):
            return False
    return True


def _are_shapes_p_o_equal(shape1: Shape, shape2: Shape) -> bool:
    if shape1.n_constraints != shape2.n_constraints:
        return False
    for a_constraint in shape1.yield_constraints():
        if not shape2.has_p_o_equal_constraint(a_constraint):
            return False
    return True


def _are_shapes_property_equal(shape1: Shape, shape2: Shape) -> bool:
    if shape1.n_constraints != shape2.n_constraints:
        return False
    for a_constraint in shape1.yield_constraints():
        if not shape2.has_property_equal_constraint(a_constraint):
            return False
    return True


def _classify_shape_likeliness(shape1: Shape, shape2: Shape, stats_dict: dict) -> None:
    if shape1.n_constraints != shape2.n_constraints:
        stats_dict[_SHAPES_DIFFERENT_CONSTRAINTS][_ABS] += 1
    elif _are_shapes_completely_equal(shape1, shape2):
        stats_dict[_SHAPES_COMPLETELY_EQUAL][_ABS] += 1
    elif _are_shapes_constraint_equal(shape1, shape2):
        stats_dict[_SHAPES_EQUAL_CONSTRAINT][_ABS] += 1
    elif _are_shapes_p_o_equal(shape1, shape2):
        stats_dict[_SHAPES_EQUAL_P_O_PAIRS][_ABS] += 1
    elif _are_shapes_property_equal(shape1, shape2):
        stats_dict[_SHAPES_EQUAL_PROPERTY][_ABS] += 1
    else:  # They must be somehow different
        stats_dict[_SHAPES_DIFFERENT_CONSTRAINTS][_ABS] += 1


def _run_ratio_shape_likeliness(stats_dict: dict) -> None:
    for a_key in _SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key][_RATIO] = \
            stats_dict[a_key][_ABS] / stats_dict[_SHARED_SHAPES]


def _run_shape_likeliness_comparison(schema1: Schema, schema2: Schema, stats_dict: dict) -> None:
    _init_shape_alikeness_entries(stats_dict)
    for a_shape in schema1.shapes:
        counterpart_shape = schema2.get_shape_by_label(a_shape.label)
        if counterpart_shape is not None:
            _classify_shape_likeliness(a_shape, counterpart_shape, stats_dict)
    _run_ratio_shape_likeliness(stats_dict)


def _init_constraint_likeliness_entries(stats_dict: dict) -> None:
    for a_key in _CONSTRAINT_LIKELINESS_KEYS + _CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key] = {_ABS: 0, _RATIO: 0}
    stats_dict[_TOTAL_NUMBER_OF_CONSTRAINTS] = 0

def _compute_constraints_per_shape_case(n_constraints: int,
                                        n_equal:int,
                                        n_validation:int,
                                        n_p_o:int,
                                        n_property:int,
                                        n_diff:int,
                                        stats_dict: dict) -> None:
    stats_dict[_CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL][_ABS] += n_equal / n_constraints
    stats_dict[_CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL][_ABS] += n_validation / n_constraints
    stats_dict[_CONSTRAINTS_PER_SHAPE_P_O_EQUAL][_ABS] += n_p_o / n_constraints
    stats_dict[_CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL][_ABS] += n_property / n_constraints
    stats_dict[_CONSTRAINTS_PER_SHAPE_DIFFERENT][_ABS] += n_diff / n_constraints

def _run_ratio_constraint_likeliness(n_constraints: int, stats_dict:dict) -> None:
    for a_key in _CONSTRAINT_LIKELINESS_KEYS + _CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key][_RATIO] = \
            stats_dict[a_key][_ABS] / n_constraints

def _classify_constraint_likeliness(shape1: Shape, shape2: Shape, stats_dict: dict) -> None:
    n_constraints = shape1.n_constraints
    c_equal = 0
    c_validation = 0
    c_p_o = 0
    c_property = 0
    c_diff = 0
    for a_constraint in shape1.yield_constraints():
        stats_dict[_TOTAL_NUMBER_OF_CONSTRAINTS] += 1
        if shape2.has_completely_equal_constraint(a_constraint):
            stats_dict[_CONSTRAINTS_COMPLETELY_EQUAL][_ABS] += 1
            c_equal += 1
        elif shape2.has_constraint_equal_no_stats(a_constraint):
            stats_dict[_CONSTRAINTS_VALIDATION_EQUAL][_ABS] += 1
            c_validation += 1
        elif shape2.has_p_o_equal_constraint(a_constraint):
            stats_dict[_CONSTRAINTS_P_O_EQUAL][_ABS] += 1
            c_p_o += 1
        elif shape2.has_property_equal_constraint(a_constraint):
            stats_dict[_CONSTRAINTS_PROPERTY_EQUAL][_ABS] += 1
            c_property += 1
        else:  # this constraint is not among the constraints of shape2
            stats_dict[_CONSTRAINTS_DIFFERENT][_ABS] += 1
            c_diff += 1
    constraints_in_shape2_not_in_shape1 = shape2.n_constraints - (shape1.n_constraints - c_diff)
    if constraints_in_shape2_not_in_shape1 > 0:
        stats_dict[_TOTAL_NUMBER_OF_CONSTRAINTS] += constraints_in_shape2_not_in_shape1
        c_diff += constraints_in_shape2_not_in_shape1
        n_constraints += constraints_in_shape2_not_in_shape1
    _compute_constraints_per_shape_case(n_constraints=n_constraints,
                                        n_equal=c_equal,
                                        n_validation=c_validation,
                                        n_p_o=c_p_o,
                                        n_property=c_property,
                                        n_diff=c_diff,
                                        stats_dict=stats_dict)
    _run_ratio_constraint_likeliness(n_constraints, stats_dict)


def _run_constraint_likeliness_comparison(schema1: Schema, schema2: Schema, stats_dict: dict) -> None:
    _init_constraint_likeliness_entries(stats_dict)
    for a_shape in schema1.shapes:
        counterpart_shape = schema2.get_shape_by_label(a_shape.label)
        if counterpart_shape is not None:
            _classify_constraint_likeliness(a_shape, counterpart_shape, stats_dict)

########### Public functions

def compare_schemas(schema1: Schema, schema2: Schema) -> dict:
    """
    1º - Shapes shared
        - Shapes in 1, not in two
        - shapes in 2, not in one.
    2º Among the shapes shared:
        - Shapes completely equal
        - Shapes equal at constraint level, but different comments.
        - Shapes equal at property-object level, but different cardinality.
        - Shapes equal regarding property usage, but different objects.
        - Shapes with different constraints.
    3º In shared shapes, avgs per shape, ratios:
        - completely equal constraints.
        - equal at constraint level.
        - equal at property-object level.
        - equal at property usage.
        - missed constraints.
    4º Same thing of constraints, but totals and ratios per shape

    :param schema1:
    :param schema2: 
    :return: JSON dictionary using the keys defined in teh const section of this file containing all that info
    """
    result = {}
    # The following division of tasks is quite efficient. The operation of looking for a similar shape in a schema
    # or comparing a given pair of constraint is performed many more times than necessary.
    # It does not really matter though considering the usual size of the schemas to be compared.
    _run_shared_shapes_comparison(schema1, schema2, result)
    _run_shape_likeliness_comparison(schema1, schema2, result)
    _run_constraint_likeliness_comparison(schema1, schema2, result)
    return result


def compare_shex_files(file_path1: str, file_path2: str) -> dict:
    """
    1º- Parse the shape schemas to in-memory objects
    2º- Run the comparison


    :param file_path1:
    :param file_path2:
    :return: JSON
    """

    schema1 = _parse_shex_schema(file_path1)
    schema2 = _parse_shex_schema(file_path2)
    return compare_schemas(schema1, schema2)
