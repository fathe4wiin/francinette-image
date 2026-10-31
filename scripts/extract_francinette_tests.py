#!/usr/bin/env python3
"""Pull every francinette test case into francinette-tests.json.

One flat list. Same keys on every case. A TUI loads it with json.load
and filters on project, suite, function, part, or kind.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "francinette" / "tests"
OUT = ROOT / "francinette-tests.json"

PART1 = {
    "isalpha", "isdigit", "isalnum", "isascii", "isprint", "strlen", "memset",
    "bzero", "memcpy", "memmove", "strlcpy", "strlcat", "toupper", "tolower",
    "strchr", "strrchr", "strncmp", "memchr", "memcmp", "strnstr", "atoi",
    "calloc", "strdup",
}
PART2 = {
    "substr", "strjoin", "strtrim", "split", "itoa", "strmapi", "striteri",
    "putchar_fd", "putstr_fd", "putendl_fd", "putnbr_fd",
}
BONUS = {
    "lstnew", "lstadd_front", "lstsize", "lstlast", "lstadd_back", "lstdelone",
    "lstclear", "lstiter", "lstmap",
}
STDERR_ODD = {"ft_putchar_fd", "ft_putstr_fd", "ft_putendl_fd", "ft_putnbr_fd"}
DROP_PARAMS = {"ms", "fd"}
PRINTF_BONUS_CATS = {"+", "0", "-", ".", "#", "space"}

CASES = []
ERRORS = []
SEQ = {}


def rel(path):
    return path.relative_to(ROOT).as_posix()


def line_of(text, index):
    return text.count("\n", 0, index) + 1


def libft_part(function):
    base = function[3:] if function.startswith("ft_") else function
    if base in PART1:
        return "part1"
    if base in PART2:
        return "part2"
    if base in BONUS:
        return "bonus"
    return "extra"


def add(project, suite, function, part, index, kind, call, args, expected, source, line, **extra):
    key = (project, suite, function)
    SEQ[key] = SEQ.get(key, 0) + 1
    case = {
        "id": f"{project}/{suite}/{function}/{SEQ[key]:04d}",
        "project": project,
        "suite": suite,
        "function": function,
        "part": part,
        "index": str(index),
        "kind": kind,
        "call": call,
        "args": args,
        "expected": expected,
        "source": source,
        "line": line,
        "bonus": part == "bonus" or bool(extra.pop("bonus", False)),
    }
    for name, value in extra.items():
        if name == "input":
            case["input"] = value
            continue
        if value is None or value == "" or value == []:
            continue
        case[name] = value
    CASES.append(case)
    return case


def skip_string(text, i):
    quote = text[i]
    i += 1
    n = len(text)
    while i < n:
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == quote:
            return i + 1
        i += 1
    return n


def decode_c_string(token):
    out = []
    i = 1
    end = len(token) - 1
    while i < end:
        if token[i] != "\\":
            out.append(token[i])
            i += 1
            continue
        if i + 1 >= end:
            break
        nxt = token[i + 1]
        simple = {
            "n": "\n", "t": "\t", "r": "\r", "v": "\v", "f": "\f",
            "\\": "\\", '"': '"', "'": "'", "a": "\a", "e": "\x1b",
        }
        if nxt in simple:
            out.append(simple[nxt])
            i += 2
            continue
        if nxt in "01234567":
            j = i + 1
            while j < end and j < i + 4 and token[j] in "01234567":
                j += 1
            out.append(chr(int(token[i + 1:j], 8) % 256))
            i = j
            continue
        if nxt == "x":
            j = i + 2
            while j < end and token[j] in "0123456789abcdefABCDEF":
                j += 1
            out.append(chr(int(token[i + 2:j] or "0", 16) % 256))
            i = j
            continue
        out.append(nxt)
        i += 2
    return "".join(out)


def decode_c_char(token):
    inner = token[1:-1]
    return decode_c_string('"' + inner + '"')


def read_balanced(text, i, open_ch, close_ch):
    if i >= len(text) or text[i] != open_ch:
        raise ValueError(f"expected {open_ch} at {i}")
    start = i + 1
    depth = 1
    i += 1
    n = len(text)
    while i < n:
        if text.startswith("//", i):
            nl = text.find("\n", i)
            i = n if nl < 0 else nl
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        ch = text[i]
        if ch in "\"'":
            i = skip_string(text, i)
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i], i + 1
        i += 1
    raise ValueError(f"unbalanced {open_ch}")


def split_args(src):
    parts = []
    buf = []
    depth = 0
    i = 0
    n = len(src)
    while i < n:
        if src.startswith("//", i):
            nl = src.find("\n", i)
            i = n if nl < 0 else nl
            continue
        if src.startswith("/*", i):
            end = src.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        ch = src[i]
        if ch in "\"'":
            j = skip_string(src, i)
            buf.append(src[i:j])
            i = j
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def parse_atom(token):
    token = token.strip()
    if token in {"NULL", "null", "nullptr"}:
        return {"type": "null", "value": None}
    if token.startswith('"'):
        value = []
        i = 0
        while i < len(token) and token[i] == '"':
            j = skip_string(token, i)
            value.append(decode_c_string(token[i:j]))
            i = j
            while i < len(token) and token[i] in " \t\n":
                i += 1
        if i >= len(token):
            return {"type": "str", "value": "".join(value)}
    if token.startswith("'") and token.endswith("'") and len(token) >= 2:
        try:
            return {"type": "char", "value": decode_c_char(token)}
        except (ValueError, IndexError):
            pass
    if re.fullmatch(r"-?(?:0x[0-9A-Fa-f]+|\d+)", token):
        if "x" in token or "X" in token:
            return {"type": "int", "value": str(int(token, 16))}
        return {"type": "int", "value": token}
    return {"type": "expr", "value": token}


def parse_arg_list(src):
    return [parse_atom(part) for part in split_args(src)]


def render(atom):
    kind = atom["type"]
    value = atom["value"]
    if kind == "null":
        return "NULL"
    if kind == "str":
        return json.dumps(value, ensure_ascii=False)
    if kind == "char":
        shown = (
            value.replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\t", "\\t")
            .replace("\r", "\\r")
            .replace("\v", "\\v")
            .replace("\f", "\\f")
            .replace("\0", "\\0")
        )
        return f"'{shown}'"
    return str(value)


def call_text(function, args):
    return function + "(" + ", ".join(render(arg) for arg in args) + ")"


def skip_ws(text, i):
    n = len(text)
    while i < n:
        if text.startswith("//", i):
            nl = text.find("\n", i)
            i = n if nl < 0 else nl + 1
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        if text[i] in " \t\r\n":
            i += 1
            continue
        break
    return i


def read_ident(text, i):
    j = i
    while j < len(text) and (text[j].isalnum() or text[j] == "_"):
        j += 1
    return text[i:j], j


def preprocessor_line(text, i):
    end = text.find("\n", i)
    if end < 0:
        end = len(text)
    return text[i:end].strip(), end


def handle_pp(line, stack):
    parent = stack[-1]
    if line.startswith("#if 0"):
        stack.append({"emit": False, "bonus": parent["bonus"], "cond": False})
    elif "FT_PRINTF_TEST_BONUS" in line and line.startswith("#if"):
        stack.append({"emit": parent["emit"], "bonus": True, "cond": True})
    elif line.startswith("#ifndef") or line.startswith("#ifdef") or line.startswith("#if"):
        stack.append({"emit": parent["emit"], "bonus": parent["bonus"], "cond": True})
    elif line.startswith("#else") or line.startswith("#elif"):
        frame = stack.pop() if len(stack) > 1 else parent
        base = stack[-1]
        cond = not frame["cond"]
        stack.append({
            "emit": base["emit"] and cond,
            "bonus": base["bonus"],
            "cond": cond,
        })
    elif line.startswith("#endif") and len(stack) > 1:
        stack.pop()


class Hit:
    def __init__(self, name, args_src, start, end, line, bonus):
        self.name = name
        self.args_src = args_src
        self.start = start
        self.end = end
        self.line = line
        self.bonus = bonus


def walk_calls(text, wanted):
    hits = []
    i = 0
    n = len(text)
    line = 1
    stack = [{"emit": True, "bonus": False, "cond": True}]
    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            i += 1
            continue
        if ch == "#":
            prev = i - 1
            while prev >= 0 and text[prev] in " \t":
                prev -= 1
            if prev < 0 or text[prev] == "\n":
                directive, end = preprocessor_line(text, i)
                handle_pp(directive, stack)
                newlines = text.count("\n", i, end)
                line += newlines
                i = end
                continue
        if text.startswith("//", i):
            nl = text.find("\n", i)
            i = n if nl < 0 else nl
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end < 0:
                break
            line += text.count("\n", i, end)
            i = end + 2
            continue
        if ch in "\"'":
            end = skip_string(text, i)
            line += text.count("\n", i, end)
            i = end
            continue
        if ch.isalpha() or ch == "_":
            name, after = read_ident(text, i)
            look = skip_ws(text, after)
            if look < n and text[look] == "(" and wanted(name):
                try:
                    args_src, end = read_balanced(text, look, "(", ")")
                except ValueError:
                    i += 1
                    continue
                if stack[-1]["emit"]:
                    hits.append(Hit(name, args_src, i, end, line, stack[-1]["bonus"]))
            i = after
            continue
        i += 1
    return hits


def comment_index(text, start):
    window = text[max(0, start - 80):start]
    match = re.search(r"/\*\s*(\d+)\s*\*/\s*$", window)
    if match:
        return match.group(1)
    return None


def find_function(text, name):
    pattern = re.compile(r"\b" + re.escape(name) + r"\s*\(")
    for match in pattern.finditer(text):
        paren = match.end() - 1
        try:
            params, after = read_balanced(text, paren, "(", ")")
        except ValueError:
            continue
        j = skip_ws(text, after)
        if j >= len(text) or text[j] != "{":
            continue
        try:
            body, end = read_balanced(text, j, "{", "}")
        except ValueError:
            continue
        return params, body, line_of(text, match.start()), match.start(), end
    return None


def param_names(param_src):
    names = []
    for part in split_args(param_src):
        pointer = re.search(r"\(\s*\*\s*(\w+)\s*\)", part)
        if pointer:
            names.append(pointer.group(1))
            continue
        word = re.search(r"(\w+)\s*$", part.strip())
        if word and word.group(1) not in {"void", "int", "char", "size_t", "unsigned"}:
            names.append(word.group(1))
    return names


def functions_in(text):
    found = {}
    for match in re.finditer(r"\b((?:static\s+)?int\s+)(\w+)\s*\(", text):
        name = match.group(2)
        got = find_function(text, name)
        if got and name not in found:
            params, body, line, _start, _end = got
            found[name] = (params, body, line)
    return found


def int_token(token):
    token = token.strip()
    if re.fullmatch(r"0x[0-9A-Fa-f]+|\d+", token):
        return int(token, 16) if token.lower().startswith("0x") else int(token)
    return None


def eval_math(token, var, value):
    token = token.strip()
    if token == var:
        return value
    left = re.fullmatch(rf"(\d+)\s*\+\s*{re.escape(var)}", token)
    if left:
        return int(left.group(1)) + value
    right = re.fullmatch(rf"{re.escape(var)}\s*\+\s*(\d+)", token)
    if right:
        return value + int(right.group(1))
    plain = int_token(token)
    return plain


def for_header(header):
    match = re.fullmatch(
        r"int\s+(\w+)\s*=\s*(0x[0-9A-Fa-f]+|\d+)\s*;\s*(\w+)\s*(<=|<)\s*(0x[0-9A-Fa-f]+|\d+)\s*;\s*(\w+)\s*\+\+\s*",
        header.strip(),
    )
    if not match:
        return None
    var, start, var2, op, end, var3 = match.groups()
    if var != var2 or var != var3:
        return None
    start_n = int_token(start)
    end_n = int_token(end)
    if start_n is None or end_n is None:
        return None
    last = end_n if op == "<=" else end_n - 1
    if last < start_n or last - start_n > 512:
        return None
    return var, start_n, last


def sprintf_char_map(body, var):
    match = re.search(
        r'sprintf\s*\(\s*(\w+)\s*,\s*"%c %i"\s*,\s*' + re.escape(var) + r"\s*,\s*" + re.escape(var) + r"\s*\+\s*1\s*\)",
        body,
    )
    if not match:
        return None
    buf = match.group(1)

    def build(value):
        return chr(value % 256) + " " + str(value + 1)

    return buf, build


def atom_from_token(token, var, value, buffers):
    token = token.strip()
    if token in buffers:
        return {"type": "str", "value": buffers[token](value)}
    if "(" in token or "rand" in token:
        return None
    number = eval_math(token, var, value)
    if number is not None and (token == var or "+" in token or int_token(token) is not None):
        if token == var or "+" in token or re.fullmatch(r"-?\d+|0x[0-9A-Fa-f]+", token):
            return {"type": "int", "value": str(number)}
    return parse_atom(token)


def read_statement(text, i):
    start = i
    depth = 0
    n = len(text)
    while i < n:
        if text.startswith("//", i):
            nl = text.find("\n", i)
            i = n if nl < 0 else nl
            continue
        if text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        ch = text[i]
        if ch in "\"'":
            i = skip_string(text, i)
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch == ";" and depth == 0:
            return text[start:i + 1], i + 1
        i += 1
    return text[start:], n


def iter_items(body):
    i = 0
    n = len(body)
    while i < n:
        i = skip_ws(body, i)
        if i >= n:
            break
        name, after = read_ident(body, i)
        if name == "for":
            paren = skip_ws(body, after)
            header, after_paren = read_balanced(body, paren, "(", ")")
            nxt = skip_ws(body, after_paren)
            if nxt < n and body[nxt] == "{":
                inner, end = read_balanced(body, nxt, "{", "}")
            else:
                inner, end = read_statement(body, nxt)
            yield ("for", i, header, inner, end)
            i = end
            continue
        statement, end = read_statement(body, i)
        yield ("stmt", i, statement, None, end)
        i = end


def init_list(args_src):
    atoms = parse_arg_list(args_src)
    values = []
    for atom in atoms[1:]:
        if atom["type"] == "null":
            break
        if atom["type"] == "str":
            values.append(atom["value"])
    return values


def update_arrays(statement, arrays):
    match = re.search(r"(\w+)\s*=\s*init_str_array\s*\(", statement)
    if not match:
        return
    paren = statement.find("(", match.end() - 1)
    try:
        inner, _end = read_balanced(statement, paren, "(", ")")
    except ValueError:
        return
    arrays[match.group(1)] = init_list(inner)


def string_bindings(body):
    found = {}
    for match in re.finditer(
        r"\b(\w+)\s*(?:\[\s*\])?\s*=\s*(\"(?:\\.|[^\"\\])*\")",
        body,
    ):
        found[match.group(1)] = {"type": "str", "value": decode_c_string(match.group(2))}
    for match in re.finditer(
        r"strcpy\s*\(\s*(\w+)\s*,\s*(\"(?:\\.|[^\"\\])*\")\s*\)",
        body,
    ):
        found[match.group(1)] = {"type": "str", "value": decode_c_string(match.group(2))}
    return found


def resolve_atom(atom, arrays, names=None):
    names = names or {}
    if atom["type"] == "expr" and atom["value"] in names:
        return names[atom["value"]]
    if atom["type"] == "expr" and atom["value"] in arrays:
        return {"type": "lines", "value": list(arrays[atom["value"]])}
    return atom


def update_names(statement, names):
    match = re.search(r'sprintf\s*\(\s*(\w+)\s*,\s*"%i"\s*,\s*([A-Za-z_]\w*)\s*\)', statement)
    if match:
        names[match.group(1)] = {"type": "expr", "value": match.group(2)}
    match = re.search(r"(\w+)\s*\[\s*0\s*\]\s*=\s*EOF\s*;", statement)
    if match:
        names[match.group(1)] = {"type": "expr", "value": "EOF"}


def expected_object(atom):
    if atom is None:
        return None
    if atom["type"] == "lines":
        return {"type": "lines", "value": atom["value"]}
    if atom["type"] == "str":
        return {"type": "str", "value": atom["value"]}
    if atom["type"] == "char":
        return {"type": "char", "value": atom["value"]}
    if atom["type"] == "int":
        return {"type": "int", "value": atom["value"]}
    if atom["type"] == "null":
        return {"type": "null", "value": None}
    return {"type": "expr", "value": atom["value"]}


LIMITS = {"INT_MAX": "2147483647", "INT_MIN": "-2147483648"}


def put_expected(function, args):
    if len(args) != 1:
        return None
    arg = args[0]
    if function == "ft_putstr_fd" and arg["type"] == "str":
        return {"type": "stdout", "value": arg["value"]}
    if function == "ft_putendl_fd" and arg["type"] == "str":
        return {"type": "stdout", "value": arg["value"] + "\n"}
    if function == "ft_putchar_fd" and arg["type"] == "char":
        return {"type": "stdout", "value": arg["value"]}
    if function == "ft_putnbr_fd" and arg["type"] == "int":
        return {"type": "stdout", "value": arg["value"] + "\n"}
    if function == "ft_putnbr_fd" and arg["type"] == "expr" and arg["value"] in LIMITS:
        return {"type": "stdout", "value": LIMITS[arg["value"]] + "\n"}
    return None


def emit_helper_call(function, hit, helpers, arrays, source, line, names=None):
    name = hit.name
    atoms = [resolve_atom(atom, arrays, names) for atom in parse_arg_list(hit.args_src)]
    if name.startswith(("libc_crash_",)):
        add(
            "libft", "fsoares", function, libft_part(function), "crash", "crash",
            name + "()", [], None,             source, line,
            notes="Must match libc on the inputs where libc itself crashes.",
        )
        return
    if name.startswith("part2_guard_"):
        add(
            "libft", "fsoares", function, libft_part(function), "guard", "guard",
            name + "()", [], None, source, line,
            notes="Null-pointer and allocation guard.",
        )
        return
    if name == "set_signature_tn":
        label = atoms[1]["value"] if len(atoms) > 1 and atoms[1]["type"] == "str" else name
        index = atoms[0]["value"] if atoms and atoms[0]["type"] == "int" else "extra"
        shown = []
        for atom in atoms[2:]:
            if atom["type"] == "expr" and (
                atom["value"] == "fd" or atom["value"].startswith("escape_")
            ):
                continue
            shown.append(atom)
        if isinstance(label, str) and "ptr" in label and shown and shown[0]["type"] == "int":
            shown = [{"type": "expr", "value": "ptr"}] + shown
        expected = put_expected(function, shown)
        add(
            "libft", "fsoares", function, libft_part(function), index, "compare_libc",
            call_text(function, shown) if shown else label,
            shown, expected, source, line,
            notes="Run through null_null_check." if function.startswith("ft_put") else None,
        )
        return
    params = []
    if name in helpers:
        params = param_names(helpers[name][0])
    kept = []
    expected = None
    index = atoms[0]["value"] if atoms else "?"
    usable = params and len(params) == len(atoms)
    chosen = atoms[1:] if not usable else []
    if usable:
        index = atoms[0]["value"] if atoms[0]["type"] in {"int", "expr"} else atoms[0]["value"]
        for param, atom in zip(params, atoms):
            if param in {"test_number", "test_n", "test_num"}:
                index = atom["value"]
                continue
            if param == "expected":
                expected = expected_object(atom)
                continue
            if param in DROP_PARAMS or param.endswith("_std"):
                continue
            kept.append(atom)
    else:
        kept = atoms[1:]
    ft_name = "ft_" + function.split("ft_")[-1]
    if not function.startswith("ft_"):
        ft_name = "ft_" + function
    written = put_expected(ft_name, kept)
    if written and expected is None:
        expected = written
    note = None
    if any(atom["type"] == "expr" and atom["value"] == "EOF" for atom in kept):
        note = "String of one byte. That byte is EOF, then NUL."
    add(
        "libft", "fsoares", ft_name, libft_part(ft_name), index, "compare_libc",
        call_text(ft_name, kept), kept, expected, source, line, notes=note,
    )


def walk_fsoares_body(body, function, helpers, arrays, source, base_line, names=None):
    ft_name = function if function.startswith("ft_") else "ft_" + function
    if names is None:
        names = {}
    for kind, start, first, inner, _end in iter_items(body):
        stmt_line = base_line + body[:start].count("\n")
        if kind == "stmt":
            update_arrays(first, arrays)
            update_names(first, names)
            hits = walk_calls(first, lambda name: (
                name.startswith(("single_test_", "test_single_", "compare_", "libc_crash_", "part2_guard_"))
                or name == "set_signature_tn"
                or (name in helpers and "set_signature_tn" in helpers[name][1])
            ))
            for hit in hits:
                if (
                    hit.name in helpers
                    and hit.name.startswith("test_")
                    and not hit.name.startswith(("test_single_",))
                    and "set_signature_tn" in helpers[hit.name][1]
                ):
                    walk_fsoares_body(
                        helpers[hit.name][1], function, helpers, arrays, source,
                        helpers[hit.name][2], names,
                    )
                    continue
                emit_helper_call(ft_name, hit, helpers, arrays, source, stmt_line, names)
            continue
        header = for_header(first)
        raw = "for (" + first.strip() + ") " + re.sub(r"\s+", " ", inner).strip()
        mapped = sprintf_char_map(inner, header[0]) if header else None
        expandable = header is not None and "rand" not in inner and ("sprintf" not in inner or mapped)
        calls = walk_calls(inner, lambda name: name.startswith(("single_test_", "test_single_", "compare_")))
        if not expandable or len(calls) != 1:
            add(
                "libft", "fsoares", ft_name, libft_part(ft_name), "generated", "generated",
                raw[:500], [], None, source, stmt_line,
                generator=raw[:500],
                notes="Loop inputs are computed at runtime. Not expanded.",
            )
            continue
        var, start_n, last_n = header
        buffers = {mapped[0]: mapped[1]} if mapped else {}
        call = calls[0]
        tokens = split_args(call.args_src)
        if any(atom_from_token(token, var, start_n, buffers) is None for token in tokens):
            add(
                "libft", "fsoares", ft_name, libft_part(ft_name), "generated", "generated",
                raw[:500], [], None, source, stmt_line, generator=raw[:500],
                notes="Loop inputs are computed at runtime. Not expanded.",
            )
            continue
        for value in range(start_n, last_n + 1):
            built = [atom_from_token(token, var, value, buffers) for token in tokens]
            emit_expanded(ft_name, call.name, built, helpers, source, stmt_line)


def emit_expanded(ft_name, helper_name, atoms, helpers, source, line):
    params = param_names(helpers[helper_name][0]) if helper_name in helpers else []
    kept = []
    expected = None
    index = atoms[0]["value"] if atoms else "?"
    if params and len(params) == len(atoms):
        for param, atom in zip(params, atoms):
            if param in {"test_number", "test_n", "test_num"}:
                index = atom["value"]
                continue
            if param == "expected":
                expected = expected_object(atom)
                continue
            if param in DROP_PARAMS or param.endswith("_std"):
                continue
            kept.append(atom)
    else:
        kept = atoms[1:]
        if atoms:
            index = atoms[0]["value"]
    written = put_expected(ft_name, kept)
    if written and expected is None:
        expected = written
    add(
        "libft", "fsoares", ft_name, libft_part(ft_name), index, "compare_libc",
        call_text(ft_name, kept), kept, expected, source, line,
    )


def extract_fsoares():
    folder = TESTS / "libft" / "fsoares"
    for path in sorted(folder.glob("test_*.c")):
        text = path.read_text(errors="replace")
        stem = path.stem.removeprefix("test_")
        helpers = functions_in(text)
        target = "test_" + stem
        if target not in helpers:
            ERRORS.append(f"no {target} in {rel(path)}")
            continue
        _params, body, line = helpers[target]
        walk_fsoares_body(body, "ft_" + stem, helpers, {}, rel(path), line)


def split_compare(expr):
    depth = 0
    i = 0
    n = len(expr)
    while i < n - 1:
        if expr.startswith("//", i):
            nl = expr.find("\n", i)
            i = n if nl < 0 else nl
            continue
        ch = expr[i]
        if ch in "\"'":
            i = skip_string(expr, i)
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif depth == 0 and expr.startswith("==", i):
            return expr[:i].strip(), expr[i + 2:].strip()
        i += 1
    return None


def tripouille_case(expr):
    flat = re.sub(r"\s+", " ", expr).strip()
    negated = flat.startswith("!")
    body = flat[1:].strip() if negated else flat
    match = re.match(r"(ft_\w+)\s*\(", body)
    if not match:
        return flat, [], None
    paren = body.find("(", match.end() - 1)
    try:
        inner, after = read_balanced(body, paren, "(", ")")
    except ValueError:
        return flat, [], None
    rest = body[after:].strip()
    args = parse_arg_list(inner)
    if rest == "":
        expected = {"type": "bool", "value": "false" if negated else "true"}
        return call_text(match.group(1), args), args, expected
    compared = split_compare(rest if rest.startswith("==") else "==" + rest if False else rest)
    if rest.startswith("=="):
        right = parse_atom(rest[2:].strip())
        return call_text(match.group(1), args), args, expected_object(right)
    return flat, [], None


def extract_tripouille():
    folder = TESTS / "libft" / "Tripouille" / "tests"
    for path in sorted(folder.glob("ft_*_test.cpp")):
        text = path.read_text(errors="replace")
        function = path.name[: -len("_test.cpp")]
        has_e = "char escape[]" in text or "string e(" in text
        for hit in walk_calls(text, lambda name: name in {"check", "mcheck"}):
            index = comment_index(text, hit.start) or "?"
            call, args, expected = tripouille_case(hit.args_src)
            notes = None
            if has_e and "e" in hit.args_src:
                notes = 'Identifier e is the string "\\t\\n\\v\\f\\r".'
            add(
                "libft", "Tripouille", function, libft_part(function), index, "expression",
                call, args, expected, rel(path), hit.line, notes=notes,
            )


def branch_body(text, after_cond):
    i = skip_ws(text, after_cond)
    if i < len(text) and text[i] == "{":
        inner, end = read_balanced(text, i, "{", "}")
        return inner, end
    return read_statement(text, i)


def range_summary(function, body):
    flat = re.sub(r"\s+", " ", body)
    match = re.search(
        r"(\w+)\s*=\s*([^;]+);\s*while\s*\(\s*\1\s*(<=|<)\s*([^)]+)\)",
        flat,
    )
    if not match:
        return None
    var, start, op, end = match.groups()
    span = f"{start.strip()}..{end.strip()}"
    if op == "<":
        span += " exclusive"
    return f"{function}({var}) for {var} in {span}"


def load_output(path):
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def extract_war_machine():
    root = TESTS / "libft" / "war-machine" / "tests"
    cond = re.compile(
        r"(?:else\s+)?if\s*\(\s*"
        r"(?:"
        r"\(\s*arg\s*=\s*atoi\s*\(\s*argv\s*\[\s*1\s*\]\s*\)\s*\)\s*=="
        r"|arg\s*=="
        r"|atoi\s*\(\s*argv\s*\[\s*1\s*\]\s*\)\s*=="
        r")\s*(\d+)\s*\)"
    )
    folders = [
        "Part1_functions", "Part2_functions", "Bonus_functions", "Additional_functions",
    ]
    for folder in folders:
        part = {
            "Part1_functions": "part1",
            "Part2_functions": "part2",
            "Bonus_functions": "bonus",
            "Additional_functions": "additional",
        }[folder]
        for main in sorted((root / folder).glob("*/main.c")):
            function = main.parent.name
            text = main.read_text(errors="replace")
            seen = set()
            for match in cond.finditer(text):
                number = int(match.group(1))
                seen.add(number)
                try:
                    body, _end = branch_body(text, match.end())
                except ValueError as exc:
                    ERRORS.append(f"{rel(main)} case {number}: {exc}")
                    continue
                hits = walk_calls(body, lambda name, function=function: name == function)
                bindings = string_bindings(body)
                args = []
                if hits:
                    args = []
                    for atom in parse_arg_list(hits[0].args_src):
                        if atom["type"] == "expr" and atom["value"] in bindings:
                            args.append(bindings[atom["value"]])
                        else:
                            args.append(atom)
                    call = range_summary(function, body) or call_text(function, args)
                else:
                    literals = [atom for atom in bindings.values()]
                    args = literals
                    call = re.sub(r"\s+", " ", body).strip()[:300]
                out_path = main.parent / f"test{number:02d}.output"
                stream = "stderr" if function in STDERR_ODD and number % 2 == 1 else "stdout"
                if out_path.exists():
                    expected = {"type": stream, "value": load_output(out_path)}
                    notes = None
                else:
                    expected = None
                    notes = "No .output file for this case."
                extra = {}
                if "\n" in body and "while" in body or "for" in body:
                    extra["body"] = body.strip()
                add(
                    "libft", "war-machine", function, part, number, "stdout",
                    call, args, expected, rel(main), line_of(text, match.start()),
                    stream=stream, notes=notes, **extra,
                )
            for out_path in sorted(main.parent.glob("test*.output")):
                number = int(out_path.stem.removeprefix("test"))
                if number not in seen:
                    stream = "stderr" if function in STDERR_ODD and number % 2 == 1 else "stdout"
                    add(
                        "libft", "war-machine", function, part, number, "stdout",
                        f"{function} case {number}", [],
                        {"type": stream, "value": load_output(out_path)},
                        rel(main), 1, stream=stream,
                        notes="Output file has no matching if-branch in main.c.",
                    )


def extract_alelievr():
    path = TESTS / "libft" / "alelievr" / "src" / "test_functions.c"
    text = path.read_text(errors="replace")
    registrars = []
    for match in re.finditer(r"\bvoid\s+(test_ft_\w+)\s*\(", text):
        got = find_function(text, match.group(1))
        if not got:
            continue
        params, body, line, _start, _end = got
        if "*" in params:
            continue
        names = re.findall(r"add_fun_subtest\(\s*(test_ft_\w+)\s*\)", body)
        if names:
            registrars.append((match.group(1), names))
    defs = {}
    for match in re.finditer(r"\bvoid\s+(test_ft_\w+)\s*\(", text):
        name = match.group(1)
        if name in defs:
            continue
        got = find_function(text, name)
        if not got:
            continue
        params, body, line, _start, _end = got
        if "*" not in params:
            continue
        defs[name] = (body, line)
    for registrar, names in registrars:
        function = registrar.removeprefix("test_")
        for name in names:
            if name not in defs:
                ERRORS.append(f"missing subtest {name}")
                continue
            body, line = defs[name]
            explained = re.search(r'SET_EXPLANATION\(\s*"((?:\\.|[^"\\])*)"', body)
            if explained:
                call = decode_c_string('"' + explained.group(1) + '"')
            else:
                call = name.removeprefix(registrar + "_") or name
            kind = "speed" if "SANDBOX_SPEED" in body else "sandbox"
            index = name.removeprefix(registrar + "_") or name
            add(
                "libft", "alelievr", function, libft_part(function), index, kind,
                call, [], None, rel(path), line, body=body.strip(),
            )


def extract_hardcore():
    folder = TESTS / "libft" / "alelievr" / "hardcore-mode"
    for path in sorted(folder.glob("test-*.c")):
        if path.name in {"test-utils.c", "test-init.c"}:
            continue
        text = path.read_text(errors="replace")
        function = "ft_" + path.stem.removeprefix("test-")
        match = re.search(r"\b(test_main_\w+)\s*\(", text)
        body = None
        line = 1
        if match:
            got = find_function(text, match.group(1))
            if got:
                _params, body, line, _start, _end = got
        add(
            "libft", "alelievr-hardcore", function, libft_part(function), "fuzz",
            "fuzzer", f"runtime fuzz of {function}", [], None, rel(path), line,
            generator="Alignment loops plus do_random_tests(). Inputs are built at runtime.",
            body=None if body is None else body.strip(),
        )


def printf_category(path):
    stem = path.stem.removesuffix("_test")
    return {
        "upperx": "X",
        "percent": "%",
        "minus": "-",
        "sharp": "#",
        "dot": ".",
        "space": "space",
        "+": "+",
        "0": "0",
    }.get(stem, stem)


def function_spans(text):
    spans = []
    for match in re.finditer(r"\b(?:void|int)\s+(\w+)\s*\(", text):
        got = find_function(text, match.group(1))
        if not got:
            continue
        _params, _body, _line, start, end = got
        spans.append((match.group(1), start, end))
    return spans


def enclosing(spans, pos):
    for name, start, end in spans:
        if start <= pos < end:
            return name
    return None


def bonus_only_functions():
    path = TESTS / "printf" / "ft_printf_test" / "main.c"
    text = path.read_text(errors="replace")
    flags = {}
    for hit in walk_calls(text, lambda name: name.startswith("test_") or name in {"generated_test", "saved_test"}):
        flags.setdefault(hit.name, set()).add(hit.bonus)
    return {name for name, used in flags.items() if used == {True}}


def extract_printf_tester():
    folder = TESTS / "printf" / "printfTester" / "tests"
    for path in sorted(folder.glob("*_test.cpp")):
        text = path.read_text(errors="replace")
        category = printf_category(path)
        part = "bonus" if category in PRINTF_BONUS_CATS else "mandatory"
        for hit in walk_calls(text, lambda name: name == "TEST"):
            parts = split_args(hit.args_src)
            index = parts[0].strip() if parts else "?"
            printed = parts[1].strip() if len(parts) > 1 else ""
            args = []
            if printed.startswith("print"):
                paren = printed.find("(")
                try:
                    inner, _end = read_balanced(printed, paren, "(", ")")
                    args = parse_arg_list(inner)
                except ValueError:
                    args = []
            call = call_text("ft_printf", args) if args else "ft_printf(" + printed + ")"
            add(
                "ft_printf", "printfTester", "ft_printf", part, index, "compare_libc",
                call, args, None, rel(path), hit.line, group=category,
                notes="Stdout and return value must match printf.",
            )


def extract_ft_printf_test(bonus_fns):
    folder = TESTS / "printf" / "ft_printf_test"
    files = sorted((folder / "tests").glob("*.c")) + [folder / "generated.c", folder / "saved_tests.c", folder / "main.c"]
    for path in files:
        if not path.exists():
            continue
        text = path.read_text(errors="replace")
        spans = function_spans(text)
        counts = {}
        for hit in walk_calls(text, lambda name: name == "ASSERT_PRINTF"):
            group = enclosing(spans, hit.start) or path.stem
            counts[group] = counts.get(group, 0) + 1
            bonus = hit.bonus or group in bonus_fns
            part = "bonus" if bonus else "mandatory"
            args = parse_arg_list(hit.args_src)
            raw = re.sub(r"\s+", " ", hit.args_src).strip()
            add(
                "ft_printf", "ft_printf_test", "ft_printf", part, counts[group],
                "compare_libc", f"ft_printf({raw})", args, None, rel(path), hit.line,
                group=group, bonus=bonus,
                notes="Stdout and return value must match printf.",
            )


def extract_printf_unit():
    header = (TESTS / "printf" / "unit-test" / "inc" / "printf_unit_test.h").read_text(errors="replace")
    source = (TESTS / "printf" / "unit-test" / "inc" / "source-generator.h").read_text(errors="replace")
    conv = re.search(r'SUPPORTED_CONVERTERS\s+"([^"]+)"', header)
    strings = re.findall(r'"((?:\\.|[^"\\])*)"', source[source.find("rand_strings"):source.find("flag_to_flag")])
    converters = conv.group(1) if conv else "cspdiuxX"
    decoded = [decode_c_string('"' + item + '"') for item in strings]
    add(
        "ft_printf", "unit-test", "ft_printf", "mandatory", "generated", "generated",
        "random formats for converters " + converters, 
        [{"type": "str", "value": item} for item in decoded],
        None, rel(TESTS / "printf" / "unit-test" / "src" / "main.cpp"), 1,
        group=converters,
        generator=(
            "Built at runtime. Converters " + converters
            + ". Basic flags are # 0 - + and space. "
            + "Sample strings are in args. Each case compares ft_printf to printf."
        ),
    )


def extract_gnl():
    folder = TESTS / "get_next_line" / "gnlTester"
    for path, part in ((folder / "tests" / "mandatory.cpp", "mandatory"), (folder / "tests" / "bonus.cpp", "bonus")):
        text = path.read_text(errors="replace")
        group = "setup"
        counts = {}
        for hit in walk_calls(text, lambda name: name in {"title", "gnl"}):
            if hit.name == "title":
                atoms = parse_arg_list(hit.args_src)
                if len(atoms) == 1 and atoms[0]["type"] == "str":
                    group = atoms[0]["value"].strip().rstrip(":").strip()
                continue
            atoms = parse_arg_list(hit.args_src)
            fd = atoms[0] if atoms else {"type": "expr", "value": "?"}
            second = atoms[1] if len(atoms) > 1 else {"type": "null", "value": None}
            if second["type"] == "null":
                expected = {"type": "end", "value": None}
            elif second["type"] == "str":
                expected = {"type": "str", "value": second["value"]}
            else:
                expected = expected_object(second)
            counts[group] = counts.get(group, 0) + 1
            index = comment_index(text, hit.start) or counts[group]
            notes = None
            if group.startswith("files/") and not (folder / group).exists():
                notes = "Fixture file is not in this repo. The expected line is still listed."
            add(
                "get_next_line", "gnlTester", "get_next_line", part, index, "lines",
                "get_next_line(" + render(fd) + ")", [fd], expected, rel(path), hit.line,
                group=group, notes=notes,
            )


def extract_all():
    extract_fsoares()
    extract_tripouille()
    extract_war_machine()
    extract_alelievr()
    extract_hardcore()
    extract_printf_tester()
    extract_ft_printf_test(bonus_only_functions())
    extract_printf_unit()
    extract_gnl()


def counts_by(key):
    found = {}
    for case in CASES:
        found[case[key]] = found.get(case[key], 0) + 1
    return dict(sorted(found.items()))


def suite_counts():
    found = {}
    for case in CASES:
        label = case["project"] + "/" + case["suite"]
        found[label] = found.get(label, 0) + 1
    return dict(sorted(found.items()))


def main():
    extract_all()
    ids = [case["id"] for case in CASES]
    if len(ids) != len(set(ids)):
        ERRORS.append("duplicate ids")
    document = {
        "schema": "francinette-tests/1",
        "usage": (
            "import json; data = json.load(open('francinette-tests.json')); "
            "cases = [t for t in data['tests'] if t['function'] == 'ft_atoi']"
        ),
        "fields": [
            "id", "project", "suite", "function", "part", "index", "kind",
            "call", "args", "expected", "source", "line", "bonus",
        ],
        "optional": ["group", "generator", "body", "stream", "notes"],
        "args": "List of {type, value}. type is str, char, int, expr, null, or lines.",
        "expected": "null, or {type, value}. type is str, char, int, bool, lines, stdout, stderr, end, expr, or null. end means get_next_line must return NULL.",
        "kinds": {
            "compare_libc": "Return value or buffer must match libc. expected is set when the suite hard-codes it.",
            "stdout": "expected.value is the exact stdout, or stderr when stream is stderr.",
            "expression": "call is the boolean check. args and expected are filled when the check is a direct comparison.",
            "lines": "One get_next_line read. expected is that line, or type end.",
            "sandbox": "Named alelievr behavior test. call is the explanation. body is the C check.",
            "speed": "alelievr speed check against libc.",
            "fuzzer": "Inputs are generated at runtime. body is the driver.",
            "generated": "A loop that was not expanded. generator is the loop.",
            "crash": "Behavior must match libc on crashing inputs.",
            "guard": "Null or allocation guard, not a normal input.",
        },
        "notes": [
            "List functions are mandatory in libft v19.2. Suites still file them under part bonus.",
            "minitalk is named in the README and has no tests in this repository.",
            "printf unit-test builds cases at runtime, so it is one generator record, not a frozen list.",
            "alelievr-hardcore is the same: one fuzzer record per function.",
        ],
        "counts": {
            "total": len(CASES),
            "by_project": counts_by("project"),
            "by_suite": suite_counts(),
            "by_kind": counts_by("kind"),
        },
        "errors": ERRORS,
        "tests": CASES,
    }
    OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT}")
    print(f"total {len(CASES)}")
    for label, count in suite_counts().items():
        print(f"  {label}: {count}")
    if ERRORS:
        print("errors:")
        for error in ERRORS:
            print(" ", error)


if __name__ == "__main__":
    main()
