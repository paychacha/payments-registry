#!/usr/bin/env python3
"""Check every file under data/ against the schemas and the rules a schema cannot express.

    pip install -r requirements.txt
    python3 scripts/validate.py

Prints one line per problem and exits with 1 if there is any. The pull request check runs this.

Beyond schema/method.schema.json and schema/provider.schema.json it checks that:
  - a file's name is its id, and ids are unique;
  - countries are ISO 3166-1 alpha-2 codes and currencies current ISO 4217 codes (scripts/codes.py);
  - no two methods have the same name, and no alias is another method's name;
  - a coverage entry names an existing method, once per provider, in order of method id;
  - `checked` is a real date, not in the future.
"""
import collections
import datetime
import glob
import json
import os
import re
import sys
import unicodedata

sys.dont_write_bytecode = True
try:
    import jsonschema
    import yaml
except ImportError:
    sys.exit("Missing packages. Run: pip install -r requirements.txt")
from codes import COUNTRIES, CURRENCIES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems = []


def problem(path, message):
    problems.append(f"{os.path.relpath(path, ROOT)}: {message}")


class Loader(yaml.SafeLoader):
    """YAML as most readers load it, except that a key may not appear twice and a date stays text
    (so `checked: 2026-13-45` is reported here, not thrown by the reader)."""

    def construct_mapping(self, node, deep=False):
        keys = [self.construct_object(key, deep=True) for key, _ in node.value]
        twice = [key for key, n in collections.Counter(keys).items() if n > 1]
        if twice:
            raise yaml.constructor.ConstructorError(None, None, f"key appears twice: {twice[0]}", node.start_mark)
        return super().construct_mapping(node, deep)


Loader.yaml_implicit_resolvers = {
    first: [(tag, pattern) for tag, pattern in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def same(text):
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", plain) or text.lower()


def codes(path, where, values, known, kind):
    """Report list items that are not codes. YAML reads a bare NO (Norway) as false."""
    for value in values if isinstance(values, list) else []:
        if value is False or value is True:
            problem(path, f'{where}: write Norway as "NO" in quotes; a bare NO means false in YAML')
        elif isinstance(value, str) and re.fullmatch(r"[A-Z]+", value) and value not in known:
            problem(path, f"{where}: {value} is not {kind}")


def load(kind, schema_name):
    schema = json.load(open(os.path.join(ROOT, "schema", schema_name), encoding="utf8"))
    validator = jsonschema.Draft202012Validator(schema)
    items = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "data", kind, "*"))):
        name = os.path.basename(path)
        if not name.endswith(".yaml"):
            problem(path, "files here are named <id>.yaml")
            continue
        try:
            with open(path, encoding="utf8") as f:
                item = yaml.load(f, Loader=Loader)
        except yaml.YAMLError as error:
            problem(path, f"not valid YAML: {' '.join(str(error).split())}")
            continue
        if not isinstance(item, dict):
            problem(path, "expected fields (id, name, ...) at the top level")
            continue
        norway = lambda error: error.instance is False and "countries" in [str(p) for p in error.absolute_path]
        for error in sorted(validator.iter_errors(item), key=lambda e: list(map(str, e.absolute_path))):
            if norway(error) or any(norway(e) for e in error.context or []):
                continue  # said better by codes()
            where = ".".join(str(p) for p in error.absolute_path) or "file"
            if error.validator == "not":
                message = "use either `global: true` or `countries`, not both"
            elif error.validator == "dependentRequired":
                message = "`merchant_countries` needs `merchant_countries_source`, the public page that lists them"
            else:
                message = error.message
            problem(path, f"{where}: {message}")
        if item.get("id") != name[: -len(".yaml")]:
            problem(path, f"id is {item.get('id')!r}; it must be the file name without .yaml")
        items[name[: -len(".yaml")]] = (path, item)
    return items


def main():
    methods = load("methods", "method.schema.json")
    providers = load("providers", "provider.schema.json")

    exact = lambda name: " ".join(name.split()).casefold()
    names = {}
    for id_, (path, method) in methods.items():
        if isinstance(method.get("name"), str):
            if exact(method["name"]) in names:
                problem(path, f"name: {method['name']!r} is also the name of {names[exact(method['name'])]}")
            names.setdefault(exact(method["name"]), id_)
    for id_, (path, method) in methods.items():
        codes(path, "countries", method.get("countries"), COUNTRIES, "an ISO 3166-1 alpha-2 country code")
        codes(path, "currencies", method.get("currencies"), CURRENCIES, "a current ISO 4217 currency code")
        seen = {same(method["name"])} if isinstance(method.get("name"), str) else set()
        for alias in method.get("aliases") if isinstance(method.get("aliases"), list) else []:
            if not isinstance(alias, str):
                continue
            if same(alias) in seen:
                problem(path, f"aliases: {alias!r} repeats the name or another alias")
            elif names.get(exact(alias), id_) != id_:
                problem(path, f"aliases: {alias!r} is the name of {names[exact(alias)]}")
            seen.add(same(alias))

    today = datetime.date.today()
    rows = 0
    for id_, (path, provider) in providers.items():
        codes(path, "merchant_countries", provider.get("merchant_countries"), COUNTRIES, "an ISO 3166-1 alpha-2 country code")
        coverage = provider.get("coverage") if isinstance(provider.get("coverage"), list) else []
        listed = [row.get("method") for row in coverage if isinstance(row, dict)]
        for method, n in collections.Counter(listed).items():
            if n > 1:
                problem(path, f"coverage: {method} appears {n} times; one entry per method")
        if listed != sorted(listed, key=str):
            problem(path, "coverage: keep the entries in order of method id")
        for row in coverage:
            if not isinstance(row, dict):
                continue
            rows += 1
            where = f"coverage {row.get('method')}"
            if isinstance(row.get("method"), str) and row["method"] not in methods:
                problem(path, f"{where}: there is no data/methods/{row['method']}.yaml; add the method first")
            codes(path, f"{where}: countries", row.get("countries"), COUNTRIES, "an ISO 3166-1 alpha-2 country code")
            codes(path, f"{where}: currencies", row.get("currencies"), CURRENCIES, "a current ISO 4217 currency code")
            if isinstance(row.get("checked"), str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["checked"]):
                try:
                    if datetime.date.fromisoformat(row["checked"]) > today + datetime.timedelta(days=1):
                        problem(path, f"{where}: checked {row['checked']} is in the future")
                except ValueError:
                    problem(path, f"{where}: checked {row['checked']} is not a date")

    if problems:
        print("\n".join(problems))
        sys.exit(f"\n{len(problems)} problem(s).")
    print(f"OK: {len(methods)} methods, {len(providers)} providers, {rows} coverage entries.")


if __name__ == "__main__":
    main()
