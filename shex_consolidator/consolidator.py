from shex_consolidator.model import Constraint, Shape, Namespace
from shex_consolidator.utils.shape_parser import parse_file
from shex_consolidator.utils.shape_serializer import serialize

_IRI = "IRI"
_BNODE = "BNODE"
_LITERAL = "LITERAL"
_NONLITERAL = "NONLITERAL"
_ANY = "."
_STARTING_SHAPE_LINK = "@"

_ABS_TOLERANCE_PER_FILE_SPLITS = 5
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
    result = []
    for a_prefix, an_url in dict_result.items():
        result.append(Namespace("PREFIX {}: <{}>".format(a_prefix, an_url)))
    return result


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

def _most_general_node_kind(kind1:str, kind2:str):
    if kind1 == _ANY:  # wildcard
        return _ANY
    elif kind1.startswith(_STARTING_SHAPE_LINK) or kind1 == _IRI: # shape or IRI
        if kind2.startswith(_STARTING_SHAPE_LINK) or kind2 == _IRI: # other shape or IRI
            return _IRI
        elif kind2 in [_BNODE, _NONLITERAL]: # bnode or nonliteral
            return _NONLITERAL
        else: # literal or wildcard
            return _ANY
    elif kind1 == _BNODE:  #bnode
        if kind2 in [_IRI, _NONLITERAL] or kind2.startswith(_STARTING_SHAPE_LINK):  # iri, nonliteral, a shape
            return _NONLITERAL
        else:  # literal or wildcard
            return _ANY
    elif kind1 == _NONLITERAL:
        if kind2 in [_IRI, _BNODE] or kind2.startswith(_STARTING_SHAPE_LINK):  # iri, bnode, a shape
            return _NONLITERAL
        else:  # literal or wildcard
            return _ANY
    else: # literal
        if kind2 in [_ANY, _IRI, _BNODE, _NONLITERAL] or kind2.startswith(_STARTING_SHAPE_LINK):  # anything except another literal
            return _ANY
        else: # another literal or the macro literal
            return _LITERAL



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

def _constraint_merged_node_kind(cons1, cons2) -> Constraint:
    result = Constraint(constraint_lines=None)
    result.predicate = cons1.predicate
    result.node_constraint = _most_general_node_kind(cons1.node_constraint, cons2.node_constraint)
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

def _is_type_constraint(a_constraint):
    return "[" in a_constraint.node_constraint and "]" in a_constraint.node_constraint



def _add_merged_constraints_to_shape(result_shape, shape1, shape2, ) -> None:
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
                    result_shape.add_constraint(_constraint_merged_node_kind(a_constraint, target))
                    merged_constraints.add(a_constraint)
                    merged_constraints.add(target)
                else:
                    result_shape.add_constraint(_constraint_with_zero_case(a_constraint))
                    merged_constraints.add(a_constraint)

    for a_constraint in [a_c for a_c in shape2.yield_constraints() if a_c not in merged_constraints]:
        result_shape.add_constraint(_constraint_with_zero_case(a_constraint))
    a = 2


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

def _can_a_constraint_promote(a_constraint: Constraint, shape_instances: int, instances_tolerance: int, minimum_ratio_to_promote: float):
    if a_constraint.instances in [None, 0] or shape_instances in [None, 0]:
        return False
    return a_constraint.incluides_zero_case() and \
           a_constraint.instances >= shape_instances - instances_tolerance and \
           a_constraint.instances / shape_instances > minimum_ratio_to_promote

def _promote_constraint(a_constraint: Constraint, shape_instances: int):
    a_constraint.instances = shape_instances
    a_constraint.cardinality = "+" if a_constraint.cardinality == "*" else ""  # from opt (?) to exactly one ( )
    print("promoted to ", a_constraint.cardinality, "!!")

def _handle_noisy_cardinalities(list_of_shapes: list,
                                number_of_files: int,
                                minimum_ratio_to_promote: float) -> None:
    for a_shape in list_of_shapes:
        for a_constraint in a_shape.yield_constraints():
            if _can_a_constraint_promote(a_constraint=a_constraint,
                                         instances_tolerance=number_of_files*_ABS_TOLERANCE_PER_FILE_SPLITS,
                                         minimum_ratio_to_promote=minimum_ratio_to_promote,
                                         shape_instances=a_shape.instances):
                _promote_constraint(a_constraint=a_constraint,
                                    shape_instances=a_shape.instances)

def _clean_low_ratio_constraints(list_of_shapes: list, acceptance_threshold: float) -> None:
    for a_shape in list_of_shapes:
        cs_to_remove = []
        for a_constraint in a_shape.yield_constraints():
            if a_constraint.instances is not None and a_shape.instances is not None:
                if a_constraint.instances / a_shape.instances < acceptance_threshold:
                    cs_to_remove.append(a_constraint)
        for a_constraint in cs_to_remove:
            a_shape.remove_constraint(a_constraint)

def _consolidate_shapes(list_of_shapes_groups: list,
                        number_of_files: int,
                        minimum_ratio_to_promote: float,
                        acceptance_threshold: float) -> list:
    result = {}
    for a_gropup in list_of_shapes_groups:
        for a_shape in a_gropup:
            if a_shape.label not in result:
                result[a_shape.label] = a_shape
            else:
                result[a_shape.label] = _merge_shapes(result[a_shape.label], a_shape)

    result = list(result.values())
    _clean_low_ratio_constraints(result, acceptance_threshold)
    _handle_noisy_cardinalities(result,
                                number_of_files,
                                minimum_ratio_to_promote)
    return result


def _consolidate_prefix_shape_tuples(prefixes_shapes_tuples: list,
                                     number_of_files: int,
                                     minimun_ratio_to_promote: float,
                                     acceptance_threshold: float) -> (list, list):
    prefixes = _consolidate_prefixes([a_tuple[0] for a_tuple in prefixes_shapes_tuples])
    shapes = _consolidate_shapes([a_tuple[1] for a_tuple in prefixes_shapes_tuples],
                                 number_of_files,
                                 minimun_ratio_to_promote,
                                 acceptance_threshold)
    return prefixes, shapes


def consolidate_files(list_of_shex_files: list, output_file: str, acceptance_threshold: float) -> None:
    targets = []
    for a_file in list_of_shex_files:
        targets.append(parse_file(a_file))
    prefixes, shapes = _consolidate_prefix_shape_tuples(prefixes_shapes_tuples=targets,
                                                        number_of_files=len(targets),
                                                        minimun_ratio_to_promote=0.97,
                                                        acceptance_threshold=acceptance_threshold)
    serialize(prefixes, shapes, output_file)



