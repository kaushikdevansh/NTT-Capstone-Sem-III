"""Hack assembler (two-pass). Usage: python assembler.py File.asm
Extra feature is chosen from K (stored in k.txt by setup.py):
  K mod 3 == 0 -> write symbols.txt
  K mod 3 == 1 -> clear error messages with line numbers
  K mod 3 == 2 -> warn on duplicate labels
"""
import sys, os

COMP = {'0':'101010','1':'111111','-1':'111010','D':'001100','A':'110000',
        '!D':'001101','!A':'110001','-D':'001111','-A':'110011','D+1':'011111',
        'A+1':'110111','D-1':'001110','A-1':'110010','D+A':'000010',
        'A+D':'000010','D-A':'010011','A-D':'000111','D&A':'000000',
        'A&D':'000000','D|A':'010101','A|D':'010101'}
JUMP = {'':'000','JGT':'001','JEQ':'010','JGE':'011','JLT':'100',
        'JNE':'101','JLE':'110','JMP':'111'}
PREDEF = {'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4,'SCREEN':16384,'KBD':24576,
          **{f'R{i}': i for i in range(16)}}

def get_k():
    try:
        return int(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'k.txt')).read())
    except Exception:
        return None

K = get_k()
FEATURE = None if K is None else K % 3

def comp_bits(c):
    if c in COMP:
        return '0' + COMP[c]
    m = c.replace('M', 'A')
    if 'M' in c and 'A' not in c and m in COMP:
        return '1' + COMP[m]
    raise ValueError('invalid instruction')

def dest_bits(d):
    if d not in ('', 'M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD') and \
       sorted(d) not in (sorted(x) for x in ('M', 'D', 'MD', 'A', 'AM', 'AD', 'AMD')):
        raise ValueError('invalid instruction')
    return ''.join('1' if x in d else '0' for x in 'ADM')

def assemble(path):
    lines = []
    with open(path) as f:
        for n, raw in enumerate(f, 1):
            s = raw.split('//')[0].replace(' ', '').replace('\t', '').strip()
            if s:
                lines.append((n, s))

    # ---- First reading: remember where each label is
    syms, rom, code, labels = dict(PREDEF), 0, [], {}
    for n, s in lines:
        if s[0] == '(':
            name = s[1:-1]
            if name in labels and FEATURE == 2:
                print(f'Warning: Line {n}: label ({name}) is already defined')
            syms[name] = rom
            labels[name] = rom
        else:
            code.append((n, s))
            rom += 1

    # ---- Second reading: translate to 16 bits
    nxt, out, variables, errors = 16, [], {}, 0
    for n, s in code:
        try:
            if s[0] == '@':
                v = s[1:]
                if v.isdigit():
                    num = int(v)
                    if num > 32767:
                        raise ValueError('invalid instruction')
                else:
                    if not v:
                        raise ValueError('invalid instruction')
                    if v not in syms:
                        syms[v] = nxt
                        variables[v] = nxt
                        nxt += 1
                    num = syms[v]
                out.append(format(num, '016b'))
            else:
                d, rest = s.split('=', 1) if '=' in s else ('', s)
                c, j = rest.split(';', 1) if ';' in rest else (rest, '')
                if j not in JUMP:
                    raise ValueError('invalid instruction')
                out.append('111' + comp_bits(c) + dest_bits(d) + JUMP[j])
        except ValueError as e:
            if FEATURE == 1:
                print(f'Line {n}: {e}   ->  {s}')
                errors += 1
            else:
                raise
    return out, labels, variables, errors

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python assembler.py File.asm')
    src = sys.argv[1]
    out, labels, variables, errors = assemble(src)
    if errors:
        sys.exit(f'{errors} error(s). No .hack file written.')
    dst = os.path.splitext(src)[0] + '.hack'
    with open(dst, 'w') as f:
        f.write('\n'.join(out) + '\n')
    print(f'Wrote {dst} ({len(out)} instructions)')
    if FEATURE == 0:
        with open(os.path.join(os.path.dirname(os.path.abspath(src)), 'symbols.txt'), 'w') as f:
            for k, v in {**labels, **variables}.items():
                f.write(f'{k} {v}\n')
        print('Wrote symbols.txt')
