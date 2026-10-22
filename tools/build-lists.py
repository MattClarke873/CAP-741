"""Rebuild the autocomplete lists in data/ from the CAA source files.

  python3 tools/build-lists.py <part66-type-rating-list.xlsx> <part145-orgs.txt>

The Part 145 text comes from the CAA "Airworthiness Approved Organisations" PDF:
  swift tools/pdf-text.swift part145.pdf > part145.txt
"""
import sys, re, json, zipfile, xml.etree.ElementTree as ET

M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'

def first_sheet_rows(path):
    z = zipfile.ZipFile(path)
    ss = [''.join(t.text or '' for t in si.iter(M + 't')) for si in ET.fromstring(z.read('xl/sharedStrings.xml'))]
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    first = wb.find(M + 'sheets')[0]          # newest year is the first tab
    target = 'xl/worksheets/' + rels[first.get(R + 'id')].split('/')[-1]
    rows = []
    for row in ET.fromstring(z.read(target)).iter(M + 'row'):
        r = {}
        for c in row.findall(M + 'c'):
            v = c.find(M + 'v')
            val = ss[int(v.text)] if c.get('t') == 's' and v is not None else (v.text if v is not None else '')
            n = 0
            for ch in re.match(r'[A-Z]+', c.get('r')).group(): n = n * 26 + ord(ch) - 64
            if val: r[n - 1] = val
        if r: rows.append([r.get(i, '') for i in range(max(r) + 1)])
    return first.get('name'), rows

def types(xlsx):
    year, rows = first_sheet_rows(xlsx)
    tidy = lambda s: re.sub(r'\s+', ' ', s or '').strip()
    holders, ends, out, seen = [], [], [], set()
    idx = lambda lst, v: lst.index(v) if v in lst else (lst.append(v) or len(lst) - 1)
    for r in rows:
        r += [''] * (11 - len(r))
        if not r[0] or r[0].startswith(('List', 'Aircraft')) or r[9].strip() == 'D': continue
        h, model, desig, end = tidy(r[2]), tidy(r[3]), tidy(r[4]), tidy(r[5])
        if not end or not model: continue
        key = (h, model, end)
        if key in seen: continue
        seen.add(key)
        out.append([idx(holders, h), model, desig, idx(ends, end)])
    ver = re.search(r'Version\s*(\d+)', rows[0][0]) if rows and rows[0] else None
    return {'source': 'UK Part-66 type rating list' + (f', version {ver.group(1)}' if ver else f' ({year})'), 'h': holders, 'e': ends, 'r': out}

def part145(txt):
    t = open(txt, encoding='utf-8').read()
    date = re.search(r'^(\d{1,2} [A-Z][a-z]+ \d{4})$', t, re.M)
    out = {}
    for b in re.split(r'(?:^| )Name\n', t, flags=re.M)[1:]:
        m = re.match(r'(.+?) \((UK\.145\.\d+)[^)]*\)\s*\n', b)
        if not m: continue
        if re.search(r'Revocation Date\s*\n\d{1,2} [A-Z]+ \d{4}', b): continue
        w = re.search(r'\nWebsite\n(.*)\n', b)
        town = w.group(1).strip().title() if w and not w.group(1).startswith(('http', 'www', 'Regional')) else ''
        out[m.group(2)] = [m.group(1).strip(), m.group(2), town]
    return {'source': 'CAA UK Part 145 approved organisations' + (f' ({date.group(1)})' if date else ''),
            'r': sorted(out.values(), key=lambda x: x[0].lower())}

if __name__ == '__main__':
    import os
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    t, p = types(sys.argv[1]), part145(sys.argv[2])
    json.dump(t, open(os.path.join(here, 'part66-types.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(p, open(os.path.join(here, 'part145-orgs.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    print(len(t['r']), 'type rows,', len(t['e']), 'ratings;', len(p['r']), 'Part 145 organisations')
