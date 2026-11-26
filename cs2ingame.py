import struct, sys, os, glob

CONT = {16, 14, 26, 15, 3}

class N:
    def __init__(s, t, v, kids=None, raw=None):
        s.t, s.v, s.kids, s.raw = t, v, kids, raw
    def pack(s):
        body = b''.join(k.pack() for k in s.kids) if s.kids is not None else s.raw
        return struct.pack('<III', s.t, len(body), s.v) + body

def parse(d, p, end):
    out = []
    while p + 12 <= end:
        t, sz, v = struct.unpack('<III', d[p:p+12])
        b = d[p+12:p+12+sz]
        out.append(N(t, v, kids=parse(d, p+12, p+12+sz) if t in CONT else None,
                     raw=None if t in CONT else b))
        p += 12 + sz
    return out

def find(n, t):
    return [k for k in n.kids if k.t == t]

def keep_bone(nid, name):
    if nid in (36, 26): return False
    if nid >= 5000: return False
    if nid >= 2000: return 'Toe0' in name and 'Nub' not in name
    return True

def convert(src, dst):
    d = open(src, 'rb').read()
    root = parse(d, 0, len(d))
    clump = next(n for n in root if n.t == 16)
    fl = find(clump, 14)[0]
    st = fl.kids[0]
    exts = fl.kids[1:]
    nfr = struct.unpack('<I', st.raw[:4])[0]
    frames = []
    for i in range(nfr):
        r = st.raw[4+i*56:4+(i+1)*56]
        frames.append(dict(rec=r, parent=struct.unpack('<i', r[48:52])[0]))
    hroot = None
    for i, e in enumerate(exts):
        f = frames[i]; f['name'] = ''; f['hid'] = None
        for x in e.kids:
            if x.t == 0x253f2fe: f['name'] = x.raw.split(b'\0')[0].decode('latin1')
            if x.t == 0x11E:
                f['hid'] = struct.unpack('<I', x.raw[4:8])[0]; f['hx'] = x
                if len(x.raw) > 12: hroot = i
        f['ext'] = e

    ver, rid, nn, hfl, ksz = struct.unpack('<IIIII', frames[hroot]['hx'].raw[:20])
    nodes = [struct.unpack('<III', frames[hroot]['hx'].raw[20+j*12:32+j*12]) for j in range(nn)]
    bone_frame = []
    for j, (nid, idx, _) in enumerate(nodes):
        bone_frame.append(next(i for i, f in enumerate(frames) if f['hid'] == nid and i >= hroot))

    keepf = set()
    for i, f in enumerate(frames):
        if f['hid'] is None or f['hid'] == 0xFFFFFFFF or i < hroot: keepf.add(i)
        elif keep_bone(f['hid'], f['name']): keepf.add(i)
    def anc(i):
        while i not in keepf: i = frames[i]['parent']
        return i
    fmap = {}
    for k, i in enumerate(sorted(keepf)): fmap[i] = k

    keepb = [j for j in range(nn) if bone_frame[j] in keepf]
    newb = {j: k for k, j in enumerate(keepb)}
    bmap = {}
    for j in range(nn):
        a = anc(bone_frame[j])
        bmap[j] = newb[next(jj for jj in range(nn) if bone_frame[jj] == a)]

    recs = []; newexts = []
    for i in sorted(keepf):
        r = bytearray(frames[i]['rec'])
        p = frames[i]['parent']
        if p >= 0: p = fmap[anc(p)] if p not in keepf else fmap[p]
        struct.pack_into('<i', r, 48, p)
        recs.append(bytes(r)); newexts.append(frames[i]['ext'])
    st.raw = struct.pack('<I', len(recs)) + b''.join(recs)
    fl.kids = [st] + newexts

    toes = [i for i in sorted(keepf) if frames[i]['hid'] and 2000 <= frames[i]['hid'] < 5000]
    toes.sort(key=lambda i: ('R ' in frames[i]['name'] or frames[i]['name'].startswith('R')))
    tid = {}
    for k, i in enumerate(toes): tid[i] = 2000 + k
    for i in keepf:
        f = frames[i]
        if f['hid'] is not None and f['hid'] != 0xFFFFFFFF and i != hroot:
            nid = tid.get(i, f['hid'])
            x = f['hx']; x.raw = struct.pack('<III', 256, nid, 0)

    kf = [bone_frame[j] for j in keepb]
    kids = {}
    for j in keepb:
        p = anc(frames[bone_frame[j]]['parent']) if frames[bone_frame[j]]['parent'] not in keepf else frames[bone_frame[j]]['parent']
        kids.setdefault(p, []).append(bone_frame[j])
    rows = []
    for k, j in enumerate(keepb):
        fi = bone_frame[j]
        nid = tid.get(fi, frames[fi]['hid'])
        par = frames[fi]['parent']
        par = par if par in keepf else anc(par)
        sib = kids.get(par, [])
        push = 2 if sib and sib[-1] != fi else 0
        pop = 1 if fi not in kids else 0
        rows.append((nid, k, push | pop))
    frames[hroot]['hx'].raw = struct.pack('<IIIII', ver, rid, len(rows), hfl, ksz) + \
        b''.join(struct.pack('<III', *r) for r in rows)

    gl = find(clump, 26)[0]
    for g in gl.kids[1:]:
        if g.t != 15: continue
        nv = struct.unpack('<IIII', g.kids[0].raw[:16])[2]
        for e in find(g, 3):
            for x in e.kids:
                if x.t != 0x116: continue
                r = x.raw
                nb, nu, mw = r[0], r[1], r[2]
                assert nb == nn and nu == 0, (nb, nn, nu)
                o = 4
                idx = [list(r[o+v*4:o+v*4+4]) for v in range(nv)]; o += nv*4
                wt = [list(struct.unpack('<4f', r[o+v*16:o+v*16+16])) for v in range(nv)]; o += nv*16
                mats = [r[o+j*68:o+j*68+68] for j in range(nb)]
                tail = r[o+nb*68:]
                ni, nw = [], []
                for v in range(nv):
                    acc = {}
                    for a, b in zip(idx[v], wt[v]):
                        if b > 0: acc[bmap[a]] = acc.get(bmap[a], 0) + b
                    items = sorted(acc.items(), key=lambda t: -t[1])[:4]
                    s = sum(w for _, w in items) or 1
                    items = [(i, w/s) for i, w in items]
                    while len(items) < 4: items.append((0, 0.0))
                    ni.append([i for i, _ in items]); nw.append([w for _, w in items])
                nr = bytes([len(keepb), 0, mw, r[3]])
                nr += b''.join(bytes(a) for a in ni)
                nr += b''.join(struct.pack('<4f', *a) for a in nw)
                nr += b''.join(mats[j] for j in keepb) + tail
                x.raw = nr
    open(dst, 'wb').write(b''.join(n.pack() for n in root))
    print('%s -> %s : %d -> %d frame, %d -> %d bone' % (src, dst, nfr, len(recs), nn, len(keepb)))

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(1)
    if os.path.isdir(a[0]):
        od = os.path.join(a[0], 'Out'); os.makedirs(od, exist_ok=True)
        for f in sorted(glob.glob(os.path.join(a[0], '*.dff'))):
            b = os.path.basename(f)
            if b.lower().startswith('cs'):
                convert(f, os.path.join(od, b[2:]))
    else:
        convert(a[0], a[1] if len(a) > 1 else os.path.join(os.path.dirname(a[0]) or '.', os.path.basename(a[0])[2:] if os.path.basename(a[0]).lower().startswith('cs') else 'ingame_' + os.path.basename(a[0])))
