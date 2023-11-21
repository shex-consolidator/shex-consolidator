from shex_consolidator.utils.shape_parser import parse_file
from shex_consolidator.model import Schema, Shape

######################## CONSTANTS -- Key definitions for JSON result

ABS = "absolute_value"
RATIO = "ratio"

SHARED_SHAPES = "SHARED_SHAPES"
SHAPES_ONLY_IN_1 = "SHAPES_ONLY_IN_1"
SHAPES_ONLY_IN_2 = "SHAPES_ONLY_IN_2"

_TOTAL_NUMBER_OF_CONSTRAINTS = "N_CONSTRAINTS"


SHAPES_COMPLETELY_EQUAL = "SHAPES_COMPLETELY_EQUAL"
SHAPES_EQUAL_CONSTRAINT = "SHAPES_EQUAL_CONSTRAINT"
SHAPES_EQUAL_P_O_PAIRS = "SHAPES_EQUAL_P_O_PAIRS"
SHAPES_EQUAL_PROPERTY = "SHAPES_EQUAL_PROPERTY"
SHAPES_DIFFERENT_CONSTRAINTS = "SHAPES_DIFFERENT_CONSTRAINTS"



CONSTRAINTS_COMPLETELY_EQUAL = "CONSTRAINTS_COMPLETELY_EQUAL"
CONSTRAINTS_VALIDATION_EQUAL = "CONSTRAINTS_VALIDATION_EQUAL"
CONSTRAINTS_P_O_EQUAL = "CONSTRAINTS_P_O_EQUAL"
CONSTRAINTS_PROPERTY_EQUAL = "CONSTRAINTS_PROPERTY_EQUAL"
CONSTRAINTS_DIFFERENT = "CONSTRAINTS_DIFFERENT"



CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL = "CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL"
CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL = "CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL"
CONSTRAINTS_PER_SHAPE_P_O_EQUAL = "CONSTRAINTS_PER_SHAPE_P_O_EQUAL"
CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL = "CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL"
CONSTRAINTS_PER_SHAPE_DIFFERENT = "CONSTRAINTS_PER_SHAPE_DIFFERENT"

########### CONSTANTS -- Key groupings by category

SHAPE_LIKELINESS_KEYS = [
        SHAPES_COMPLETELY_EQUAL,
        SHAPES_EQUAL_CONSTRAINT,
        SHAPES_EQUAL_P_O_PAIRS,
        SHAPES_EQUAL_PROPERTY,
        SHAPES_DIFFERENT_CONSTRAINTS
    ]

CONSTRAINT_LIKELINESS_KEYS = [
        CONSTRAINTS_COMPLETELY_EQUAL,
        CONSTRAINTS_VALIDATION_EQUAL,
        CONSTRAINTS_P_O_EQUAL,
        CONSTRAINTS_PROPERTY_EQUAL,
        CONSTRAINTS_DIFFERENT
    ]

CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS = [
        CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL,
        CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL,
        CONSTRAINTS_PER_SHAPE_P_O_EQUAL,
        CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL,
        CONSTRAINTS_PER_SHAPE_DIFFERENT
    ]

