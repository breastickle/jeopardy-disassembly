#!/usr/bin/env python3
"""
disasm6502.py - a small, dependency-free 6502 disassembler for the
Jeopardy! 25th Anniversary Edition (NES) ROM.

Targets the stock No-Intro USA dump (headerless cart SHA-1
317FB395B4D408F3A4BEF73DD54C92FBB7748F4D, CRC32 0BDD8DD9). The ROM is
mapper 7 (AOROM): 128 KB PRG = four switchable 32 KB banks mapped at
$8000-$FFFF. There is no CHR-ROM (8 KB CHR-RAM), so large stretches of
PRG are tile/clue data, not code.

This tool exists so the disassembly can be regenerated from the ROM
the maintainer supplies (the ROM is never committed). It does linear
sweeps, recursive-descent code/data mapping, byte-pattern search, and
JSR/JMP cross-reference scans within a single 32 KB AOROM bank.

Usage examples (rom path = your own legally-dumped .nes):
  # Recursive-descent trace from the bank-0 reset/NMI/IRQ vectors:
  python disasm6502.py ROM --bank 0 --trace

  # Linear listing of a CPU range in bank 0:
  python disasm6502.py ROM --bank 0 --linear 8000 80FF

  # Find every write that latches the AOROM bank (STA abs to $8000+):
  python disasm6502.py ROM --bank 0 --find "8D ?? ??" --filter-store-high

  # All JSR/JMP targets reachable in a bank (call graph seed):
  python disasm6502.py ROM --bank 0 --xref

A JSON symbol file (--syms) supplies labels, inline comments and
data-range overrides so the listing grows richer as the ROM is mapped.
"""

import argparse
import json
import sys

HEADER = 0x10          # iNES header size
BANK = 0x8000          # AOROM 32 KB window
PRG = 0x20000          # 128 KB PRG
NBANKS = 4

# --- addressing modes: operand byte count + ca65 format template ------
MODES = {
    "imp": (0, "{m}"),
    "acc": (0, "{m}"),
    "imm": (1, "{m} #${0:02X}"),
    "zp":  (1, "{m} ${0:02X}"),
    "zpx": (1, "{m} ${0:02X},X"),
    "zpy": (1, "{m} ${0:02X},Y"),
    "izx": (1, "{m} (${0:02X},X)"),
    "izy": (1, "{m} (${0:02X}),Y"),
    "abs": (2, "{m} ${0:04X}"),
    "abx": (2, "{m} ${0:04X},X"),
    "aby": (2, "{m} ${0:04X},Y"),
    "ind": (2, "{m} (${0:04X})"),
    "rel": (1, "{m} ${0:04X}"),
}

