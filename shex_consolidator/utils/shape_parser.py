from shex_consolidator.model import Namespace
from shex_consolidator.model import Shape

_END_SHAPE = "}"


def _relevant_shape_lines(shex_file: str):
    with open(shex_file, encoding="utf-8") as in_file:
        for a_line in in_file:
            if not a_line.startswith("PREFIX ") and not a_line.strip() == "":
                yield a_line


def _turn_grouped_lines_into_shape_objs(grouped_lines: list):
    return [Shape(a_group) for a_group in grouped_lines]


def _parse_shapes(shex_file: str):
    grouped_lines = []  # 2 dimensions
    current_group = []  # 1 dimension
    for a_line in _relevant_shape_lines(shex_file):
        stripped = a_line.strip()
        current_group.append(a_line)
        if stripped.startswith(_END_SHAPE):
            grouped_lines.append(current_group)
            current_group = []
    return _turn_grouped_lines_into_shape_objs(grouped_lines)


def _turn_p_lines_into_namespace_objs(p_lines):
    return [Namespace(namespace_declaration=a_p_line) for a_p_line in p_lines]


def _parse_prefixes(shex_file: str):
    with open(shex_file, encoding="utf-8") as in_file:
        p_lines = [a_line for a_line in in_file if a_line.startswith("PREFIX ")]
    return _turn_p_lines_into_namespace_objs(p_lines)


def parse_file(shex_file: str):
    prefixes = _parse_prefixes(shex_file)
    shapes = _parse_shapes(shex_file)
    return prefixes, shapes
