"""Run once:  python setup.py <K>     e.g. python setup.py 41
Creates k.txt and Box.asm for your K."""
import sys
if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    sys.exit('Usage: python setup.py <K>   (K = last two digits of roll no.)')
K = int(sys.argv[1])
W = (K % 4) + 1                 # width in words (16 pixels each)
START = 16384 + 32 * K          # first word of row K
STEP = 32 - W                   # jump from end of one box row to start of next
open('k.txt', 'w').write(str(K))
asm = f"""// Box.asm  -  K={K}
// Box: starts at row {K}, 20 rows tall, {16*W} pixels wide ({W} word(s)) from left edge.
// While any key is pressed the box is black; otherwise white.

(LOOP)
    @KBD
    D=M
    @BLACK
    D;JNE
    @color
    M=0             // no key -> white
    @DRAW
    0;JMP
(BLACK)
    @color
    M=-1            // key -> black
(DRAW)
    @{START}         // address of row {K}, column 0
    D=A
    @addr
    M=D
    @20
    D=A
    @rows
    M=D
(ROW)
    @{W}
    D=A
    @cols
    M=D
(COL)
    @color
    D=M
    @addr
    A=M
    M=D             // paint one word (16 pixels)
    @addr
    M=M+1
    @cols
    M=M-1
    D=M
    @COL
    D;JGT
    @{STEP}             // move to next screen row (32 - {W})
    D=A
    @addr
    M=D+M
    @rows
    M=M-1
    D=M
    @ROW
    D;JGT
    @LOOP
    0;JMP
"""
open('Box.asm', 'w').write(asm)
print(f'K={K}: width={16*W}px, start address={START}, extra feature = K mod 3 = {K%3}')
print('Next: python assembler.py Box.asm')
