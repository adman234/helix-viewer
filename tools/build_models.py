#!/usr/bin/env python3
"""
Build html/models.js from the model definitions that ship with Line 6 HX Edit.

HX Edit installs its full model database as JSON under its `res` folder:
  *.models              every model, with each parameter's id, name, range,
                        default and displayType
  HX_ModelCatalog.json  category tree, friendly names and on-screen param order
  HelixControls.json    how each displayType is scaled and formatted (units)

Usage:
  python tools/build_models.py ["C:/Program Files (x86)/Line6/HX Edit/res"]

Re-run after updating HX Edit to pick up new models from a firmware release.
"""
import glob
import json
import os
import subprocess
import sys
from datetime import date

DEFAULT_RES = {
    'win32':  r'C:\Program Files (x86)\Line6\HX Edit\res',
    'darwin': '/Applications/HX Edit.app/Contents/Resources',
}
OUT = os.path.join(os.path.dirname(__file__), '..', 'html', 'models.js')

# Keys from HelixControls.json the viewer needs for scaling/formatting.
CONTROL_KEYS = ('format', 'formatUnits', 'isDiscrete', 'dspToDisplayScale',
                'dspToDisplayIntegerOffset', 'minimumValue', 'maximumValue')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def hx_edit_version(res):
    exe = os.path.join(res, '..', 'HX Edit.exe')
    if sys.platform == 'win32' and os.path.exists(exe):
        try:
            out = subprocess.run(
                ['powershell', '-NoProfile', '-Command',
                 f'(Get-Item "{os.path.abspath(exe)}").VersionInfo.ProductVersion'],
                capture_output=True, text=True, timeout=30)
            return out.stdout.strip() or None
        except Exception:
            return None
    return None


def build_controls(res):
    raw = load(os.path.join(res, 'HelixControls.json'))

    def resolve(name, depth=0):
        c = raw.get(name)
        if c is None or depth > 10:
            return None
        if 'alias' in c:
            base = dict(resolve(c['alias'], depth + 1) or {})
            base.update({k: v for k, v in c.items() if k != 'alias'})
            return base
        return c

    out = {}
    for name in raw:
        c = resolve(name)
        if c:
            out[name] = {k: c[k] for k in CONTROL_KEYS if k in c}
    return out


def build_catalog(res):
    """model id -> (category, subcategory, [(paramId, labelOverride)])"""
    cat = load(os.path.join(res, 'HX_ModelCatalog.json'))
    info = {}

    def walk(models, cname, sname):
        for m in models:
            if m['id'] in info:
                continue  # same model listed under Mono and Stereo
            order = []

            def flatten(items):
                # Grouped knobs (e.g. TempoSync/Note Sync/Time) are nested lists.
                for p in items:
                    if isinstance(p, list):
                        flatten(p)
                    else:
                        order.extend(p.items())
            flatten(m.get('params') or [])
            info[m['id']] = (cname, sname, order, m.get('name'))

    for c in cat['categories']:
        walk(c.get('models', []), c['name'], None)
        for s in c.get('subcategories', []):
            walk(s.get('models', []), c['name'], s['name'])
    return info


def build_models(res, catalog):
    models = {}
    for path in sorted(glob.glob(os.path.join(res, '*.models'))):
        for m in load(path):
            mid = m['symbolicID']
            if mid.startswith('@'):
                continue
            cname, sname, order, cat_name = catalog.get(mid, (None, None, [], None))
            params = {p['symbolicID']: p for p in m['params']
                      if not p['symbolicID'].startswith('@')}

            # HX Edit's on-screen order first, then any extra (page 2) params.
            ordered = [pid for pid, _ in order if pid in params]
            ordered += [pid for pid in params if pid not in ordered]
            labels = {pid: label for pid, label in order if label}

            plist = []
            for pid in ordered:
                p = params[pid]
                name = labels.get(pid) or p.get('name') or pid
                row = [pid, None if name == pid else name,
                       p.get('displayType'), p['min'], p['max'], p['default']]
                extra = {}
                for src, dst in (('displayType_stereo', 'dts'),
                                 ('max_stereo', 'maxs'),
                                 ('default_stereo', 'defs')):
                    if src in p:
                        extra[dst] = p[src]
                if extra:
                    row.append(extra)
                plist.append(row)

            entry = {'n': m.get('name') or cat_name or mid, 'p': plist}
            if cname:
                entry['c'] = cname
            if sname:
                entry['s'] = sname
            if m.get('devices'):
                entry['d'] = sorted({d['id'] for d in m['devices']})
            models[mid] = entry
    return models


def main():
    res = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RES.get(sys.platform)
    if not res or not os.path.isdir(res):
        sys.exit(f'HX Edit resource folder not found: {res!r}\n'
                 'Pass the path to HX Edit\'s "res" folder as an argument.')

    catalog = build_catalog(res)
    db = {
        'source': 'HX Edit ' + (hx_edit_version(res) or 'unknown'),
        'built': date.today().isoformat(),
        'controls': build_controls(res),
        'models': build_models(res, catalog),
    }
    js = ('// Generated by tools/build_models.py from Line 6 HX Edit model definitions.\n'
          '// Do not edit by hand; re-run the script after updating HX Edit.\n'
          'window.HX_DB = ' + json.dumps(db, separators=(',', ':'), ensure_ascii=False) + ';\n')
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print(f"{db['source']}: {len(db['models'])} models, "
          f"{sum(len(m['p']) for m in db['models'].values())} params, "
          f"{len(db['controls'])} display types -> {os.path.normpath(OUT)} "
          f"({len(js) // 1024} KB)")


if __name__ == '__main__':
    main()
