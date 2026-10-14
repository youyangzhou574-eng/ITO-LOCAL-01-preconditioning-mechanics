"""Offline structure/manifest checks for this instruction-only skill bundle.

Does not fetch external links, run bundled code, install dependencies, or prove
agent behavior/FE correctness. Exact package hashes are checked, not trust of
the manifest author. Python 3.10+ standard library only.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys


def _reject_constant(value):
    raise ValueError('Nonfinite JSON constant: ' + value)


def _files(root):
    return sorted(p for p in root.rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and p.suffix != '.pyc')


def validate(root):
    root = Path(root).resolve()
    errors = []
    if not root.is_dir():
        return ['Skill root is not a directory']
    files = _files(root)
    for p in files:
        if p.is_symlink() or not p.resolve().is_relative_to(root):
            errors.append('Symlink/outside file not allowed in bundle: ' + str(p))
    skill = root/'SKILL.md'
    if not skill.is_file():
        errors.append('Missing SKILL.md frontmatter')
    else:
        try:
            text = skill.read_text(encoding='utf-8')
            header = text.split('---',2)
            if len(header) != 3 or header[0] != '' or not header[1].startswith('\n'):
                errors.append('Invalid SKILL.md frontmatter')
            else:
                pairs = {}
                for line in header[1].strip().splitlines():
                    key, sep, value = line.partition(':')
                    if not sep or key in pairs:
                        errors.append('Invalid/duplicate frontmatter field: ' + line)
                    pairs[key] = value.strip()
                if set(pairs) != {'name','description'}:
                    errors.append('Expected name and description frontmatter')
                if pairs.get('name') != 'abaqus-modeling-fracture':
                    errors.append('Wrong skill name')
                if not pairs.get('description','').startswith('Use when'):
                    errors.append('Description must identify trigger')
        except UnicodeError:
            errors.append('SKILL.md is not UTF-8')
    for p in files:
        try:
            text = p.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            errors.append('Unreadable/non-UTF8 text file: ' + str(p.relative_to(root)))
            continue
        if p.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if '://' in link or link.startswith('#'):
                    continue
                target = (p.parent/link.split('#')[0]).resolve()
                if not target.is_relative_to(root):
                    errors.append('Escaping link: ' + link)
                elif not target.exists():
                    errors.append('Missing link: ' + link)
        if p.suffix == '.json':
            try:
                json.loads(text, parse_constant=_reject_constant)
            except (ValueError, TypeError) as exc:
                errors.append('Invalid JSON ' + p.name + ': ' + str(exc))
        if p.suffix == '.py':
            try:
                tree = ast.parse(text, filename=str(p))
            except SyntaxError as exc:
                errors.append('Invalid Python syntax: ' + str(exc))
                continue
            if p.parent == root/'scripts':
                forbidden = {'odbAccess','abaqus','subprocess','socket','requests','urllib','http'}
                for node in ast.walk(tree):
                    names = ([alias.name for alias in node.names] if isinstance(node,ast.Import)
                             else [node.module or ''] if isinstance(node,ast.ImportFrom) else [])
                    for name in names:
                        if name.split('.')[0] in forbidden:
                            errors.append('Forbidden import in offline helper: ' + name)
    manifest_path = root/'FILE_MANIFEST.json'
    if not manifest_path.is_file():
        errors.append('Missing FILE_MANIFEST.json')
        return errors
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'), parse_constant=_reject_constant)
        records = manifest['files']
        paths = [r['path'] for r in records]
        if len(paths) != len(set(paths)):
            errors.append('Duplicate manifest inventory entries')
        actual = {p.relative_to(root).as_posix() for p in files if p != manifest_path}
        if set(paths) != actual:
            errors.append('Manifest inventory differs from bundle files')
        for r in records:
            p = (root/r['path']).resolve()
            if not p.is_relative_to(root):
                errors.append('Escaping manifest path: ' + r['path']); continue
            if not p.is_file():
                errors.append('Missing manifest file: ' + r['path']); continue
            b = p.read_bytes()
            if len(b) != r['bytes'] or hashlib.sha256(b).hexdigest() != r['sha256']:
                errors.append('Manifest hash/size mismatch: ' + r['path'])
    except (ValueError, KeyError, TypeError, OSError) as exc:
        errors.append('Invalid manifest: ' + str(exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    print(json.dumps({'status': 'PASS' if not errors else 'FAIL',
                      'scope': 'OFFLINE_STRUCTURE_AND_HASHES_ONLY',
                      'errors': errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