# --- full 256-entry opcode matrix (legal + undocumented) --------------
# Each entry: (mnemonic, mode, legal?). Undocumented ops are kept so a
# linear sweep never desyncs and so we can use them as a "this is data"
# signal during recursive descent.
OPS = {
    0x00:("BRK","imp",1),0x01:("ORA","izx",1),0x02:("KIL","imp",0),0x03:("SLO","izx",0),
    0x04:("NOP","zp",0), 0x05:("ORA","zp",1), 0x06:("ASL","zp",1), 0x07:("SLO","zp",0),
    0x08:("PHP","imp",1),0x09:("ORA","imm",1),0x0A:("ASL","acc",1),0x0B:("ANC","imm",0),
    0x0C:("NOP","abs",0),0x0D:("ORA","abs",1),0x0E:("ASL","abs",1),0x0F:("SLO","abs",0),
    0x10:("BPL","rel",1),0x11:("ORA","izy",1),0x12:("KIL","imp",0),0x13:("SLO","izy",0),
    0x14:("NOP","zpx",0),0x15:("ORA","zpx",1),0x16:("ASL","zpx",1),0x17:("SLO","zpx",0),
    0x18:("CLC","imp",1),0x19:("ORA","aby",1),0x1A:("NOP","imp",0),0x1B:("SLO","aby",0),
    0x1C:("NOP","abx",0),0x1D:("ORA","abx",1),0x1E:("ASL","abx",1),0x1F:("SLO","abx",0),
    0x20:("JSR","abs",1),0x21:("AND","izx",1),0x22:("KIL","imp",0),0x23:("RLA","izx",0),
    0x24:("BIT","zp",1), 0x25:("AND","zp",1), 0x26:("ROL","zp",1), 0x27:("RLA","zp",0),
    0x28:("PLP","imp",1),0x29:("AND","imm",1),0x2A:("ROL","acc",1),0x2B:("ANC","imm",0),
    0x2C:("BIT","abs",1),0x2D:("AND","abs",1),0x2E:("ROL","abs",1),0x2F:("RLA","abs",0),
    0x30:("BMI","rel",1),0x31:("AND","izy",1),0x32:("KIL","imp",0),0x33:("RLA","izy",0),
    0x34:("NOP","zpx",0),0x35:("AND","zpx",1),0x36:("ROL","zpx",1),0x37:("RLA","zpx",0),
    0x38:("SEC","imp",1),0x39:("AND","aby",1),0x3A:("NOP","imp",0),0x3B:("RLA","aby",0),
    0x3C:("NOP","abx",0),0x3D:("AND","abx",1),0x3E:("ROL","abx",1),0x3F:("RLA","abx",0),
    0x40:("RTI","imp",1),0x41:("EOR","izx",1),0x42:("KIL","imp",0),0x43:("SRE","izx",0),
    0x44:("NOP","zp",0), 0x45:("EOR","zp",1), 0x46:("LSR","zp",1), 0x47:("SRE","zp",0),
    0x48:("PHA","imp",1),0x49:("EOR","imm",1),0x4A:("LSR","acc",1),0x4B:("ALR","imm",0),
    0x4C:("JMP","abs",1),0x4D:("EOR","abs",1),0x4E:("LSR","abs",1),0x4F:("SRE","abs",0),
    0x50:("BVC","rel",1),0x51:("EOR","izy",1),0x52:("KIL","imp",0),0x53:("SRE","izy",0),
    0x54:("NOP","zpx",0),0x55:("EOR","zpx",1),0x56:("LSR","zpx",1),0x57:("SRE","zpx",0),
    0x58:("CLI","imp",1),0x59:("EOR","aby",1),0x5A:("NOP","imp",0),0x5B:("SRE","aby",0),
    0x5C:("NOP","abx",0),0x5D:("EOR","abx",1),0x5E:("LSR","abx",1),0x5F:("SRE","abx",0),
    0x60:("RTS","imp",1),0x61:("ADC","izx",1),0x62:("KIL","imp",0),0x63:("RRA","izx",0),
    0x64:("NOP","zp",0), 0x65:("ADC","zp",1), 0x66:("ROR","zp",1), 0x67:("RRA","zp",0),
    0x68:("PLA","imp",1),0x69:("ADC","imm",1),0x6A:("ROR","acc",1),0x6B:("ARR","imm",0),
    0x6C:("JMP","ind",1),0x6D:("ADC","abs",1),0x6E:("ROR","abs",1),0x6F:("RRA","abs",0),
    0x70:("BVS","rel",1),0x71:("ADC","izy",1),0x72:("KIL","imp",0),0x73:("RRA","izy",0),
    0x74:("NOP","zpx",0),0x75:("ADC","zpx",1),0x76:("ROR","zpx",1),0x77:("RRA","zpx",0),
    0x78:("SEI","imp",1),0x79:("ADC","aby",1),0x7A:("NOP","imp",0),0x7B:("RRA","aby",0),
    0x7C:("NOP","abx",0),0x7D:("ADC","abx",1),0x7E:("ROR","abx",1),0x7F:("RRA","abx",0),
    0x80:("NOP","imm",0),0x81:("STA","izx",1),0x82:("NOP","imm",0),0x83:("SAX","izx",0),
    0x84:("STY","zp",1), 0x85:("STA","zp",1), 0x86:("STX","zp",1), 0x87:("SAX","zp",0),
    0x88:("DEY","imp",1),0x89:("NOP","imm",0),0x8A:("TXA","imp",1),0x8B:("XAA","imm",0),
    0x8C:("STY","abs",1),0x8D:("STA","abs",1),0x8E:("STX","abs",1),0x8F:("SAX","abs",0),
    0x90:("BCC","rel",1),0x91:("STA","izy",1),0x92:("KIL","imp",0),0x93:("AHX","izy",0),
    0x94:("STY","zpx",1),0x95:("STA","zpx",1),0x96:("STX","zpy",1),0x97:("SAX","zpy",0),
    0x98:("TYA","imp",1),0x99:("STA","aby",1),0x9A:("TXS","imp",1),0x9B:("TAS","aby",0),
    0x9C:("SHY","abx",0),0x9D:("STA","abx",1),0x9E:("SHX","aby",0),0x9F:("AHX","aby",0),
    0xA0:("LDY","imm",1),0xA1:("LDA","izx",1),0xA2:("LDX","imm",1),0xA3:("LAX","izx",0),
    0xA4:("LDY","zp",1), 0xA5:("LDA","zp",1), 0xA6:("LDX","zp",1), 0xA7:("LAX","zp",0),
    0xA8:("TAY","imp",1),0xA9:("LDA","imm",1),0xAA:("TAX","imp",1),0xAB:("LAX","imm",0),
    0xAC:("LDY","abs",1),0xAD:("LDA","abs",1),0xAE:("LDX","abs",1),0xAF:("LAX","abs",0),
    0xB0:("BCS","rel",1),0xB1:("LDA","izy",1),0xB2:("KIL","imp",0),0xB3:("LAX","izy",0),
    0xB4:("LDY","zpx",1),0xB5:("LDA","zpx",1),0xB6:("LDX","zpy",1),0xB7:("LAX","zpy",0),
    0xB8:("CLV","imp",1),0xB9:("LDA","aby",1),0xBA:("TSX","imp",1),0xBB:("LAS","aby",0),
    0xBC:("LDY","abx",1),0xBD:("LDA","abx",1),0xBE:("LDX","aby",1),0xBF:("LAX","aby",0),
    0xC0:("CPY","imm",1),0xC1:("CMP","izx",1),0xC2:("NOP","imm",0),0xC3:("DCP","izx",0),
    0xC4:("CPY","zp",1), 0xC5:("CMP","zp",1), 0xC6:("DEC","zp",1), 0xC7:("DCP","zp",0),
    0xC8:("INY","imp",1),0xC9:("CMP","imm",1),0xCA:("DEX","imp",1),0xCB:("AXS","imm",0),
    0xCC:("CPY","abs",1),0xCD:("CMP","abs",1),0xCE:("DEC","abs",1),0xCF:("DCP","abs",0),
    0xD0:("BNE","rel",1),0xD1:("CMP","izy",1),0xD2:("KIL","imp",0),0xD3:("DCP","izy",0),
    0xD4:("NOP","zpx",0),0xD5:("CMP","zpx",1),0xD6:("DEC","zpx",1),0xD7:("DCP","zpx",0),
    0xD8:("CLD","imp",1),0xD9:("CMP","aby",1),0xDA:("NOP","imp",0),0xDB:("DCP","aby",0),
    0xDC:("NOP","abx",0),0xDD:("CMP","abx",1),0xDE:("DEC","abx",1),0xDF:("DCP","abx",0),
    0xE0:("CPX","imm",1),0xE1:("SBC","izx",1),0xE2:("NOP","imm",0),0xE3:("ISC","izx",0),
    0xE4:("CPX","zp",1), 0xE5:("SBC","zp",1), 0xE6:("INC","zp",1), 0xE7:("ISC","zp",0),
    0xE8:("INX","imp",1),0xE9:("SBC","imm",1),0xEA:("NOP","imp",1),0xEB:("SBC","imm",0),
    0xEC:("CPX","abs",1),0xED:("SBC","abs",1),0xEE:("INC","abs",1),0xEF:("ISC","abs",0),
    0xF0:("BEQ","rel",1),0xF1:("SBC","izy",1),0xF2:("KIL","imp",0),0xF3:("ISC","izy",0),
    0xF4:("NOP","zpx",0),0xF5:("SBC","zpx",1),0xF6:("INC","zpx",1),0xF7:("ISC","zpx",0),
    0xF8:("SED","imp",1),0xF9:("SBC","aby",1),0xFA:("NOP","imp",0),0xFB:("ISC","aby",0),
    0xFC:("NOP","abx",0),0xFD:("SBC","abx",1),0xFE:("INC","abx",1),0xFF:("ISC","abx",0),
}