KEY_EXPLANATIONS = {
        SHAPES_COMPLETELY_EQUAL: "Number of shapes completely equal in both files",
        SHAPES_EQUAL_CONSTRAINT: "Number of shapes with equal constraints w.r.t. validation, but some ended up having a different number of annotated instances",
        SHAPES_EQUAL_P_O_PAIRS: "Number of shapes whose constraints have always the same predicate and node constraint, but at least one with different cardinality",
        SHAPES_EQUAL_PROPERTY: "Number of shapes whose constraints have always the same predicate, but at least one has a different node constraint",
        SHAPES_DIFFERENT_CONSTRAINTS: "Number of shapes including constraints that are not in both versions of the shape",
        CONSTRAINTS_COMPLETELY_EQUAL: "Number of constraints completely equal in both files",
        CONSTRAINTS_VALIDATION_EQUAL: "Number of equal constraints but with a different number of annotated instances",
        CONSTRAINTS_P_O_EQUAL: "Number of constraints that have the same predicate and node constraint, but different cardinality",
        CONSTRAINTS_PROPERTY_EQUAL: "Number of constraints that have the same predicate, but different node constraint",
        CONSTRAINTS_DIFFERENT: "Number of constraints that are not in both versions of the shape",
        CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL: "Average constraints in a shape that are completely equal in both files",
        CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL: "Average constraints in a shape that are equal constraints but with a different number of annotated instances",
        CONSTRAINTS_PER_SHAPE_P_O_EQUAL: "Average constraints in a shape that have the same predicate and node constraint, but different cardinality",
        CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL: "Average constraints in a shape that have the same predicate, but different node constraint",
        CONSTRAINTS_PER_SHAPE_DIFFERENT: "Average constraints in a shape that are not in both versions of the shape",
}

DIFF_CONST_IN_SCHEMA_1 = "DIFF_CONST_IN_SCHEMA_1"



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
    return shared


def _run_shared_shapes_comparison(schema1: Schema, schema2: Schema, stats_dict: dict) -> None:
    number_of_shapes_shared = _count_shared_shapes(schema1, schema2)
    stats_dict[SHARED_SHAPES] = number_of_shapes_shared
    stats_dict[SHAPES_ONLY_IN_1] = schema1.n_shapes - number_of_shapes_shared
    stats_dict[SHAPES_ONLY_IN_2] = schema2.n_shapes - number_of_shapes_shared


def _init_shape_alikeness_entries(stats_dict: dict) -> None:
    for a_key in SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key] = {ABS: 0, RATIO: 0}


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
        stats_dict[SHAPES_DIFFERENT_CONSTRAINTS][ABS] += 1
    elif _are_shapes_completely_equal(shape1, shape2):
        stats_dict[SHAPES_COMPLETELY_EQUAL][ABS] += 1
    elif _are_shapes_constraint_equal(shape1, shape2):
        stats_dict[SHAPES_EQUAL_CONSTRAINT][ABS] += 1
    elif _are_shapes_p_o_equal(shape1, shape2):
        stats_dict[SHAPES_EQUAL_P_O_PAIRS][ABS] += 1
    elif _are_shapes_property_equal(shape1, shape2):
        stats_dict[SHAPES_EQUAL_PROPERTY][ABS] += 1
    else:  # They must be somehow different
        stats_dict[SHAPES_DIFFERENT_CONSTRAINTS][ABS] += 1


def _run_ratio_shape_likeliness(stats_dict: dict) -> None:
    for a_key in SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key][RATIO] = \
            stats_dict[a_key][ABS] / stats_dict[SHARED_SHAPES]


def _run_shape_likeliness_comparison(schema1: Schema, schema2: Schema, stats_dict: dict) -> None:
    _init_shape_alikeness_entries(stats_dict)
    for a_shape in schema1.shapes:
        counterpart_shape = schema2.get_shape_by_label(a_shape.label)
        if counterpart_shape is not None:
            _classify_shape_likeliness(a_shape, counterpart_shape, stats_dict)
    _run_ratio_shape_likeliness(stats_dict)


def _init_constraint_likeliness_entries(stats_dict: dict) -> None:
    for a_key in CONSTRAINT_LIKELINESS_KEYS + CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key] = {ABS: 0, RATIO: 0}
    stats_dict[_TOTAL_NUMBER_OF_CONSTRAINTS] = 0
    stats_dict[DIFF_CONST_IN_SCHEMA_1] = []

