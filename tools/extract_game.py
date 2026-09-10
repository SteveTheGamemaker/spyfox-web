#!/usr/bin/env python3
"""Extract Spy Fox's original resources from an ISO 9660 disc; no dependencies."""
import argparse
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ('SPYFOX.HE0', 'SPYFOX.HE1', 'SPYFOX.HE2', 'SPYFOX.HE4')


def root_files(disc):
    disc.seek(16 * 2048)
    pvd = disc.read(2048)
    if pvd[:7] != b'\x01CD001\x01':
        raise ValueError('Not an ISO 9660 disc')
    root = pvd[156:190]
    extent, = struct.unpack_from('<I', root, 2)
    size, = struct.unpack_from('<I', root, 10)
    disc.seek(extent * 2048)
    directory = disc.read(size)
    pos = 0
    entries = {}
    while pos < size:
        length = directory[pos]
        if not length:
            pos = (pos // 2048 + 1) * 2048
            continue
        record = directory[pos:pos + length]
        name = record[33:33 + record[32]].decode('ascii').split(';')[0]
        if not record[25] & 2:
            entries[name] = (struct.unpack_from('<I', record, 2)[0] * 2048,
                             struct.unpack_from('<I', record, 10)[0])
        pos += length
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', nargs='?', type=Path, default=ROOT / 'spyfox.iso')
    args = parser.parse_args()
    output = ROOT / 'web/data/games/spyfox'
    output.mkdir(parents=True, exist_ok=True)
    manifest = {}
    report = []
    with args.iso.open('rb') as disc:
        entries = root_files(disc)
        for name in REQUIRED:
            if name not in entries:
                raise ValueError(f'The disc is missing {name}')
            offset, size = entries[name]
            disc.seek(offset)
            data = disc.read(size)
            if len(data) != size:
                raise ValueError(f'Truncated resource: {name}')
            target = name.lower()
            (output / target).write_bytes(data)
            manifest[target] = size
            report.append(dict(file=target, iso_offset=offset, size=size,
                               sha256=hashlib.sha256(data).hexdigest(),
                               scummvm_md5_5000=hashlib.md5(data[:5000]).hexdigest()))
            print(f'{target}: {size:,} bytes')
    (output / 'index.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (ROOT / 'docs/disc-manifest.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