# Instructions that end a straight-line run during recursive descent.
TERMINATORS = {0x4C, 0x6C, 0x60, 0x40, 0x00}  # JMP, JMP(), RTS, RTI, BRK
BRANCHES = {0x10,0x30,0x50,0x70,0x90,0xB0,0xD0,0xF0}  # relative conditionals

# Hardware registers common to every NES, applied automatically so the
# listing reads sensibly without a hand-built symbol file.
HW = {
    0x2000:"PPUCTRL",0x2001:"PPUMASK",0x2002:"PPUSTATUS",0x2003:"OAMADDR",
    0x2004:"OAMDATA",0x2005:"PPUSCROLL",0x2006:"PPUADDR",0x2007:"PPUDATA",
    0x4000:"SQ1_VOL",0x4001:"SQ1_SWEEP",0x4002:"SQ1_LO",0x4003:"SQ1_HI",
    0x4004:"SQ2_VOL",0x4005:"SQ2_SWEEP",0x4006:"SQ2_LO",0x4007:"SQ2_HI",
    0x4008:"TRI_LINEAR",0x400A:"TRI_LO",0x400B:"TRI_HI",
    0x400C:"NOISE_VOL",0x400E:"NOISE_LO",0x400F:"NOISE_HI",
    0x4010:"DMC_FREQ",0x4011:"DMC_RAW",0x4012:"DMC_START",0x4013:"DMC_LEN",
    0x4014:"OAMDMA",0x4015:"APUSTATUS",0x4016:"JOY1",0x4017:"JOY2_FRAME",
}