def _compute_constraints_per_shape_case(n_constraints: int,
                                        n_equal:int,
                                        n_validation:int,
                                        n_p_o:int,
                                        n_property:int,
                                        n_diff:int,
                                        stats_dict: dict) -> None:
    stats_dict[CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL][RATIO] += n_equal / n_constraints
    stats_dict[CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL][RATIO] += n_validation / n_constraints
    stats_dict[CONSTRAINTS_PER_SHAPE_P_O_EQUAL][RATIO] += n_p_o / n_constraints
    stats_dict[CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL][RATIO] += n_property / n_constraints
    stats_dict[CONSTRAINTS_PER_SHAPE_DIFFERENT][RATIO] += n_diff / n_constraints

def _run_ratio_constraint_likeliness(n_constraints: int, stats_dict:dict, n_shapes:int) -> None:

    for a_key in CONSTRAINT_LIKELINESS_KEYS:
        stats_dict[a_key][RATIO] = \
            stats_dict[a_key][ABS] / n_constraints

    accumulated_absolute_avgs_per_shape = 0

    for a_key in CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key][ABS] = \
            stats_dict[a_key][ABS] / n_shapes
        accumulated_absolute_avgs_per_shape += stats_dict[a_key][ABS]


    for a_key in CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS:
        stats_dict[a_key][RATIO] = \
            stats_dict[a_key][ABS] / accumulated_absolute_avgs_per_shape

def _classify_constraint_likeliness(shape1: Shape, shape2: Shape, stats_dict: dict) -> int:
    n_constraints = shape1.n_constraints
    c_equal = 0
    c_validation = 0
    c_p_o = 0
    c_property = 0
    c_diff = 0
    for a_constraint in shape1.yield_constraints():
        stats_dict[_TOTAL_NUMBER_OF_CONSTRAINTS] += 1
        if shape2.has_completely_equal_constraint(a_constraint):
            stats_dict[CONSTRAINTS_COMPLETELY_EQUAL][ABS] += 1
            stats_dict[CONSTRAINTS_PER_SHAPE_COMPLETELY_EQUAL][ABS] += 1
            c_equal += 1
        elif shape2.has_constraint_equal_no_stats(a_constraint):
            stats_dict[CONSTRAINTS_VALIDATION_EQUAL][ABS] += 1
            stats_dict[CONSTRAINTS_PER_SHAPE_VALIDATION_EQUAL][ABS] += 1
            c_validation += 1
        elif shape2.has_p_o_equal_constraint(a_constraint):
            stats_dict[CONSTRAINTS_P_O_EQUAL][ABS] += 1
            stats_dict[CONSTRAINTS_PER_SHAPE_P_O_EQUAL][ABS] += 1
            c_p_o += 1
        elif shape2.has_property_equal_constraint(a_constraint):
            stats_dict[CONSTRAINTS_PROPERTY_EQUAL][ABS] += 1
            stats_dict[CONSTRAINTS_PER_SHAPE_PROPERTY_EQUAL][ABS] += 1
            c_property += 1
        else:  # this constraint is not among the constraints of shape2
            stats_dict[CONSTRAINTS_DIFFERENT][ABS] += 1
            stats_dict[CONSTRAINTS_PER_SHAPE_DIFFERENT][ABS] += 1
            c_diff += 1
            stats_dict[DIFF_CONST_IN_SCHEMA_1].append( (shape1.label, a_constraint.predicate, a_constraint.node_constraint) )
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
    return n_constraints



def _run_constraint_likeliness_comparison(schema1: Schema, schema2: Schema, stats_dict: dict) -> None:
    _init_constraint_likeliness_entries(stats_dict)
    total_constraints = 0
    shapes_expored = 0
    for a_shape in schema1.shapes:
        counterpart_shape = schema2.get_shape_by_label(a_shape.label)
        if counterpart_shape is not None:
            shapes_expored += 1
            total_constraints += _classify_constraint_likeliness(a_shape, counterpart_shape, stats_dict)
    _run_ratio_constraint_likeliness(n_constraints=total_constraints,
                                     stats_dict=stats_dict,
                                     n_shapes=shapes_expored)

########### Public functions

def explain(a_key: str) -> str:
    return KEY_EXPLANATIONS[a_key] if a_key in KEY_EXPLANATIONS else a_key

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
