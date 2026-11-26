import os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
from cs2ingame import convert
imp, exp = os.path.join(here, 'Import'), os.path.join(here, 'Export')
os.makedirs(imp, exist_ok=True); os.makedirs(exp, exist_ok=True)
n = ok = 0
for root, dirs, files in os.walk(imp):
    for f in sorted(files):
        if not f.lower().endswith('.dff'): continue
        n += 1
        src = os.path.join(root, f)
        rel = os.path.relpath(root, imp)
        od = exp if rel == '.' else os.path.join(exp, rel)
        os.makedirs(od, exist_ok=True)
        out = f[2:] if f.lower().startswith('cs') else 'ingame_' + f
        try:
            convert(src, os.path.join(od, out)); ok += 1
        except Exception as e:
            print('LOI %s: %r' % (os.path.join(rel, f), e))
if not n: print('Import trong. Bo file csplayN.dff (co the nam trong thu muc con) vao Import.')
print('Xong %d/%d file -> Export (giu nguyen cau truc thu muc)' % (ok, n))
