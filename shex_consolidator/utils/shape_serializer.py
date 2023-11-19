_HEADING_TEMPLATE = "{}  [<{}>~]  AND"
_SHAPE_INSTANCES_TEMPLATE = "         #  {} instances"
_CONSTRAINT_TEMPLATE_CARD_ARB = "    {}  {}  {}"
_CONSTRAINT_TEMPLATE_CARD_1 = "    {}  {}  "
_CONSTRAINT_TEMPLATE_INSTANCES = "        #   {}  % ({} instances)"
_PREFIX_TEMPLATE = "PREFIX {}: <{}>\n"


def _serialize_prefixes(prefixes, out_stream):
    for a_prefix in prefixes:
        out_stream.write(_PREFIX_TEMPLATE.format(a_prefix.prefix, a_prefix.url))


def _str_constraints_of_a_shape(a_shape):
    result_constraints = []
    counter = 0
    for a_constraint in a_shape.yield_constraints():
        counter +=1
        if a_constraint.cardinality != "{1}":
            base_str = _CONSTRAINT_TEMPLATE_CARD_ARB.format(a_constraint.predicate,
                                                                           a_constraint.node_constraint,
                                                                           a_constraint.cardinality)
        else:
            base_str = _CONSTRAINT_TEMPLATE_CARD_1.format(a_constraint.predicate,
                                                                         a_constraint.node_constraint)
        if counter < a_shape.n_constraints:
            base_str += ";"
        if a_constraint.instances is not None and a_shape.instances is not None:
            base_str += _CONSTRAINT_TEMPLATE_INSTANCES.format(round(a_constraint.instances/a_shape.instances*100, 3),
                                                              a_constraint.instances)
        result_constraints.append(base_str)
    return "\n".join(result_constraints)



def _heading_of_a_shape(a_shape):
    if a_shape.template is not None:
        base_result = _HEADING_TEMPLATE.format(a_shape.label, a_shape.template)
    else:
        base_result = a_shape.label
    if a_shape.instances is not None:
        base_result += _SHAPE_INSTANCES_TEMPLATE.format(a_shape.instances)
    return base_result

def _serialization_of_merged_shape(a_shape):
    result = _heading_of_a_shape(a_shape)
    result += "\n{\n"
    result += _str_constraints_of_a_shape(a_shape)
    result += "\n}\n"
    return result


def _serialize_shapes(shapes, out_stream):
    for a_shape in shapes:
        if a_shape.original_lines is not None:
            out_stream.write("".join(a_shape.original_lines))
        else:
            out_stream.write(_serialization_of_merged_shape(a_shape))
        out_stream.write("\n\n")


def serialize(prefixes, shapes, out_file):
    with open(out_file, "w") as out_stream:
        _serialize_prefixes(prefixes, out_stream)
        _serialize_shapes(shapes, out_stream)