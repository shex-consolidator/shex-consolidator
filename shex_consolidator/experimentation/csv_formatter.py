from shex_consolidator.experimentation.schema_comparator import  RATIO, ABS ,\
    SHAPE_LIKELINESS_KEYS , CONSTRAINT_LIKELINESS_KEYS ,CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS, \
    DIFF_CONST_IN_SCHEMA_1, SHARED_SHAPES, SHAPES_ONLY_IN_1, SHAPES_ONLY_IN_2, explain

from typing import TextIO
# import json

def _write_different_const(out_stream: TextIO, json_stats: dict, separator: str) -> None:
    out_stream.write("CONSTRAINTS ONLY IN SHAPES OF THE SCHEMA 1:\n")
    out_stream.write(separator.join( ("Shape", "predicate", "node constraint") ) + "\n")
    for a_tuple in json_stats[DIFF_CONST_IN_SCHEMA_1]:
        out_stream.write(separator.join(a_tuple) + "\n")

def _write_detailed_stats(out_stream: TextIO, json_stats: dict, separator: str) -> None:
    out_stream.write(separator.join(("Concept", "Absolute value", "Ratio", "Concept explanation"))+"\n")
    for a_key in SHAPE_LIKELINESS_KEYS:
        out_stream.write(separator.join([a_key, str(json_stats[a_key][ABS]), str(json_stats[a_key][RATIO]), explain(a_key)]) + "\n")
    for a_key in CONSTRAINT_LIKELINESS_KEYS:
        out_stream.write(separator.join([a_key, str(json_stats[a_key][ABS]), str(json_stats[a_key][RATIO]), explain(a_key)]) + "\n")
    for a_key in CONSTRAINT_PER_SHAPE_LIKELINESS_KEYS:
        out_stream.write(separator.join([a_key, str(json_stats[a_key][ABS]), str(json_stats[a_key][RATIO]), explain(a_key)]) + "\n")

def _write_main_stats(out_stream: TextIO, json_stats: dict, separator: str) -> None:
    out_stream.write(separator.join((SHARED_SHAPES, str(json_stats[SHARED_SHAPES]))) + "\n")
    out_stream.write(separator.join((SHAPES_ONLY_IN_1, str(json_stats[SHAPES_ONLY_IN_1]))) + "\n")
    out_stream.write(separator.join((SHAPES_ONLY_IN_2, str(json_stats[SHAPES_ONLY_IN_2]))) + "\n")

def _write_title(stream: TextIO, title: str) -> None:
    stream.write(title + "\n")

def _new_file_section(stream: TextIO) -> None:
    stream.write("\n\n")

def json_to_csv (file_path: str, file_title:str, json_stats:dict, separator=";", write_diff_const: bool=True) -> None:
    with open(file_path, "w") as out_stream:
        _write_title(out_stream, file_title)
        _new_file_section(out_stream)
        _write_main_stats(out_stream, json_stats, separator)
        _new_file_section(out_stream)
        _write_detailed_stats(out_stream, json_stats, separator)
        if write_diff_const:
            _new_file_section(out_stream)
            _write_different_const(out_stream, json_stats, separator)