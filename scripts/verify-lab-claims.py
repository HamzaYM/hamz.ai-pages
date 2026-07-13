#!/usr/bin/env python3
"""
verify-lab-claims.py — self-auditing verifier for the hamz.ai lab pages.

Reads scripts/lab-claims.json, resolves each machine-checkable claim against
its evidence source in one of the two repo checkouts (the Reliable AI Skills
evidence repo and this website repo), and prints a per-claim PASS/FAIL table.

Exit 0 when every check passes; non-zero when any check fails, listing the
failures. Attested claims (no in-repo machine source) are reported separately
and never affect the exit code, but they are never silently skipped.

Stdlib only. Runs offline from the two checkouts. Override repo roots with the
env vars named in the manifest (HAMZ_EVIDENCE_REPO, HAMZ_WEBSITE) if the
checkouts live somewhere other than the manifest defaults.

Where the "claims last verified" badge would go (NOT added here, per plan;
lands post-consolidation): the hero <div class="crumbs"> of each page, beside
the existing "Updated July 2026" <span> — e.g. a sibling
<span>claims verified YYYY-MM-DD</span> stamped from this script's exit-0 run.
"""

import ast
import json
import os
import re
import sys

MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab-claims.json")


def resolve_roots(manifest):
    roots = {}
    for name, spec in manifest["roots"].items():
        root = os.environ.get(spec["env"], spec["default"])
        if not os.path.isdir(root):
            fail(f"repo root '{name}' not found: {root} "
                 f"(set ${spec['env']} to override)")
        roots[name] = root
    return roots


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def read_file(roots, repo, rel):
    path = os.path.join(roots[repo], rel)
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# ---- table parser: the recovered per-task judge table in the README --------

def parse_per_task_table(text):
    """
    Rows look like:  | S1 | ... | 3/3 -> 3/3 | 2/3 -> 3/3 | [link](...) |
    with the arrow as U+2192. Each 'cold/denom -> loaded/denom' is one task.
    Returns derived study totals.
    """
    pair = re.compile(r"(\d+)\s*/\s*(\d+)\s*(?:→|->)\s*(\d+)\s*/\s*(\d+)")
    cold_total = loaded_total = exp_total = 0
    n_tasks = n_tasks_of_3 = n_tasks_of_4 = 0
    skill_rows = 0
    for line in text.splitlines():
        s = line.strip()
        if not re.match(r"^\|\s*S\d+\b", s):
            continue
        matches = pair.findall(s)
        if not matches:
            continue
        skill_rows += 1
        for cold_hit, denom, loaded_hit, denom2 in matches:
            denom, denom2 = int(denom), int(denom2)
            if denom != denom2:
                raise ValueError(f"denominator mismatch in row: {s!r}")
            cold_total += int(cold_hit)
            loaded_total += int(loaded_hit)
            exp_total += denom
            n_tasks += 1
            if denom == 3:
                n_tasks_of_3 += 1
            elif denom == 4:
                n_tasks_of_4 += 1
    if n_tasks == 0:
        raise ValueError("per-task table not found or empty")
    return {
        "cold_total": cold_total,
        "loaded_total": loaded_total,
        "exp_total": exp_total,
        "n_tasks": n_tasks,
        "n_tasks_of_3": n_tasks_of_3,
        "n_tasks_of_4": n_tasks_of_4,
        "n_skills": skill_rows,
        "cold_pct": round(cold_total / exp_total * 100, 1),
        "loaded_pct": round(loaded_total / exp_total * 100, 1),
    }


def build_tables(manifest, roots):
    tables = {}
    for name, spec in manifest.get("tables", {}).items():
        if spec["parser"] != "per_task_table":
            fail(f"unknown table parser: {spec['parser']}")
        tables[name] = parse_per_task_table(
            read_file(roots, spec["repo"], spec["file"]))
    return tables


# ---- source evaluators -----------------------------------------------------

def eval_arith(expr):
    """Evaluate a literal arithmetic expression safely (numbers + +-*/ only)."""
    node = ast.parse(expr, mode="eval")
    allowed = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
               ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd)
    for n in ast.walk(node):
        if not isinstance(n, allowed):
            raise ValueError(f"disallowed expression element: {type(n).__name__}")
    return eval(compile(node, "<arith>", "eval"), {"__builtins__": {}}, {})


def dig(obj, path):
    for key in path:
        obj = obj[key]
    return obj


def evaluate(check, tables, roots):
    """Return (actual_value, ok, detail)."""
    src = check["source"]
    kind = src["kind"]
    expect = check["expect"]

    if kind == "table_field":
        actual = tables[src["table"]][src["field"]]
        return actual, actual == expect, f"{src['table']}.{src['field']}={actual}"

    if kind == "matrix":
        data = json.loads(read_file(roots, src["repo"], src["file"]))
        val = dig(data, src["path"])
        if src.get("op") == "len":
            actual = len(val)
        else:
            actual = val
        loc = "/".join(str(p) for p in src["path"])
        op = f" (len)" if src.get("op") == "len" else ""
        return actual, actual == expect, f"{os.path.basename(src['file'])}:{loc}{op}={actual}"

    if kind == "literal":
        text = read_file(roots, src["repo"], src["file"])
        present = src["needle"] in text
        return present, present == expect, f"{src['file']} contains needle: {present}"

    if kind == "arith":
        actual = eval_arith(src["expr"])
        return actual, actual == expect, f"{src['expr']}={actual}"

    fail(f"unknown source kind: {kind}")


# ---- reporting -------------------------------------------------------------

def main():
    with open(MANIFEST, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    roots = resolve_roots(manifest)
    tables = build_tables(manifest, roots)

    checks = manifest["checks"]
    results = []
    for check in checks:
        try:
            actual, ok, detail = evaluate(check, tables, roots)
        except (FileNotFoundError, KeyError, ValueError) as exc:
            actual, ok, detail = None, False, f"evidence error: {exc}"
        results.append((check, ok, detail))

    id_w = max(len(c["id"]) for c, _, _ in results)
    print("=" * 72)
    print("LAB CLAIM VERIFICATION")
    print(f"  evidence repo : {roots['evidence_repo']}")
    print(f"  website       : {roots['website']}")
    print("=" * 72)
    print(f"{'STATUS':<6}  {'CLAIM ID':<{id_w}}  EVIDENCE")
    print("-" * 72)
    failures = []
    for check, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures.append((check, detail))
        print(f"{status:<6}  {check['id']:<{id_w}}  {detail}")
        exp = check["expect"]
        print(f"{'':<6}  {'':<{id_w}}  expect={exp!r} :: {check['claim']}")
    print("-" * 72)
    n = len(results)
    passed = n - len(failures)
    print(f"checked: {n}   passed: {passed}   failed: {len(failures)}")

    attested = manifest.get("attested", [])
    print()
    print(f"ATTESTED (no in-repo machine source; not graded): {len(attested)}")
    print("-" * 72)
    aid_w = max((len(a["id"]) for a in attested), default=0)
    for a in attested:
        print(f"ATTEST  {a['id']:<{aid_w}}  {a['claim']}")
        print(f"{'':<8}{'':<{aid_w}}  reason: {a['reason']}")
    print("=" * 72)

    if failures:
        print("\nFAILURES:")
        for check, detail in failures:
            print(f"  - {check['id']}: {check['claim']}")
            print(f"      {detail}  (expected {check['expect']!r})")
        sys.exit(1)
    print("\nAll machine-checkable claims match their evidence.")
    sys.exit(0)


if __name__ == "__main__":
    main()
