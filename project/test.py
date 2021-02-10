def replace_args(ln, tgt):
    from re import findall, match
    digits = "[0-9]+"
    argpattern = f"(\${{{digits}}})"
    for m in findall(argpattern, ln):
        i = int(match( f"\${{({digits})}}" , m).groups()[0])
        if tgt=='bat':
            ln = ln.replace(m,  f"%{i}")
        else:
            assert(tgt=='sh')
            ln = ln.replace(m,  f"${i}")
    argpattern = "\${\*}"
    m = findall(argpattern, ln)
    if m:
        assert(len(m)==1)
        m = m[0]
        if tgt=='bat':
            ln = ln.replace(m, r"%*")
        else:
            assert(tgt=='sh')
            ln = ln.replace(m, "$@")
    return ln

