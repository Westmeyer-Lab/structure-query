from lark import Lark, Transformer, Tree
import logging
from logging import Logger
from typing import Any


LOG: Logger = logging.getLogger(__name__)


class BooleanTransformer(Transformer):
    """
    A transformer class for converting parsed boolean expressions into a structured dictionary format.
    This class defines methods for handling 'and', 'or', and variable nodes in the parsed expression tree.
    """

    def _and(self, args: list[Any]) -> dict[str, Any]:
        return {"operator": "and", "nodes": list(args)}

    def _or(self, args: list[Any]) -> dict[str, Any]:
        return {"operator": "or", "nodes": list(args)}

    def _var(self, args: list[Any]) -> str:
        return str(args[0])


GRAMMAR: str = """
    ?start: expr
    ?expr:
        | expr "&" term   -> _and
        | expr "|" term   -> _or
        | term
    ?term: NAME           -> _var
        | "(" expr ")"
    NAME: /[A-z0-9_]+/
    %import common.WS
    %ignore WS
"""
PARSER: Lark = Lark(GRAMMAR, parser="lalr", transformer=BooleanTransformer())


def parse(expression: str) -> Tree:
    """
    Parses a boolean expression string into a structured dictionary format.

    Args:
        expression (str): The boolean expression string to parse.

    Returns:
        Tree: The parsed boolean expression tree.
    """
    LOG.info(f"Parsing expression: {expression}")
    try:
        tree = PARSER.parse(expression)
        LOG.debug(f"Parsed expression tree: {tree}")
        return tree
    except Exception as e:
        LOG.exception("Failed to parse boolean expression.")
        LOG.error(str(e))
        return Tree("error", [])


def transform(node: Tree, parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively transforms a parsed boolean expression node into a structured dictionary format for RCSB search API queries.

    Args:
        node (str|dict): The parsed boolean expression node.
        parameters (dict[str, Any]): The parameters to use for the terminal nodes.

    Returns:
        dict[str, Any]: The structured dictionary representation of the boolean expression node for RCSB search API queries.
    """
    if isinstance(node, str):
        LOG.debug(f"Transforming terminal node: {node}")
        if node not in parameters:
            LOG.error(
                f"Unknown label '{node}' in expression — no matching parameters found."
            )
            raise KeyError(f"Unknown label '{node}' in expression.")
        return {"type": "terminal", "service": "text", "parameters": parameters[node]}
    elif isinstance(node, dict):
        LOG.debug(
            f"Transforming group node: {node} with the operator {node['operator']}"
        )
        return {
            "type": "group",
            "logical_operator": node["operator"],
            "nodes": [transform(subnode, parameters) for subnode in node["nodes"]],
        }
    else:
        LOG.error(f"Invalid node type during transformation: {type(node)}")
        return dict()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    expression = "(A & B) | C"
    parameters = {"A": "val1", "B": "val2", "C": "val3"}
    tree = parse(expression)
    query = transform(tree, parameters)
    print(query)
