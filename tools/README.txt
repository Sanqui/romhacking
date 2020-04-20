gbd.py usage in brief
=====================

Ran into a jumptable?

$ gbd hm3.gbc 00:26E7 dw 16
    dw $2707
    dw $0061
    dw $2707
    dw $270c
    dw $273c
    dw $275a
    dw $2791
    dw $2834
    dw $285b
    dw $288a
    dw $28bb
    dw $28da
    dw $28df
    dw $28fe
    dw $2928
    dw $2966
; 00:2707

Ready to label these?

3$ gbd hm3.gbc 00:26E7 dw 16 State
    dw State0 ; $2707
    dw State1 ; $0061
    dw State2 ; $2707
    dw State3 ; $270c
    dw State4 ; $273c
    dw State5 ; $275a
    dw State6 ; $2791
    dw State7 ; $2834
    dw State8 ; $285b
    dw State9 ; $288a
    dw StateA ; $28bb
    dw StateB ; $28da
    dw StateC ; $28df
    dw StateD ; $28fe
    dw StateE ; $2928
    dw StateF ; $2966
; 00:2707

Dealing with a pointer table?

$ gbd hm3.gbc 7b:4427 dwb 0x15
    dwb $42d6, $6d
    dwb $46f0, $6d
    dwb $4759, $6d
    dwb $4812, $6d
    dwb $5628, $6d
    dwb $5c33, $6d
    dwb $6285, $6d
    dwb $4bcb, $6d
    dwb $4fe2, $6d
    dwb $6bec, $6d
    dwb $6d3f, $6d
    dwb $6e14, $6d
    dwb $6f46, $6d
    dwb $7094, $6d
    dwb $7094, $6d
    dwb $71b7, $6d
    dwb $4feb, $6c
    dwb $4feb, $6c
    dwb $5622, $6c
    dwb $5bd4, $6c
; 7b:4463

Oh, wait, but we want to symbolize, right?  Just prepare a `pwb` macro and...

$ gbd hm3.gbc 7b:4427 dwb 0x14 Tilemap
    pwb Tilemap0 ; 6d:42d6
    pwb Tilemap1 ; 6d:46f0
    pwb Tilemap2 ; 6d:4759
    pwb Tilemap3 ; 6d:4812
    pwb Tilemap4 ; 6d:5628
    pwb Tilemap5 ; 6d:5c33
    pwb Tilemap6 ; 6d:6285
    pwb Tilemap7 ; 6d:4bcb
    pwb Tilemap8 ; 6d:4fe2
    pwb Tilemap9 ; 6d:6bec
    pwb Tilemapa ; 6d:6d3f
    pwb Tilemapb ; 6d:6e14
    pwb Tilemapc ; 6d:6f46
    pwb Tilemapd ; 6d:7094
    pwb Tilemape ; 6d:7094
    pwb Tilemapf ; 6d:71b7
    pwb Tilemap10 ; 6c:4feb
    pwb Tilemap11 ; 6c:4feb
    pwb Tilemap12 ; 6c:5622
    pwb Tilemap13 ; 6c:5bd4
; 7b:4463

Wait, by "symbolize" I meant "stick them into shim.sym", because I'm lazy.  Ok.

$ gbd hm3.gbc 7b:4427 swb 0x14 Tilemap
6d:42d6 Tilemap0
6d:46f0 Tilemap1
6d:4759 Tilemap2
6d:4812 Tilemap3
6d:5628 Tilemap4
6d:5c33 Tilemap5
6d:6285 Tilemap6
6d:4bcb Tilemap7
6d:4fe2 Tilemap8
6d:6bec Tilemap9
6d:6d3f Tilemapa
6d:6e14 Tilemapb
6d:6f46 Tilemapc
6d:7094 Tilemapd
6d:7094 Tilemape
6d:71b7 Tilemapf
6c:4feb Tilemap10
6c:4feb Tilemap11
6c:5622 Tilemap12
6c:5bd4 Tilemap13

Some weirdly formatted data?  No problem.

$ gbd hm3.gbc 7A:544C db 64 4
    db $81, $83, $72, $02
    db $ff, $77, $75, $05
    db $ff, $ff, $77, $07
    db $ff, $ff, $68, $08
    db $ff, $ff, $69, $09
    db $7a, $ff, $7a, $09
    db $ff, $ff, $66, $ff
    db $15, $17, $ff, $ff
    db $25, $27, $ff, $ff
    db $35, $37, $ff, $ff
    db $45, $47, $ff, $ff
    db $55, $57, $ff, $ff
    db $65, $67, $ff, $ff
    db $75, $77, $ff, $06
    db $09, $00, $ff, $ff
    db $19, $10, $ff, $ff
; 7a:548c

Oh, this look like a huge tilemap.  Still fine!

$ gbd hm3.gbc 7A:745C db 20*13 20
    db $d8,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$d9,$da
    db $db,$d7,$0a,$d7,$0b,$d7,$0c,$d7,$0d,$d7,$0e,$d7,$0f,$d7,$10,$d7,$11,$d7,$12,$df
    db $db,$d7,$13,$d7,$14,$d7,$15,$d7,$16,$d7,$17,$d7,$18,$d7,$19,$d7,$1a,$d7,$1b,$df
    db $db,$d7,$1c,$d7,$1d,$d7,$1e,$d7,$1f,$d7,$20,$d7,$21,$d7,$22,$d7,$23,$d7,$d7,$df
    db $db,$d7,$24,$d7,$25,$d7,$26,$d7,$27,$d7,$28,$d7,$29,$d7,$2a,$d7,$2b,$d7,$2c,$df
    db $db,$d7,$2d,$d7,$2e,$d7,$2f,$d7,$30,$d7,$31,$d7,$32,$d7,$33,$d7,$34,$d7,$35,$df
    db $db,$d7,$36,$d7,$37,$d7,$38,$d7,$39,$d7,$3a,$d7,$3b,$d7,$3c,$d7,$3d,$d7,$d7,$df
    db $db,$d7,$4a,$d7,$4d,$d7,$4e,$d7,$6a,$d7,$6d,$d7,$6e,$d7,$77,$d7,$d7,$d7,$d7,$df
    db $db,$d7,$00,$d7,$01,$d7,$02,$d7,$03,$d7,$04,$d7,$05,$d7,$06,$d7,$ef,$d7,$d7,$df
    db $db,$d7,$07,$d7,$08,$d7,$09,$d7,$df,$d7,$e0,$d7,$e1,$d7,$e8,$d7,$d7,$d7,$d7,$df
    db $db,$d7,$e9,$d7,$ec,$d7,$e5,$d7,$e6,$d7,$e2,$d7,$e3,$d7,$e4,$d7,$d7,$d7,$d7,$df
    db $db,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$d7,$00,$09,$0b,$df
    db $dc,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$dd,$de
; 7a:7560
