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

class DiskGeometry:
    def __init__(self, tps: int, spt: int, bps: int):
        assert tps > 0
        assert spt > 0
        assert bps > 0
        assert bps % 128 == 0

        self.tracks_per_side = tps
        self.sectors_per_track = spt
        self.bytes_per_sector = bps

    def track_size(self):
        return self.sectors_per_track * self.bytes_per_sector

    def disk_size(self):
        return self.track_size() * self.tracks_per_side

    def offset(self, track, sector):
        assert track >= 0
        assert track <= self.tracks_per_side
        assert sector > 0
        assert sector <= self.sectors_per_track

        return (
            track * self.bytes_per_sector * self.sectors_per_track +
            (sector - 1) * self.bytes_per_sector
        )

class SectorAddress:
    def __init__(self, geometry: DiskGeometry, track=0, sector=1):
        self.geometry = geometry
        self.from_track_sector(track, sector)

    def from_track_sector(self, track, sector):
        assert track >= 0
        assert track < self.geometry.tracks_per_side
        assert sector > 0
        assert sector <= self.geometry.sectors_per_track

        self.track = track
        self.sector = sector

    def from_ibm(self, sector_address):
        assert len(sector_address) == 5

        (track, _, sector) = struct.unpack("<2sc2s", sector_address)

        self.track = int(track.decode('ascii'))
        self.sector = int(sector.decode('ascii'))

    def from_unitel(self, sector_address):
        assert len(sector_address) == 4

        (track, sector) = struct.unpack("<2s2s", sector_address)

        self.track = int(track.decode('ascii'), 16)
        self.sector = int(sector.decode('ascii'), 16)

    def offset(self):
        return self.geometry.offset(self.track, self.sector)

    def last_offset(self):
        return self.offset() + self.geometry.bytes_per_sector - 1

class ErrorMap:
    def __init__(self, raw):
        assert len(raw) >= 128
        assert raw[0:5] == b'ERMAP'

        self.first_defective_track = -1
        self.second_defective_track = -1
        self.defective_record = False

        self._parse(raw)

    def _parse(self, raw):
        if raw[6:8] != b'  ':
            self.first_defective_track = int(raw[6:8].decode('ascii'))

        if raw[10:12] != b'  ':
            self.second_defective_track = int(raw[10:12].decode('ascii'))

        if raw[22] == ord('D'):
            self.defective_record = True

    def has_defective_track(self):
        return self.first_defective_track >= 0

    def has_defective_record(self):
        return self.defective_record

class VolumeLabel:
    def __init__(self, raw):
        assert len(raw) >= 128
        assert raw[0:4] == b'VOL1'

        self.label = ""
        self.locked = False
        self.owner = ""
        self.sides = 1
        self.double_density = False
        self.bytes_per_sector = 128
        self.sector_sequence = 1
        self.label_standard = True

        self._parse(raw)

    def _parse(self, raw):
        # Volume label
        self.label = raw[4:10].decode('ascii').strip()

        # Locked state
        if raw[10] != ord(' '):
            self.locked = True

        # Owner identifier
        self.owner = raw[37:51].decode('ascii').strip()

        # Number of sides and recording density
        if raw[71] == ord('2'):
            self.sides = 2
        elif raw[71] == ord('M'):
            self.sides = 2
            self.double_density = True

        # Bytes per sector
        if raw[75] == ord('1'):
            self.bytes_per_sector = 256
        elif raw[75] == ord('2'):
            self.bytes_per_sector = 512
        elif raw[75] == ord('3'):
            self.bytes_per_sector = 1024

        # Physical sector sequence
        if raw[76:78] != b'  ':
            self.sector_sequence = int(raw[76:78].decode('ascii'))

        # Label standard
        if raw[79] != ord('W'):
            self.label_standard = False

class DataSet:
    def __init__(self, raw, geometry: DiskGeometry):
        assert len(raw) >= 128
        assert raw[0:4] == b'HDR1' or raw[0:4] == b'DDR1'

        self.deleted = False
        self.identifier = ""
        self.block_length = 80
        self.blocked_record = False
        self.spanned_record = False
        self.beginning_of_extent = SectorAddress(geometry)
        self.physical_record_length = 128
        self.end_of_extent = SectorAddress(geometry)
        self.fixed_length = True
        self.bypass = False
        self.restricted = False
        self.write_protect = False
        self.multi_volume = False
        self.sequence_number = -1
        self.creation_date = ""
        self.record_length = self.block_length
        self.expiration_date = ""
        self.end_of_data = SectorAddress(geometry)

        self._parse(raw)

    def _parse(self, raw):
        if raw[0] == ord('D'):
            self.deleted = True

        self.identifier = raw[5:22].decode('ascii').strip()
        self.block_length = int(raw[22:27].decode('ascii').strip())

        if raw[27] == ord('R'):
            self.blocked_record = True
            self.spanned_record = True
        elif raw[27] == ord('B'):
            self.blocked_record = True
            self.spanned_record = False

        self.beginning_of_extent.from_ibm(raw[28:33])
        
        if raw[33] == ord('1'):
            self.physical_record_length = 256
        if raw[33] == ord('2'):
            self.physical_record_length = 512
        if raw[33] == ord('3'):
            self.physical_record_length = 1024

        self.end_of_extent.from_ibm(raw[34:39])

        if raw[39] != ord(' ') and raw[39] != ord('F'):
            self.fixed_length = False

        if raw[40] == ord('B'):
            self.bypass = True

        if raw[41] != ord(' '):
            self.restricted = True

        if raw[42] == ord('P'):
            self.write_protect = True

        if raw[44] == ord('C') or raw[44] == ord('L'):
            self.multi_volume = True

        if raw[45:47] != b'  ':
            self.sequence_number = int(raw[45:47].decode('ascii'))

        if raw[47:53] != b'      ':
            self.creation_date = raw[47:53].decode('ascii').strip()

        if raw[53:57] == b'    ':
            self.record_length = self.block_length
        else:
            self.record_length = int(raw[53:57].decode('ascii').strip())

        if raw[66:72] != b'      ':
            self.expiration_date = raw[66:72].decode('ascii').strip()

        self.end_of_data.from_ibm(raw[74:79])

