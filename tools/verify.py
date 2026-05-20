#!/usr/bin/env python3
"""
verify.py - confirm a ROM is the stock No-Intro USA dump this disassembly
targets, before you trust any offset in docs/ or src/.

NES hashing convention: the *cartridge* hash (PRG+CHR, iNES header
stripped) is authoritative. iNES-header byte drift between dumps is
normal and does not affect emulation, so we hash headerless.

    python tools/verify.py "path/to/your.nes"

Exit code 0 = match, 1 = mismatch / bad file.
"""

import hashlib
import sys
import zlib

HEADER = 0x10
WANT_SHA1 = "317FB395B4D408F3A4BEF73DD54C92FBB7748F4D"
WANT_CRC32 = 0x0BDD8DD9
WANT_PRG = 0x20000  # 128 KB


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: verify.py <rom.nes>")
    data = open(sys.argv[1], "rb").read()
    if data[:4] != b"NES\x1a":
        print("FAIL: not an iNES file (missing NES\\x1a magic)")
        return 1
    body = data[HEADER:]
    sha1 = hashlib.sha1(body).hexdigest().upper()
    crc = zlib.crc32(body) & 0xFFFFFFFF
    ok = sha1 == WANT_SHA1 and crc == WANT_CRC32 and len(body) == WANT_PRG

    print("file              : %s" % sys.argv[1])
    print("iNES header       : %s" % data[:HEADER].hex())
    print("PRG size          : %d bytes (want %d)" % (len(body), WANT_PRG))
    print("headerless SHA-1  : %s" % sha1)
    print("                    %s" % ("MATCH" if sha1 == WANT_SHA1 else "MISMATCH (want %s)" % WANT_SHA1))
    print("headerless CRC32  : %08X" % crc)
    print("                    %s" % ("MATCH" if crc == WANT_CRC32 else "MISMATCH (want %08X)" % WANT_CRC32))
    print()
    print("RESULT: %s" % ("OK - stock dump, offsets valid" if ok
                          else "NOT the stock dump - offsets in docs/ may not match"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