class Rom:
    def __init__(self, path):
        with open(path, "rb") as f:
            self.raw = f.read()
        if self.raw[:4] != b"NES\x1a":
            sys.exit("not an iNES file (missing NES\\x1a magic)")
        self.prg = self.raw[HEADER:HEADER + PRG]
        if len(self.prg) < PRG:
            sys.exit("PRG shorter than 128 KB; not the expected image")

    def bank_bytes(self, bank):
        off = bank * BANK
        return self.prg[off:off + BANK]

    def file_off(self, bank, cpu):
        """CPU $8000-$FFFF -> file offset (iNES header included)."""
        return HEADER + bank * BANK + (cpu - BANK)


class Symbols:
    def __init__(self, syms_path=None):
        self.labels = {}    # "bank:cpu" -> name
        self.comments = {}  # "bank:cpu" -> text
        self.data = []      # list of [bank, start, end] inclusive-exclusive
        if syms_path:
            with open(syms_path) as f:
                d = json.load(f)
            self.labels = d.get("labels", {})
            self.comments = d.get("comments", {})
            self.data = [tuple(int(x, 0) if isinstance(x, str) else x
                               for x in rng) for rng in d.get("data", [])]

    def label(self, bank, cpu):
        return self.labels.get("%d:%04X" % (bank, cpu))

    def comment(self, bank, cpu):
        return self.comments.get("%d:%04X" % (bank, cpu))

    def is_data(self, bank, cpu):
        for b, s, e in self.data:
            if b == bank and s <= cpu < e:
                return True
        return False


def operand_name(cpu, syms, bank):
    """Render an operand address as a symbol if we know one."""
    if cpu in HW:
        return HW[cpu]
    if cpu >= BANK:
        lbl = syms.label(bank, cpu)
        if lbl:
            return lbl
    return None


def decode(mem, pc):
    """Decode one instruction at in-bank index pc. Returns
    (opcode, mnemonic, mode, length, operand_value, legal)."""
    op = mem[pc]
    mn, mode, legal = OPS[op]
    nbytes, _ = MODES[mode]
    val = None
    if nbytes == 1:
        val = mem[pc + 1] if pc + 1 < len(mem) else 0
    elif nbytes == 2:
        lo = mem[pc + 1] if pc + 1 < len(mem) else 0
        hi = mem[pc + 2] if pc + 2 < len(mem) else 0
        val = lo | (hi << 8)
    return op, mn, mode, 1 + nbytes, val, legal


def target_addr(mode, val, cpu):
    """Absolute CPU address an instruction refers to, or None."""
    if mode in ("abs", "abx", "aby", "ind"):
        return val
    if mode == "rel":
        rel = val - 256 if val >= 0x80 else val
        return (cpu + 2 + rel) & 0xFFFF
    return None


