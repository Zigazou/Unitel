#!/usr/bin/env python3

import sys
import struct

def ebcdic_to_vdt(bytes):
    tovdt = [
        0x00, 0x01, 0x02, 0x03, 0x04, 0x09, 0x06, 0x7F,
        0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x08, 0x17,
        0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x0A, 0x17, 0x1B,
        0x28, 0x29, 0x3A, 0x3B, 0x3C, 0x05, 0x06, 0x07,
        0x30, 0x31, 0x16, 0x33, 0x34, 0x35, 0x36, 0x04,
        0x38, 0x39, 0x3A, 0x3B, 0x14, 0x15, 0x3E, 0x3F,
        0x20, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47,
        0x48, 0x49, 0x5B, 0x2E, 0x3C, 0x28, 0x2B, 0x21,
        0x26, 0x51, 0x52, 0x53, 0x54, 0x55, 0x56, 0x57,
        0x58, 0x59, 0x5D, 0x24, 0x2A, 0x29, 0x3B, 0x5E,
        0x2D, 0x2F, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67,
        0x68, 0x69, 0x7C, 0x2C, 0x25, 0x5F, 0x3E, 0x3F,
        0x70, 0x71, 0x72, 0x73, 0x74, 0x75, 0x76, 0x77,
        0x78, 0x60, 0x3A, 0x23, 0x40, 0x27, 0x3D, 0x22,
        0x1A, 0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67,
        0x68, 0x69, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
        0x1A, 0x6A, 0x6B, 0x6C, 0x6D, 0x6E, 0x6F, 0x70,
        0x71, 0x72, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
        0x1A, 0x7E, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78,
        0x79, 0x7A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
        0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
        0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
        0x7B, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47,
        0x48, 0x49, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
        0x7D, 0x4A, 0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50,
        0x51, 0x52, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
        0x5C, 0x1A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58,
        0x59, 0x5A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
        0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
        0x38, 0x39, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A,
    ]

    return bytearray([ tovdt[byte] for byte in bytes ])

class UnitelDisk:
    def __init__(self):
        self.bytes = []
        self.set_geometry(
            tracks_per_side=81,
            sectors_per_track=26,
            bytes_per_sector=128
        )

    def set_geometry(self,tracks_per_side, sectors_per_track, bytes_per_sector):
        assert tracks_per_side > 0
        assert sectors_per_track > 0
        assert bytes_per_sector > 0
        assert bytes_per_sector % 128 == 0

        self.tracks_per_side = tracks_per_side
        self.sectors_per_track = sectors_per_track
        self.bytes_per_sector = bytes_per_sector

    def get_offset(self, track, sector):
        assert track >= 0
        assert sector > 0

        return (
            track * self.bytes_per_sector * self.sectors_per_track +
            (sector - 1) * self.bytes_per_sector
        )

    def get_bytes(self, track, sector, length):
        offset = self.get_offset(track, sector)
        return self.bytes[offset : offset + length]

    def check_valid_disk(self):
        if len(self.bytes) < self.get_offset(1, 1):
            raise ValueError("Invalid IBM3740 disk image, catalog missing")

        (ermap,) = struct.unpack("<5s", self.get_bytes(0, 5, 5))
        if ermap != b"ERMAP":
            raise ValueError("Invalid IBM3740 disk image, ERMAP not found")

        (vol1ibmird,) = struct.unpack("<10s", self.get_bytes(0, 7, 10))
        if vol1ibmird != b"VOL1IBMIRD":
            raise ValueError("Invalid IBM3740 disk image, VOL1IBMIRD not found")

        entries = self.dir()

    def load(self, filename):
        # Loads the Unitel EBCDIC bytes
        with open(filename, 'rb') as unitel_file:
            unitel_raw = unitel_file.read()

            # Convert the Unitel EBCDIC bytes to Unitel VDT bytes
            self.bytes = ebcdic_to_vdt(unitel_raw)

        self.check_valid_disk()

    def dir(self):
        entries = []
        for sector in range(8, 27):
            entry = self.get_bytes(0, sector, 80)

            # Read entry type and file name
            (entry_type, _, name) = struct.unpack("<4sc17s", entry[0:22])

            # Ignore deleted entries
            if entry_type == b"DDR1":
                continue

            # Read start and end track/sector
            (trk_from, _, sct_from) = struct.unpack("<2sc2s", entry[28:33])
            (trk_to, _, sct_to) = struct.unpack("<2sc2s", entry[34:39])

            # Converts tracks and sectors to integers
            trk_from = int(trk_from.decode('ascii'))
            sct_from = int(sct_from.decode('ascii'))
            trk_to = int(trk_to.decode('ascii'))
            sct_to = int(sct_to.decode('ascii'))

            entries.append((
                name.decode('ascii').strip(),
                (trk_from, sct_from),
                (trk_to, sct_to)
            ))

        return entries

    def get_file(self, filename):
        entries = self.dir()

        for (name, (trk_from, sct_from), (trk_to, sct_to)) in entries:
            if name != filename:
                continue

            offset_from = self.get_offset(trk_from, sct_from)
            offset_to = self.get_offset(trk_to, sct_to) + self.bytes_per_sector
            return self.bytes[offset_from:offset_to]

        raise FileNotFoundError("File not found")

    def catalog(self):
        catalog = self.get_file("FICMAC")

        # Offsets of catalog screens and number of entries per screen
        # TODO: read as many screens as FICMAC file size allows it
        offsets = [
            (0x380, 12),
            (0x900, 22),
            (0x1100, 22),
            (0x1900, 22),
            (0x2100, 22)
        ]

        pages = []

        # Pages are grouped on several screens
        for (offset, nb_entries) in offsets:
            entries = catalog[offset : offset + nb_entries * 0x40]

            # Get every page of the current screen
            for entry_offset in range(0, nb_entries):
                entry = entries[entry_offset * 0x40: (entry_offset + 1) * 0x40]
                (used, trk_from, sct_from, length, _) = struct.unpack(
                    "<c2s2s4s8s",
                    entry[24:41]
                )

                # First digit indicates if the page is used or not
                if used == b'0':
                    continue

                # Values are encoded in hexadecimal
                trk_from = int(trk_from.decode('ascii'), 16)
                sct_from = int(sct_from.decode('ascii'), 16)
                length = int(length.decode('ascii'), 16)

                pages.append((
                    (trk_from, sct_from),
                    length
                ))

        return pages

