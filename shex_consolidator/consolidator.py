from model import Constraint, Shape, Namespace
from utils.shape_parser import parse_file
from utils.shape_serializer import serialize

def _consolidate_prefixes(list_of_prefixes_groups: list) -> list:
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


def _add_zero_case_to_cardinality(target_cardinality) -> str:
    if target_cardinality in ["*", "+"]:
        return "*"
    elif target_cardinality in ["?", "{1}"]:
        return "?"
    elif target_cardinality.startswith("{"):
        return "*"
    else:
        raise ValueError("Trying to add zero case to an unknown cardinality: {}".format(target_cardinality))


def _constraint_with_zero_case(target_constraint) -> Constraint:
    result = Constraint(constraint_lines=None)
    result.predicate = target_constraint.predicate
    result.node_constraint = target_constraint.node_constraint
    result.cardinality = _add_zero_case_to_cardinality(target_constraint.cardinality)
    if target_constraint.instances is not None:
        result.instances = target_constraint.instances
    return result


def _most_general_cardinality(card1, card2) -> str:
    grouped_cards = [card1, card2]
    if card1 == card2:
        return card1
    elif "*" in grouped_cards or ("?" in grouped_cards and "+" in grouped_cards):
        return "*"
    elif "?" in grouped_cards:
        return "?"
    else:  # "+" in grouped_cards or they both start with "{" but are different
        return "+"


def _constraint_exact_match(cons1, cons2) -> Constraint:
    result = Constraint(constraint_lines=None)
    result.predicate = cons1.predicate
    result.node_constraint = cons1.node_constraint
    result.cardinality = cons1.cardinality
    if cons1.instances is not None and cons2.instances is not None:
        result.instances = cons1.instances + cons2.instances
    return result


def _constraint_with_most_general_cardinality(cons1, cons2) -> Constraint:
    # Here I'm assuming that both constraints have the same predicade and node_constraint
    result = Constraint(constraint_lines=None)
    result.predicate = cons1.predicate
    result.node_constraint = cons1.node_constraint
    result.cardinality = _most_general_cardinality(cons1.cardinality, cons2.cardinality)
    if cons1.instances is not None and cons2.instances is not None:
        result.instances = cons1.instances + cons2.instances
    return result


def _longest_common_prefix(uri1, uri2) -> str:
    """
    It returns a str containing the longest possible common initial part of uri1 and uri2

    :param uri1:
    :param uri2:

    :return:
    """
    if len(uri1) == 0 or len(uri2) == 0:
        return ""
    shortest = len(uri1) if len(uri1) < len(uri2) else len(uri2)
    for i in range(shortest):
        if uri1[i] != uri2[i]:
            return uri1[:i]
    return uri1[:shortest]


def _compute_longest_common_template(template1, template2) -> [None, str]:
    candidate = _longest_common_prefix(template1, template2)
    if candidate == "":
        return None
    further_slash = candidate.rfind("/")
    further_sharp = candidate.rfind("#")
    candidate = candidate[:(further_slash if further_slash > further_sharp else further_sharp) + 1]
    if len(candidate) > 10:
        return candidate
    return None


def _add_merged_constraints_to_shape(result_shape, shape1, shape2) -> None:
    merged_constraints = set()
    for a_constraint in shape1.yield_constraints():
        target = shape2.exact_constraint(a_constraint)
        if target is not None:
            result_shape.add_constraint(_constraint_exact_match(a_constraint, target))
            merged_constraints.add(a_constraint)
            merged_constraints.add(target)
        else:
            target = shape2.constraint_only_different_cardinality(a_constraint)
            if target is not None:
                result_shape.add_constraint(_constraint_with_most_general_cardinality(a_constraint, target))
                merged_constraints.add(a_constraint)
                merged_constraints.add(target)
            else:
                target = shape2.constraint_only_common_predicate(a_constraint)
                if target is not None:
                    result_shape.add_constraint(_constraint_with_zero_case(a_constraint))
                    merged_constraints.add(a_constraint)
                    merged_constraints.add(target)
                else:
                    result_shape.add_constraint(_constraint_with_zero_case(a_constraint))
                    merged_constraints.add(a_constraint)

    for a_constraint in [a_c for a_c in shape2.yield_constraints() if a_c not in merged_constraints]:
        result_shape.add_constraint(_constraint_with_zero_case(a_constraint))


def _merge_shapes(shape1, shape2) -> Shape:
    result_shape = Shape(shape_lines=None, shape_label=shape1.label)
    if shape1.template is not None and shape2.template is not None:
        if shape1.template == shape2.template:
            result_shape.template = shape1.template
        else:
            result_shape.template = _compute_longest_common_template(shape1.template, shape2.template)
        if shape1.instances is not None and shape2.instances is not None:
            result_shape.instances = shape1.instances + shape2.instances

    _add_merged_constraints_to_shape(result_shape=result_shape,
                                     shape1=shape1,
                                     shape2=shape2)

    return result_shape


def _consolidate_shapes(list_of_shapes_groups: list) -> list:
    result_dict = {}
    for a_gropup in list_of_shapes_groups:
        for a_shape in a_gropup:
            if a_shape.label not in result_dict:
                result_dict[a_shape.label] = a_shape
            else:
                result_dict[a_shape.label] = _merge_shapes(result_dict[a_shape.label], a_shape)
    return list(result_dict.values())


def _consolidate_prefix_shape_tuples(prefixes_shapes_tuples: list) -> (list, list):
    prefixes = _consolidate_prefixes([a_tuple[0] for a_tuple in prefixes_shapes_tuples])
    shapes = _consolidate_shapes([a_tuple[1] for a_tuple in prefixes_shapes_tuples])
    return prefixes, shapes


def consolidate_files(list_of_shex_files: list, output_file: str) -> None:
    targets = []
    for a_file in list_of_shex_files:
        targets.append(parse_file(a_file))
    prefixes, shapes = _consolidate_prefix_shape_tuples(targets)
    serialize(prefixes, shapes, output_file)



