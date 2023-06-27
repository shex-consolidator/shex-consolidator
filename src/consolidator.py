_END_SHAPE = "}"
import re

_BLANKS = re.compile("  +")


class Constraint(object):

    def __init__(self, constraint_lines):
        self._original_lines = constraint_lines
        self._predicate, self._node_constraint, self._cardinality = \
            self._parse_predicate_and_node_constraint(constraint_lines[0]) \
                if constraint_lines is not None else None, None, None

    @property
    def predicate(self):
        return self._predicate

    @property
    def cardinality(self):
        return self._cardinality

    @property
    def node_constraint(self):
        return self._node_constraint

    @predicate.setter
    def predicate(self, value):
        self._predicate = value

    @cardinality.setter
    def cardinality(self, value):
        self._cardinality = value

    @node_constraint.setter
    def node_constraint(self, value):
        self._node_constraint = value

    def _parse_predicate_and_node_constraint(self, target_line: str):
        target_line = _BLANKS.sub(" ", target_line).strip()
        pieces = target_line.split(" ")
        predicate = pieces[0]
        node_constraint = pieces[1] if len(pieces) < 3 or pieces[2] != "OR" else self._look_for_or_node_constraint(
            pieces)
        expected_card_position = 2 if len(pieces) < 3 or pieces[2] != "OR" else self._r_index_or(pieces) + 1
        cardinality = "{1}" if len(pieces) < 3 or pieces[expected_card_position] in [";", "#"] else pieces[
            expected_card_position]
        if cardinality.endswith(";"):
            cardinality = cardinality[:-1]
        return predicate, node_constraint, cardinality

    def _r_index_or(self, str_pieces):
        return len(str_pieces) - 1 - str_pieces[::-1].index("OR")

    def _look_for_or_node_constraint(self, str_pieces: list):
        return " ".join(str_pieces[1:self._r_index_or(str_pieces) + 1])

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self._predicate == other.predicate and \
            self._cardinality == other.cardinality and \
            self._node_constraint == other.node_constraint

    def __ne__(self, other):
        return not (self == other)


class Shape(object):

    def __init__(self, shape_lines, shape_label: str = None):

        self._original_lines = shape_lines

        self._label, self._template = self._parse_label_and_template(shape_lines[0]) if shape_lines is not None else (
        shape_label, None)
        self._constraints = self._parse_constraints(shape_lines[1:]) if shape_lines is not None else []

    @property
    def label(self):
        return self._label

    def yield_constraints(self):
        for a_constraint in self._constraints:
            yield a_constraint

    def add_constraint(self, constraint: Constraint):
        self._constraints.append(constraint)

    def constraint_only_different_cardinality(self, target_constraint):
        for a_c in self._constraints:
            if target_constraint.predicate == a_c.predicate and \
                    target_constraint.node_constraint == a_c.node_constraint and \
                    target_constraint.cardinality != a_c.cardinality:
                return a_c
        return None

    def constraint_only_common_predicate(self, target_constraint):
        for a_c in self._constraints:
            if target_constraint.predicate == a_c.predicate and \
                    target_constraint.node_constraint != a_c.node_constraint:
                return a_c
        return None

    def _parse_constraints(self, shape_lines: list):
        result = []
        current_group = []
        for a_line in shape_lines:
            stripped = a_line.strip()
            if stripped not in ["{", "}"]:
                if not stripped.startswith("# ") and len(current_group) != 0:
                    result.append(Constraint(current_group))
                    current_group = []
                current_group.append(a_line)
        return result

    def _parse_label_and_template(self, heading_line: str):
        shape_label = heading_line[:heading_line.find(" ") if " " in heading_line else -1].strip()
        template = None if "[" not in heading_line else heading_line[heading_line.find("[") + 1:heading_line.find("]")]
        return shape_label, template


class Namespace(object):
    def __init__(self, namespace_declaration):
        self._prefix, self._url = self._parse_declaration(namespace_declaration)

    def _parse_declaration(self, declaration: str):  # example --> PREFIX dc: <http://purl.org/dc/terms/>
        declaration = declaration.strip()
        prefix = declaration[7:declaration.find(":")].strip()
        url = declaration[declaration.find("<") + 1:declaration.rfind(">")]
        return prefix, url

    @property
    def prefix(self):
        return self._prefix

    @property
    def url(self):
        return self._url


def _turn_p_lines_into_namespace_objs(p_lines):
    return [Namespace(namespace_declaration=a_p_line) for a_p_line in p_lines]


def _parse_prefixes(shex_file: str):
    with open(shex_file, encoding="utf-8") as in_file:
        p_lines = [a_line for a_line in in_file if a_line.startswith("PREFIX ")]
    return _turn_p_lines_into_namespace_objs(p_lines)


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


