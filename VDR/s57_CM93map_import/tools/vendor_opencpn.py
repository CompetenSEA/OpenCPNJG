#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import hashlib
from pathlib import Path

def rewrite_includes(file_path):
    text = file_path.read_text()
    text = re.sub(r'#include <wx/[^>]+>', '#include "wx_shim.hpp"', text)
    text = text.replace('#include "s52s57.h"', '#include "s52s57_min.h"')
    text = re.sub(r'#include\s+[<"]gdal/(cpl_[^>"]+)[>"]', r'#include "\1"', text)
    file_path.write_text(text)

def main():
    parser = argparse.ArgumentParser(description="Vendor OpenCPN subset")
    parser.add_argument('--ocpn', default='../../')
    args = parser.parse_args()
    ocpn_root = Path(args.ocpn).resolve()
    root = Path(__file__).resolve().parents[1]
    dest = root / 'vendor' / 'opencpn_subset'
    preserve = {'wx_shim.hpp', 's52s57_min.h', 'compat.hpp', 'minimal.cpp'}
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
    exclude = ['s52', 'Quilt', 'chcanv', 'glChartCanvas', '/wx/', 'OpenGL', 'Osenc', 'plugin', 's57.h', 'ddfrecordindex']
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
        dest_file = dest / 'src' / rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest_file)
        rewrite_includes(dest_file)
        copied.append(f'src/{rel_str}')
    filelist = dest.parent / 'vendor_filelist.cmake'
    with filelist.open('w') as fp:
        fp.write('\n'.join(copied))
    forbidden = ['<wx/', 'OpenGL', 's52plib', 'Quilt', 'glChartCanvas', 'Osenc', 'plugin', 'ogr_']
    for rel_str in copied:
        content = (dest / rel_str).read_text()
        for bad in forbidden:
            if bad in content:
                raise SystemExit(f"Forbidden include {bad} in {rel_str}")
    print(f"Copied {len(copied)} files; skipped {skipped}; no forbidden includes")

    # Parse VENDOR_MAP for CPL headers
    vendor_map = root / 'docs' / 'VENDOR_MAP.md'
    headers = set()
    in_dep_table = False
    for line in vendor_map.read_text().splitlines():
        if line.startswith('### CPL header dependencies'):
            in_dep_table = True
            continue
        if in_dep_table:
            if line.startswith('##') and not line.startswith('### CPL'):
                break
            m = re.match(r'\|\s*(cpl_[^|]+)\s*\|', line)
            if m:
                headers.add(m.group(1).strip())
    if 'cpl_port.h' in headers:
        headers.add('cpl_config.h')

    cpl_map = {
        'cpl_error.h': ['cpl_error.cpp'],
        'cpl_conv.h': ['cpl_conv.cpp'],
        'cpl_string.h': ['cpl_string.cpp'],
        'cpl_vsi.h': ['cpl_vsisimple.cpp'],
        'cpl_port.h': [],
        'cpl_config.h': [],
    }

    cpl_dest = root / 'vendor' / 'gdal_cpl'
    if cpl_dest.exists():
        shutil.rmtree(cpl_dest)
    cpl_dest.mkdir(parents=True)

    gdal_src = ocpn_root / 'libs' / 'gdal'
    copied_cpl = []
    for header in headers:
        src = gdal_src / 'include' / 'gdal' / header
        shutil.copy2(src, cpl_dest / header)
        copied_cpl.append(header)
        for srcfile in cpl_map.get(header, []):
            src_path = gdal_src / 'src' / srcfile
            shutil.copy2(src_path, cpl_dest / srcfile)
            copied_cpl.append(srcfile)

    sha_lines = []
    for name in sorted(copied_cpl):
        sha = hashlib.sha256((cpl_dest / name).read_bytes()).hexdigest()
        sha_lines.append(f"- gdal_cpl/{name} `{sha}`")

    prov = root / 'docs' / 'PROVENANCE.md'
    text = prov.read_text()
    block_pattern = r'Vendored CPL files \([^\n]*\) with SHA256:\n(?:- .+\n)*'
    replacement = 'Vendored CPL files ({0}) with SHA256:\n{1}\n'.format(len(sha_lines), '\n'.join(sha_lines))
    text = re.sub(block_pattern, replacement, text)
    prov.write_text(text)

if __name__ == '__main__':
    main()