class EmptyEntry:
    def __init__(self):
        pass

def makeCatalogEntry(geometry: DiskGeometry, raw):
    assert len(raw) >= 128

    if raw[0:5] == b"ERMAP":
        return ErrorMap(raw)

    if raw[0:4] == b"VOL1":
        return VolumeLabel(raw)

    if raw[0:4] == b"HDR1" or raw[0:4] == b"DDR1":
        return DataSet(raw, geometry)

    return EmptyEntry()

class UnitelDisk:
    def __init__(self):
        self.bytes = b''
        self.index = []
        self.geometry = DiskGeometry(tps=74, spt=26, bps=128)

    def get_bytes(self, from_sector: SectorAddress, length: int):
        assert length > 0

        offset = from_sector.offset()
        return self.bytes[offset : offset + length]

    def _read_index(self):
        self.index = []
        for sector in range(1, self.geometry.sectors_per_track + 1):
            entry_addr = SectorAddress(self.geometry, 0, sector)

            entry = self.get_bytes(entry_addr, self.geometry.bytes_per_sector)

            self.index.append(makeCatalogEntry(self.geometry, entry))

    def check_valid_disk(self):
        if not isinstance(self.index[4], ErrorMap):
            raise ValueError("Invalid disk image, error map not found")

        if not isinstance(self.index[6], VolumeLabel):
            raise ValueError("Invalid disk image, volume label not found")

    def load(self, filename):
        # Loads the Unitel EBCDIC bytes
        with open(filename, 'rb') as unitel_file:
            unitel_raw = unitel_file.read()

            if len(unitel_raw) < self.geometry.track_size():
                raise ValueError("Invalid IBM3740 disk image, no catalog")

            # Convert the Unitel EBCDIC bytes to Unitel VDT bytes
            self.bytes = ebcdic_to_vdt(unitel_raw)

        self._read_index()
        self.check_valid_disk()

    def dir(self):
        return [ entry
            for entry in self.index
            if isinstance(entry, DataSet) and not entry.deleted
        ]

    def get_file(self, name):
        try:
            entry = next(x for x in self.dir() if x.identifier == name)

            return self.bytes[
                entry.beginning_of_extent.offset() :
                entry.end_of_extent.offset() + self.geometry.bytes_per_sector
            ]
        except StopIteration:
            raise FileNotFoundError("File not found")

    def diskinfo(self):
        try:
            return next(x for x in self.index if isinstance(x, VolumeLabel))
        except StopIteration:
            raise FileNotFoundError("Volume label not found")

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

                (used, location, length, _) = struct.unpack(
                    "<c4s4s8s", entry[24:41]
                )

                # First digit indicates if the page is used or not
                if used == b'0':
                    continue

                # Values are encoded in hexadecimal
                start = SectorAddress(self.geometry)
                start.from_unitel(location)
                length = int(length.decode('ascii'), 16)

                pages.append((start, length))

        return pages

def show_help():
    print("Unitel - Extract Videotex pages from 8 inches floppy disks.")
    print()
    print("Usage: unitel.py <command> <filename>")
    print()
    print("Commands:")
    print("    - convert: converts EBCDIC disk image to ASCII disk image")
    print("    - diskinfo: display information about the disk image")
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
    elif command == 'diskinfo':
        vlabel = disk.diskinfo()

        print("Information on volume {}:".format(vlabel.label))
        print(" - locked: {}".format(vlabel.locked))
        print(" - owner: {}".format(vlabel.owner))
        print(" - side(s): {}".format(vlabel.sides))
        print(" - double density: {}".format(vlabel.double_density))
        print(" - bytes per sector: {}".format(vlabel.bytes_per_sector))
        print(" - sector sequence: {}".format(vlabel.sector_sequence))
        print(" - label standard: {}".format(vlabel.label_standard))
    elif command == 'listfiles':
        # Gives directory entries with start and end offsets
        print("identifier        start l.end p.end blk ")
        print("----------------- ----- ----- ----- ----")
        for entry in disk.dir():
            print("{:17s} {:05X} {:05X} {:05X} {:4d}".format(
                entry.identifier,
                entry.beginning_of_extent.offset(),
                entry.end_of_extent.last_offset(),
                entry.end_of_data.offset() - 1,
                entry.block_length
            ))
    elif command == 'listpages':
        # List Videotex pages
        print("id  start len  ")
        print("--- ----- -----")
        index = 1
        for (start, length) in disk.catalog():
            print("{:03d} {:05X} {:5d}".format(
                index,
                start.offset(),
                length
            ))
            index += 1
    elif command == 'extract':
        # Extract Videotex pages
        index = 1
        for (start, length) in disk.catalog():
            with open("{}-{:03d}.vdt".format(filename, index), "wb") as output:
                output.write(disk.get_bytes(start, length))

            index += 1

if __name__ == '__main__':
    main(sys.argv)
