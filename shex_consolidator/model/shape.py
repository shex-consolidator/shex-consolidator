from shex_consolidator.model.constraint import Constraint


class Shape(object):

    def __init__(self, shape_lines, shape_label: str = None):

        self._original_lines = shape_lines

        self._label, self._template, self._instances = self._parse_label_and_template(
            shape_lines[0]) if shape_lines is not None else (
            shape_label, None, None)
        self._constraints = self._parse_constraints(shape_lines[1:]) if shape_lines is not None else []

    @property
    def original_lines(self):
        return self._original_lines

    @property
    def label(self):
        return self._label

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value

    @property
    def instances(self):
        return self._instances

    @instances.setter
    def instances(self, value):
        self._instances = value

    @property
    def n_constraints(self):
        return len(self._constraints)

    def yield_constraints(self):
        for a_constraint in self._constraints:
            yield a_constraint

    def add_constraint(self, constraint: Constraint):
        self._constraints.append(constraint)

    def remove_constraint(self, constraint: Constraint):
        self._constraints.remove(constraint)

    def exact_constraint(self, target_constraint, exclude: [None, list] = None):
        for a_c in self._constraints:
            if target_constraint.predicate == a_c.predicate and \
                    target_constraint.node_constraint == a_c.node_constraint and \
                    target_constraint.cardinality == a_c.cardinality:
                if exclude is None or target_constraint not in exclude:
                    return a_c
        return None

    def constraint_only_different_cardinality(self, target_constraint, strict_mode=True, exclude: [None, list] = None):
        for a_c in self._constraints:
            if target_constraint.predicate == a_c.predicate and \
                    target_constraint.node_constraint == a_c.node_constraint:
                if strict_mode:
                    if target_constraint.cardinality != a_c.cardinality and \
                            (exclude is None or target_constraint not in exclude):
                        return a_c
                elif exclude is None or target_constraint not in exclude:
                    return a_c
        return None

    def constraint_only_common_predicate(self, target_constraint, strict_mode=True, exclude: [None, list] = None):
        for a_c in self._constraints:
            if target_constraint.predicate == a_c.predicate:
                if strict_mode:
                    if target_constraint.node_constraint != a_c.node_constraint and \
                            (exclude is None or target_constraint not in exclude):
                        return a_c
                elif exclude is None or target_constraint not in exclude:
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
        if len(current_group) != 0:
            result.append(Constraint(current_group))
        return result

    def _parse_label_and_template(self, heading_line: str):
        shape_label = heading_line[:heading_line.find(" ") if " " in heading_line else -1].strip()
        template = None if "[" not in heading_line else heading_line[
                                                        heading_line.find("[") + 2:heading_line.find("]") - 2]
        pieces = heading_line.replace("instances", "instance").strip().split(" ")
        instances = None if "instance" not in pieces else int(pieces[pieces.index("instance") - 1])
        return shape_label, template, instances

    def has_completely_equal_constraint(self, a_constraint: Constraint):
        candidate_constraint = self.exact_constraint(a_constraint)
        if candidate_constraint is None:
            return False
        return candidate_constraint.instances == self._instances

    def has_constraint_equal_no_stats(self, a_constraint: Constraint, exclude: [None, list] = None):
        return self.exact_constraint(a_constraint, exclude=exclude) is not None

    def has_p_o_equal_constraint(self, a_constraint: Constraint, exclude: [None, list] = None):
        return self.constraint_only_different_cardinality(a_constraint, strict_mode=False, exclude=exclude) is not None

    def has_property_equal_constraint(self, a_constraint: Constraint, exclude: [None, list] = None):
        return self.constraint_only_common_predicate(a_constraint, strict_mode=False, exclude=exclude) is not None
