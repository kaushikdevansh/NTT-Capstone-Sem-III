// Box.asm  -  K=60
// Box: starts at row 60, 20 rows tall, 16 pixels wide (1 word(s)) from left edge.
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
    @18304         // address of row 60, column 0
    D=A
    @addr
    M=D
    @20
    D=A
    @rows
    M=D
(ROW)
    @1
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
    @31             // move to next screen row (32 - 1)
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
