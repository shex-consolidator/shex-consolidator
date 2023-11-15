import re

_BLANKS = re.compile("  +")


class Constraint(object):

    def __init__(self, constraint_lines):
        self._original_lines = constraint_lines
        self._predicate, self._node_constraint, self._cardinality = \
            self._parse_predicate_and_node_constraint(constraint_lines[0]) \
                if constraint_lines is not None else (None, None, None)
        self._instances = self._parse_instances(constraint_lines) \
            if constraint_lines is not None else None

    @property
    def original_lines(self):
        return self._original_lines

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

    @property
    def instances(self):
        return self._instances

    @instances.setter
    def instances(self, value):
        self._instances = value

    def _parse_instances(self, original_lines):
        pieces = original_lines[0].replace(")", " ").replace("(", " ").replace("instances", "instance").split(" ")
        try:
            pos_instances = pieces.index("instance")
        except ValueError:
            if len(original_lines) == 1:
                return None
            pieces = original_lines[1].replace(")", " ").replace("(", " ").replace("instances", "instance").split(" ")
            try:
                pos_instances = pieces.index("instance")
            except ValueError:
                return None
            return int(pieces[pos_instances - 1])
        return int(pieces[pos_instances - 1])

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

    # def __eq__(self, other):
    #     if type(other) != type(self):
    #         return False
    #     return self._predicate == other.predicate and \
    #         self._cardinality == other.cardinality and \
    #         self._node_constraint == other.node_constraint
    #
    # def __ne__(self, other):
    #     return not (self == other)
    #
    # def __hash__(self):
    #     return hash(self.__attrs())