def show_help():
    print("Unitel - Extract Videotex pages from 8 inches floppy disks.")
    print()
    print("Usage: unitel.py <command> <filename>")
    print()
    print("Commands:")
    print("    - convert: converts EBCDIC disk image to ASCII disk image")
    print("    - listfiles: list files and offsets")
    print("    - listpages: list Videotex pages and offsets")
    print("    - extract: extract all pages into *.vdt files")
    print()

def main(argv):
    # There must be at least a command and a file name
    if len(argv) < 3:
        show_help()
        sys.exit(1)

    command = argv[1]
    filename = argv[2]

    # Load the Until disk
    disk = UnitelDisk()
    disk.load(filename)

    if command == 'convert':
        # Converts the image from EBCDIC to ASCII
        print("Converting to " + filename + ".ascii")
        with open(filename + '.ascii', 'wb') as output:
            output.write(disk.bytes)
    elif command == 'listfiles':
        # Gives directory entries with start and end offsets
        print("file\tstart\tend")
        print("----\t-----\t---")
        for (name, (trk_from, sct_from), (trk_to, sct_to)) in disk.dir():
            offset_from = disk.get_offset(trk_from, sct_from)
            offset_to = disk.get_offset(trk_to, sct_to) + disk.bytes_per_sector
            print("{}\t{}\t{}".format(
                name,
                offset_from,
                offset_to - 1
            ))
    elif command == 'listpages':
        # List Videotex pages
        print("index\tstart\tlength")
        print("-----\t-----\t------")
        index = 1
        for ((trk_from, sct_from), length) in disk.catalog():
            offset_from = disk.get_offset(trk_from, sct_from)
            print("{:03d}\t{}\t{}".format(
                index,
                offset_from,
                length
            ))
            index += 1
    elif command == 'extract':
        # Extract Videotex pages
        index = 1
        for ((trk_from, sct_from), length) in disk.catalog():
            with open("{}-{:03d}.vdt".format(filename, index), "wb") as output:
                output.write(disk.get_bytes(trk_from, sct_from, length))

            index += 1

if __name__ == '__main__':
    main(sys.argv)