def fmt_instruction(bank, cpu, op, mn, mode, length, val, legal, mem, idx, syms):
    raw = " ".join("%02X" % mem[idx + i] for i in range(length))
    tmpl = MODES[mode][1]
    tgt = target_addr(mode, val, cpu)
    text = ""
    if mode in ("imp", "acc"):
        text = mn if mode == "imp" else mn + " A"
    elif mode == "rel":
        sym = operand_name(tgt, syms, bank)
        text = "%s %s" % (mn, sym if sym else "$%04X" % tgt)
    elif mode in ("abs", "abx", "aby", "ind"):
        sym = operand_name(val, syms, bank)
        shown = sym if sym else "$%04X" % val
        suffix = {"abs": "", "abx": ",X", "aby": ",Y", "ind": ""}[mode]
        if mode == "ind":
            text = "%s (%s)" % (mn, shown)
        else:
            text = "%s %s%s" % (mn, shown, suffix)
    else:
        text = tmpl.format(val, m=mn)
    flag = "" if legal else "  ; *** undocumented opcode (likely data)"
    note = syms.comment(bank, cpu)
    comment = "  ; $%04X  %s" % (cpu, raw)
    if note:
        comment += "  " + note
    return "    %-22s%s%s" % (text, comment, flag)


def trace(rom, bank, entries, syms):
    """Recursive-descent: mark every byte reachable as code starting
    from the given entry CPU addresses. Returns a set of in-bank code
    indices and the set of discovered entry labels."""
    mem = rom.bank_bytes(bank)
    code = set()       # in-bank indices that begin an instruction
    seen = set()
    work = list(entries)
    jsr_targets, jmp_targets = set(), set()
    while work:
        cpu = work.pop()
        if cpu < BANK:        # RAM / register space, not in this bank
            continue
        idx = cpu - BANK
        while 0 <= idx < BANK:
            if idx in seen:
                break
            seen.add(idx)
            cur_cpu = idx + BANK
            if syms.is_data(bank, cur_cpu):
                break
            op, mn, mode, length, val, legal = decode(mem, idx)
            if not legal:
                break          # wandered into data; stop this run
            code.add(idx)
            tgt = target_addr(mode, val, cur_cpu)
            if op == 0x20:                       # JSR
                if tgt is not None and tgt >= BANK:
                    jsr_targets.add(tgt)
                    work.append(tgt)
            elif op in BRANCHES:                 # conditional: follow both
                if tgt is not None:
                    work.append(tgt)
            elif op == 0x4C:                     # JMP abs
                if tgt is not None and tgt >= BANK:
                    jmp_targets.add(tgt)
                    work.append(tgt)
                break
            elif op in TERMINATORS:              # JMP(), RTS, RTI, BRK
                break
            idx += length
    return code, jsr_targets, jmp_targets


def listing(rom, bank, start, end, syms, code=None):
    """Emit an annotated listing for [start,end) CPU addresses. If a
    `code` set is given, indices not in it are emitted as .byte data."""
    mem = rom.bank_bytes(bank)
    out = []
    cpu = start
    while cpu < end:
        idx = cpu - BANK
        lbl = syms.label(bank, cpu)
        if lbl:
            out.append("%s:" % lbl)
        is_code = (code is None) or (idx in code)
        if is_code and not syms.is_data(bank, cpu):
            op, mn, mode, length, val, legal = decode(mem, idx)
            if cpu + length > end:
                length = end - cpu
                out.append("    .byte " + ", ".join(
                    "$%02X" % mem[idx + i] for i in range(length)))
                break
            out.append(fmt_instruction(bank, cpu, op, mn, mode, length,
                                       val, legal, mem, idx, syms))
            cpu += length
        else:
            note = syms.comment(bank, cpu)
            tail = "  ; %s" % note if note else ""
            out.append("    .byte $%02X%s" % (mem[idx], tail))
            cpu += 1
    return "\n".join(out)


def find(rom, bank, pattern, filter_store_high=False):
    """Find a byte pattern ('8D ?? ??' etc.) in a bank. With
    filter_store_high, only report matches whose absolute operand is
    >= $8000 (i.e. the kind of write that latches the AOROM bank)."""
    mem = rom.bank_bytes(bank)
    toks = pattern.split()
    pat = [None if t == "??" else int(t, 16) for t in toks]
    hits = []
    for i in range(len(mem) - len(pat) + 1):
        if all(p is None or mem[i + j] == p for j, p in enumerate(pat)):
            cpu = i + BANK
            if filter_store_high and len(pat) >= 3:
                operand = mem[i + 1] | (mem[i + 2] << 8)
                if operand < BANK:
                    continue
            hits.append((cpu, rom.file_off(bank, cpu),
                         " ".join("%02X" % mem[i + j] for j in range(len(pat)))))
    return hits


