from robot.parsing import ModelTransformer
from robot.parsing.model.blocks import TestCase
from robot.parsing.model.statements import TestCaseName

from robot.errors import VariableError

from ast import literal_eval
from copy import deepcopy
import re


def find_orthogonal_identifier(raw):
    """Get valid orthogonal identifier

    $${VARNAME} -> VARNAME

    Args:
        raw: Raw identifier with `$${}`
    
    Returns:
        Variable name if raw identifier is valid, otherwise `None`
    """
    res = re.findall(r"[$]{2}\{([^{}]+)\}", raw)
    return res


def parse_orthogonal_factors(orth_dict, target_keys):
    """Get orthogonal factors those presented in `target_keys`

    orth_dict:
    {
        'ANIMAL': '["cat", "dog"],
        'COLOR': '["red", "green", "blue"]'
    }
    target_keys:
    {'COLOR', 'ANIMAL'}
    ->
    [[('ANIMAL', 'cat'), ('ANIMAL', 'dog')],
     [('COLOR', 'red'), ('COLOR', 'green'), ('COLOR', 'blue')]]

    Args:
        orth_dict: AST `TestCaseSection` node
        target_keys: A set contains orthgonal factors those would be called in cases 
    
    Returns:
        List of tuples, each tuple contains orthogonal factor name and value
    """
    if not orth_dict:
        return []
    orth_pairs = []

    for name in orth_dict:
        if name not in target_keys:
            continue
        args = literal_eval(orth_dict[name])
        gp = []
        for i in args:
            gp.append((name, i))
        orth_pairs.append(gp)
    return orth_pairs


def generate_orthogonal_chunks(orth_dict, target_keys):

    def _product(args, **kwds):
        """Generate orthogonal matrix

        _product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        _product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        """
        pools = list(map(tuple, args)) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x + [y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

    serialized_ofs = parse_orthogonal_factors(orth_dict, target_keys)
    return [x for x in _product(serialized_ofs)]


def get_template_cases(node):
    raw = []
    for case in node.body:
        name = case.header.tokens[0]
        raw.append((name, case.body))
    return raw


class OrthogonalTestGenerator(ModelTransformer):

    def __init__(self):
        self._orth_dict = {}

    def visit_OrthogonalSection(self, node):
        for factor in node.body:
            self._orth_dict[factor.tokens[0].value] = factor.tokens[1].value
        return self.generic_visit(node)

    def visit_TestCaseSection(self, node):
        template_cases = get_template_cases(node)

        for name, body in template_cases:
            count = 1
            case_name = name.value

            orth_vars = set()
            get_orthogonal_variable(body, orth_vars)
            check_orthogonal_variables(orth_vars, self._orth_dict)
            vars_for_new_cases = generate_orthogonal_chunks(
                self._orth_dict, orth_vars)

            if not vars_for_new_cases[0]:
                new_body = deepcopy(body)
                new_case = TestCase(
                    header=TestCaseName.from_params(case_name),
                    body=new_body,
                )
                node.body.insert(0, new_case)
                continue

            # Each chunk generates a new sub case
            for chunk in vars_for_new_cases:
                new_body = deepcopy(body)
                pairs = {}
                for kv in chunk:
                    pairs[kv[0]] = kv[1]

                new_case_name = replace_orthogonal_identifier(
                    new_body, pairs, count, case_name)
                new_case = TestCase(
                    header=TestCaseName.from_params(new_case_name),
                    body=new_body,
                )
                node.body.insert(0, new_case)
                count += 1

        for _ in range(len(template_cases)):
            node.body.pop()
        node.body.reverse()

        return self.generic_visit(node)


def check_orthogonal_variables(var_list, orth_dict):
    for var in var_list:
        if not var in orth_dict:
            raise VariableError(f"Undefined orthogonal variable: $${{{var}}}")


def get_orthogonal_variable(body, orth_vars):
    if isinstance(body, list):
        for item in body:
            get_orthogonal_variable(item, orth_vars)
    if hasattr(body, "body"):
        get_orthogonal_variable(body.body, orth_vars)
    if hasattr(body, "orelse"):
        get_orthogonal_variable(body.orelse, orth_vars)
    if hasattr(body, "header"):
        get_orthogonal_variable(body.header, orth_vars)
    if hasattr(body, "tokens"):
        for token in body:
            oi_list = find_orthogonal_identifier(token.value)
        if oi_list:
            [orth_vars.add(x) for x in oi_list]


def replace_orthogonal_identifier(body, pairs, count, raw_name):
    case_name = deepcopy(raw_name)
    if isinstance(body, list):
        for item in body:
            case_name = replace_orthogonal_identifier(item, pairs, count,
                                                      raw_name)
    if hasattr(body, "body"):
        case_name = replace_orthogonal_identifier(body.body, pairs, count,
                                                  raw_name)
    if hasattr(body, "orelse"):
        case_name = replace_orthogonal_identifier(body.orelse, pairs, count,
                                                  raw_name)
    if hasattr(body, "header"):
        case_name = replace_orthogonal_identifier(body.header, pairs, count,
                                                  raw_name)
    if hasattr(body, "tokens"):
        subcase_ident = "-".join([x for x in pairs.values()])
        case_name = f'[{count}].{raw_name}-{subcase_ident}'
        for token in body:
            oi_list = find_orthogonal_identifier(token.value)
            if oi_list:
                for key in pairs:
                    token.value = token.value.replace(f"$${{{key}}}",
                                                      pairs[key])
    return case_name