def parse_file(shex_file: str):
    prefixes = _parse_prefixes(shex_file)
    shapes = _parse_shapes(shex_file)
    return prefixes, shapes


def consolidate_prefixes(list_of_prefixes_groups: list):
    if len(list_of_prefixes_groups) == 0:
        return []
    dict_result = {}
    for a_group in list_of_prefixes_groups:
        for a_namespace in a_group:
            if a_namespace.prefix not in dict_result:
                dict_result[a_namespace.prefix] = a_namespace.url
            else:
                if a_namespace.url != dict_result[a_namespace.prefix]:
                    raise ValueError("There is a prefix ({}) currently associated to different namespaces "
                                     "({} and {}) in different files. This consolidator can't handle this case yet".format(
                        a_namespace.prefix,
                        a_namespace.url,
                        dict_result[a_namespace.prefix]
                    ))

    if len(dict_result) == len(list_of_prefixes_groups[0]):
        return list_of_prefixes_groups[0]
    for a_prefix, an_url in dict_result:
        return [Namespace("PREFIX {}: <{}>".format(a_prefix, an_url))]


def add_zero_case_to_cardinality(target_cardinality):
    if target_cardinality in ["*", "+"]:
        return "*"
    elif target_cardinality  in ["?", "{1}"]:
        return "?"
    elif target_cardinality.startswith("{"):
        return "*"
    else:
        raise ValueError("Trying to add zero case to an unknown cardinality: {}".format(target_cardinality))

def constraint_with_zero_case(target_constraint):
    result = Constraint(constraint_lines=None)
    result.predicate = target_constraint.predicate
    result.node_constraint = target_constraint.node_constraint
    result.cardinality = add_zero_case_to_cardinality(target_constraint.cardinality)
    return result

def most_general_cardinality(card1, card2):
    grouped_cards = [card1, card2]
    if card1 == card2:
        return card1
    elif "*" in grouped_cards or ("?" in grouped_cards and "+" in grouped_cards):
        return "*"
    elif "?" in grouped_cards:
        return "?"
    else:  # "+" in grouped_cards or they both start with "{" but are different
        return "+"


def constraint_with_most_general_cardinality(cons1, cons2):
    # Here I'm assuming that both constraints have the same predicade and node_constraint
    result = Constraint(constraint_lines=None)
    result.predicate = cons1.predicate
    result.node_constraint = cons1.node_constraint
    result.cardinality = most_general_cardinality(cons1.cardinality, cons2.cardinality)
    return result

def merge_shapes(shape1, shape2):
    result_shape = Shape(shape_lines=None, shape_label=shape1.label)
    merged_constraints = set()
    for a_constraint in shape1.yield_constraints():
        if shape2.contains_exact_constraint(a_constraint):
            result_shape.add_constraint(a_constraint)
            merged_constraints.add(a_constraint)
        else:
            target = shape2.constraint_only_different_cardinality(a_constraint)
            if target is not None:
                result_shape.add_constraint(constraint_with_most_general_cardinality(a_constraint, target))
                merged_constraints.add(a_constraint)
                merged_constraints.add(target)
            else:
                target = shape2.constraint_only_common_predicate(a_constraint)
                result_shape.add_constraint(constraint_with_zero_case(a_constraint))
                merged_constraints.add(a_constraint)
                merged_constraints.add(target)

    for a_constraint in [a_c for a_c in shape2.yield_constraints() if a_c not in merged_constraints]:
        result_shape.add_constraint(constraint_with_zero_case(a_constraint))

    return result_shape


def consolidate_shapes(list_of_shapes_groups: list):
    result_dict = {}
    for a_gropup in list_of_shapes_groups:
        for a_shape in a_gropup:
            if a_shape.label not in result_dict:
                result_dict[a_shape.label] = a_shape
            else:
                result_dict[a_shape.label] = merge_shapes(result_dict[a_shape.label], a_shape)
    return list(result_dict.values())


def consolidate_prefix_shape_tuples(prefixes_shapes_tuples: list):
    prefixes = consolidate_prefixes([a_tuple[0] for a_tuple in prefixes_shapes_tuples])
    shapes = consolidate_shapes([a_tuple[1] for a_tuple in prefixes_shapes_tuples])
    return prefixes, shapes


def consolidate_files(list_of_shex_files: list):
    targets = []
    for a_file in list_of_shex_files:
        targets.append(parse_file(a_file))
    prefixes, shapes = consolidate_prefix_shape_tuples(targets)
    a = 5


if __name__ == "__main__":
    template = r"C:\Users\Dani\repos_git\consolidator-shex\examples\pdb_subset{}.shex"
    files = [template.format(i) for i in range(10)]
    prefixes, shapes = parse_file(r"C:\Users\Dani\repos_git\consolidator-shex\examples\pdb_subset0.shex")
    print("Done")