def xref(rom, bank, syms):
    """List every JSR/JMP-abs target reachable by linear scan of a bank."""
    mem = rom.bank_bytes(bank)
    targets = {}
    i = 0
    while i < BANK - 2:
        op = mem[i]
        if op in (0x20, 0x4C):
            tgt = mem[i + 1] | (mem[i + 2] << 8)
            if tgt >= BANK:
                targets.setdefault(tgt, []).append(i + BANK)
        i += 1
    return targets


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom")
    ap.add_argument("--bank", type=int, default=0, choices=range(NBANKS))
    ap.add_argument("--syms", help="JSON symbol/label/comment/data file")
    ap.add_argument("--linear", nargs=2, metavar=("START", "END"),
                    help="linear listing of CPU range (hex, END exclusive)")
    ap.add_argument("--trace", action="store_true",
                    help="recursive-descent from --entry (or the vectors)")
    ap.add_argument("--entry", action="append", default=[],
                    help="extra entry CPU address (hex); repeatable")
    ap.add_argument("--find", help="byte pattern, e.g. '8D ?? ??'")
    ap.add_argument("--filter-store-high", action="store_true",
                    help="with --find, keep only operands >= $8000")
    ap.add_argument("--xref", action="store_true",
                    help="list JSR/JMP-abs targets in the bank")
    ap.add_argument("--dump", nargs=2, metavar=("START", "END"),
                    help="hex+char dump of a CPU range (hex, END exclusive)")
    ap.add_argument("--refs", metavar="ADDR",
                    help="find instructions whose operand == ADDR (hex)")
    args = ap.parse_args()

    rom = Rom(args.rom)
    syms = Symbols(args.syms)

    if args.find:
        for cpu, fo, b in find(rom, args.bank, args.find, args.filter_store_high):
            lbl = syms.label(args.bank, cpu) or ""
            print("$%04X  file 0x%05X  %-12s %s" % (cpu, fo, b, lbl))
        return

    if args.xref:
        tgts = xref(rom, args.bank, syms)
        for tgt in sorted(tgts):
            lbl = syms.label(args.bank, tgt) or ""
            callers = ", ".join("$%04X" % c for c in tgts[tgt][:6])
            more = "" if len(tgts[tgt]) <= 6 else " (+%d)" % (len(tgts[tgt]) - 6)
            print("$%04X  %-16s <- %s%s" % (tgt, lbl, callers, more))
        return

    if args.trace:
        # Default entries: the three vectors at the bank tail.
        mem = rom.bank_bytes(args.bank)
        nmi = mem[0x7FFA] | (mem[0x7FFB] << 8)
        rst = mem[0x7FFC] | (mem[0x7FFD] << 8)
        irq = mem[0x7FFE] | (mem[0x7FFF] << 8)
        entries = [rst, nmi, irq] + [int(e, 16) for e in args.entry]
        code, jsr, jmp = trace(rom, args.bank, entries, syms)
        print("; bank %d vectors: NMI $%04X  RESET $%04X  IRQ $%04X"
              % (args.bank, nmi, rst, irq))
        print("; reachable code bytes: %d / %d (%.1f%%)"
              % (len(code), BANK, 100 * len(code) / BANK))
        print("; distinct JSR targets: %d   JMP targets: %d"
              % (len(jsr), len(jmp)))
        return

    if args.dump:
        mem = rom.bank_bytes(args.bank)
        start = int(args.dump[0], 16)
        end = int(args.dump[1], 16)
        cpu = start
        while cpu < end:
            row = mem[cpu - BANK:min(cpu - BANK + 16, end - BANK)]
            hexs = " ".join("%02X" % b for b in row)
            chrs = "".join(chr(b) if 0x20 <= b < 0x7F else "." for b in row)
            print("$%04X  file 0x%05X  %-47s  %s"
                  % (cpu, rom.file_off(args.bank, cpu), hexs, chrs))
            cpu += 16
        return

    if args.refs:
        target = int(args.refs, 16)
        mem = rom.bank_bytes(args.bank)
        i = 0
        while i < BANK:
            op = mem[i]
            mn, mode, legal = OPS[op]
            nb, _ = MODES[mode]
            if nb == 2 and i + 2 < BANK:
                val = mem[i + 1] | (mem[i + 2] << 8)
                if val == target:
                    print("$%04X  %-4s %-4s $%04X" % (i + BANK, mn, mode, val))
            i += 1
        return

    if args.linear:
        start = int(args.linear[0], 16)
        end = int(args.linear[1], 16)
        print(listing(rom, args.bank, start, end, syms))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
