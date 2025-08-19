#!/usr/bin/env python3
import argparse
import os
import re
import shutil
from pathlib import Path

def rewrite_includes(file_path):
    text = file_path.read_text()
    text = re.sub(r'#include <wx/[^>]+>', '#include "wx_shim.hpp"', text)
    text = text.replace('#include "s52s57.h"', '#include "s52s57_min.h"')
    text = re.sub(r'#include <gdal/(cpl_port.h|cpl_conv.h|cpl_string.h)>',
                  r'#include "shim/gdal/\1"', text)
    file_path.write_text(text)

def main():
    parser = argparse.ArgumentParser(description="Vendor OpenCPN subset")
    parser.add_argument('--ocpn', default='../../')
    args = parser.parse_args()
    ocpn_root = Path(args.ocpn).resolve()
    dest = Path(__file__).resolve().parents[1] / 'vendor' / 'opencpn_subset'
    preserve = {'wx_shim.hpp', 's52s57_min.h', 'shim', 'compat.hpp', 'minimal.cpp'}
    if dest.exists():
        for item in dest.iterdir():
            if item.name not in preserve:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
    else:
        dest.mkdir(parents=True)
    patterns = ['iso8211']
    exclude = ['s52', 'Quilt', 'chcanv', 'glChartCanvas', '/wx/', 'OpenGL', 'Osenc', 'plugin']
    copied = []
    skipped = 0
    for path in ocpn_root.rglob('*'):
        if not path.is_file():
            continue
        if path.suffix not in ('.h', '.hpp', '.cpp'):
            continue
        rel = path.relative_to(ocpn_root)
        rel_str = rel.as_posix()
        if not any(pat in rel_str for pat in patterns):
            continue
        if any(exc in rel_str for exc in exclude):
            skipped += 1
            continue
        dest_file = dest / rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest_file)
        rewrite_includes(dest_file)
        copied.append(rel_str)
    filelist = dest.parent / 'vendor_filelist.cmake'
    with filelist.open('w') as fp:
        fp.write('\n'.join(copied))
    forbidden = ['<wx/', 'OpenGL', 's52plib', 'Quilt', 'glChartCanvas', 'Osenc', 'plugin']
    for rel_str in copied:
        content = (dest / rel_str).read_text()
        for bad in forbidden:
            if bad in content:
                raise SystemExit(f"Forbidden include {bad} in {rel_str}")
    print(f"Copied {len(copied)} files; skipped {skipped}; no forbidden includes")

if __name__ == '__main__':
    main()
