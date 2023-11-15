from shex_consolidator.utils.shape_parser import parse_file
from shex_consolidator.model import Schema, Shape

_SHARED_SHAPES = "SHARED_SHAPES"
_SHAPES_ONLY_IN_1 = "SHAPES_ONLY_IN_1"
_SHAPES_ONLY_IN_2 = "SHAPES_ONLY_IN_2"

# Shapes completly equal
#         - Shapes completly equal at constraint level, but different comments.
#         - Shapres completly equal at property-object level, but different cardinality.
#         - Shapes completly equal regarding property usage, but different objects.
#         - Shapes with different constraints.

_SHAPES_COMPLETELY_EQUAL = "SHAPES_COMPLETELY_EQUAL"
_SHAPES_EQUAL_CONSTRAINT = "SHAPES_EQUAL_CONSTRAINT"
_SHAPES_EQUAL_P_O_PAIRS = "SHAPES_EQUAL_P_O_PAIRS"
_SHAPES_EQUAL_PROPERTY = "SHAPES_EQUAL_PROPERTY"
_SHAPES_DIFFERENT_CONSTRAINTS = "SHAPES_DIFFERENT_CONSTRAINTS"

_LIKELINESS_KEYS = [
        _SHAPES_COMPLETELY_EQUAL,
        _SHAPES_EQUAL_CONSTRAINT,
        _SHAPES_EQUAL_P_O_PAIRS,
        _SHAPES_EQUAL_PROPERTY,
        _SHAPES_DIFFERENT_CONSTRAINTS
    ]

_ABS = "absolute_number"
_RATIO = "ratio"


def _parse_shex_schema(shex_file_path: str):
    prefixes, shapes = parse_file(shex_file_path)
    return Schema(namespaces=prefixes,
                  shapes=shapes)


def _count_shared_shapes(schema1: Schema, schema2: Schema):
    shared = 0
    for a_shape in schema1.yield_shapes():
        if schema2.contains_shape(a_shape):
            shared += 1
    return shared


def _run_shared_shapes_comparison(schema1: Schema, schema2: Schema, stats_dict: dict):
    number_of_shapes_shared = _count_shared_shapes(schema1, schema2)
    stats_dict[_SHARED_SHAPES] = number_of_shapes_shared
    stats_dict[_SHAPES_ONLY_IN_1] = schema1.n_shapes - number_of_shapes_shared
    stats_dict[_SHAPES_ONLY_IN_2] = schema2.n_shapes - number_of_shapes_shared


def _init_shape_alikeness_entries(stats_dict: dict):
    for a_key in _LIKELINESS_KEYS:
        stats_dict[a_key] = {_ABS: 0, _RATIO: 0}


def are_shapes_completely_equal(shape1: Shape, shape2: Shape):
    if shape1.n_constraints != shape2.n_constraints:
        return False
    for a_constraint in shape1.yield_constraints():
        if not shape2.has_completely_equal_constraint(a_constraint):
            return False
    return True


def _are_shapes_constraint_equal(shape1: Shape, shape2: Shape):
    if shape1.n_constraints != shape2.n_constraints:
        return False
    for a_constraint in shape1.yield_constraints():
        if not shape2.has_constraint_equal_no_stats(a_constraint):
            return False
    return True


def _are_shapes_p_o_equal(shape1: Shape, shape2: Shape):
    if shape1.n_constraints != shape2.n_constraints:
        return False
    for a_constraint in shape1.yield_constraints():
        if not shape2.has_p_o_equal_constraint(a_constraint):
            return False
    return True


def _are_shapes_property_equal(shape1: Shape, shape2: Shape):
    if shape1.n_constraints != shape2.n_constraints:
        return False
    for a_constraint in shape1.yield_constraints():
        if not shape2.has_roperty_equal_constraint(a_constraint):
            return False
    return True


def _classify_shape_likeliness(shape1: Shape, shape2: Shape, stats_dict: dict):
    if shape1.n_constraints != shape2.n_constraints:
        stats_dict[_SHAPES_DIFFERENT_CONSTRAINTS][_ABS] += 1
    elif are_shapes_completely_equal(shape1, shape2):
        stats_dict[_SHAPES_COMPLETELY_EQUAL][_ABS] += 1
    elif _are_shapes_constraint_equal(shape1, shape2):
        stats_dict[_SHAPES_EQUAL_CONSTRAINT][_ABS] += 1
    elif _are_shapes_p_o_equal(shape1, shape2):
        stats_dict[_SHAPES_EQUAL_P_O_PAIRS][_ABS] += 1
    elif _are_shapes_property_equal(shape1, shape2):
        stats_dict[_SHAPES_EQUAL_PROPERTY][_ABS] += 1
    else:  # They must be somehow different
        stats_dict[_SHAPES_DIFFERENT_CONSTRAINTS][_ABS] += 1


def _run_ratio_shape_likeliness(stats_dict: dict):
    for a_key in _LIKELINESS_KEYS:
        stats_dict[a_key][_RATIO] = \
            stats_dict[a_key][_ABS] / stats_dict[_SHARED_SHAPES]


def _run_shape_likeliness_comparison(schema1: Schema, schema2: Schema, stats_dict: dict):
    _init_shape_alikeness_entries(stats_dict)
    for a_shape in schema1.shapes:
        counterpart_shape = schema2.get_shape_by_label(a_shape.label)
        if counterpart_shape is not None:
            _classify_shape_likeliness(a_shape, counterpart_shape, stats_dict)
    _run_ratio_shape_likeliness(stats_dict)


def _init_constraint_likeliness_entries(stats_dict):
    pass  # todo


def _run_constraint_likeliness_comparison(schema1: Schema, schema2: Schema, stats_dict: dict):
    _init_constraint_likeliness_entries(stats_dict)
    pass  # TODO; continue


def comparison_stats_report(schema1: Schema, schema2: Schema):
    """
    1º - Shapes shared
        - Shapes in 1, not in two
        - shapes in 2, not in one.
    2º Among the shapes shared:
        - Shapes completly equal
        - Shapes completly equal at constraint level, but different comments.
        - Shapres completly equal at property-object level, but different cardinality.
        - Shapes completly equal regarding property usage, but different objects.
        - Shapes with different constraints.
    3º In shared shapes, avgs per shape, ratios:
        - completly equal constraints.
        - equal at constraint level.
        - equal at property-object level.
        - equal at property usage.
        - missed constraints.

    :param schema1:
    :param schema2: 
    :return:
    """
    result = {}
    _run_shared_shapes_comparison(schema1, schema2, result)
    _run_shape_likeliness_comparison(schema1, schema2, result)
    _run_constraint_likeliness_comparison(schema1, schema2, result)
    return result


def compare_shex_files(file_path1: str, file_path2: str):
    """
    1º- Parse the shape schemas to in-memory objects
    2º- Run the comparison


    :param file_path1:
    :param file_path2:
    :return:
    """

    schema1 = _parse_shex_schema(file_path1)
    schema2 = _parse_shex_schema(file_path2)
    return comparison_stats_report(schema1, schema2)
