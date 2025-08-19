#!/usr/bin/env python3
import argparse, os, re, sys

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--seeds', nargs='+', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()
    root = os.path.abspath(args.root)
    deny = re.compile(r's52|Quilt|glChartCanvas|OpenGL|wx/|Osenc|Senc|plugin|test|sample', re.I)
    visited = []
    queue = [os.path.abspath(f) for f in args.seeds]
    seen = set()
    while queue:
        f = queue.pop()
        if f in seen: continue
        seen.add(f)
        if not f.startswith(root):
            continue
        rel = os.path.relpath(f, root)
        if deny.search(rel):
            print(f"deny: {rel}", file=sys.stderr)
            continue
        visited.append(rel)
        try:
            with open(f, 'r', errors='ignore') as fh:
                for line in fh:
                    m = re.match(r'\s*#\s*include\s+"([^"]+)"', line)
                    if m:
                        inc = os.path.normpath(os.path.join(os.path.dirname(f), m.group(1)))
                        if inc.startswith(root):
                            queue.append(inc)
        except Exception:
            pass
        base, ext = os.path.splitext(f)
        for sfx in ['.c', '.cc', '.cpp']:
            cand = base + sfx
            if os.path.exists(cand) and cand != f:
                queue.append(cand)
    with open(args.out, 'w') as out:
        for rel in visited:
            out.write(rel + '\n')
    dirs = {}
    for v in visited:
        d = os.path.dirname(v)
        dirs[d] = dirs.get(d,0)+1
    print(f"files: {len(visited)}")
    print(f"dirs: {len(dirs)}")
    print("sample:")
    for v in visited[:10]:
        print(f"  {v}")

if __name__ == '__main__':
    main()
