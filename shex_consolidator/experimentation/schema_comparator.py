from shex_consolidator.utils.shape_parser import parse_file
from shex_consolidator.model import Schema


_SHARED_SHAPES = "SHARED_SHAPES"
_SHAPES_ONLY_IN_1 = "SHAPES_ONLY_IN_1"
_SHAPES_ONLY_IN_2 = "SHAPES_ONLY_IN_2"

def _parse_shex_schema(shex_file_path):
    prefixes, shapes = parse_file(shex_file_path)
    return Schema(namespaces=prefixes,
                  shapes=shapes)

def _count_shared_shapes(schema1:Schema, schema2:Schema):
    shared = 0
    for a_shape in schema1.yield_shapes():
        if schema2.contains_shape(a_shape):
            shared += 1
    return shared

def _run_shared_shapes_comparison(schema1:Schema, schema2:Schema, stats_dict:dict):
    number_of_shapes_shared = _count_shared_shapes(schema1, schema2)
    stats_dict[_SHARED_SHAPES] = number_of_shapes_shared
    stats_dict[_SHAPES_ONLY_IN_1] = schema1.n_shapes - number_of_shapes_shared
    stats_dict[_SHAPES_ONLY_IN_2] = schema2.n_shapes - number_of_shapes_shared

def _run_shape_alikeness_comparison(schema1:Schema, schema2:Schema, stats_dict:dict):
    pass  # TODO: WHOLE THING

def comparison_stats_report(schema1:Schema, schema2:Schema):
    """
    1º - Shapes sahred
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

    :param schem1a:
    :param schema1:
    :return:
    """
    result = {}
    _run_shared_shapes_comparison(schema1, schema2, result)
    _run_shape_alikeness_comparison(schema1, schema2, result)
    # TODO: STEP 3
    return result

def compare_shex_files(file_path1: str, file_path2:str):
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