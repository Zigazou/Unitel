Unitel
======

Unitel is a standalone Python3 script that allows you to extract Videotex pages
from an 8 inches floppy disk created on a Unitel application (it probably ran
on an IBM 3740 or something like that).

The filesystem uses the Data Set Record format.

Usage
-----

    unitel.py <command> <filename>

The last parameter is the file name of a Unitel disk image.

Available commands:

    - **convert**: converts EBCDIC disk image to ASCII disk image
    - **listfiles**: list files and offsets
    - **listpages**: list Videotex pages and offsets
    - **extract**: extract all pages into *.vdt files

The first three commands are there for debug purposes.

Example:

    unitel.py extract test.img

will generate files like:

    test-001.img
    test-002.img
    test-003.img
    ...

Technical notes
---------------

### Disk geometry

A Unitel floppy disk has the following geometry:

- single sided
- 81 tracks
- 26 sectors per trak
- 128 bytes per sector

### The disk catalog

The first track is entirely dedicated to the disk catalog.

Each sector of the first track contains one entry.

This means the catalog holds a maximum of 26 entries.

The real number is smaller:

- the first 4 entries are blank
- the 5th entry is ERMAP (error map)
- the 6th entry is blank
- the 7th entry is VOL1IBMIRD with a 'W' in the 80th column
- the 19 remaining entries contains the actual files

With the exception of the 7 first entries, the standard entries use the
following scheme:

- first character: H for a working entry, D for a deleted entry.
- 2nd, 3rd and 4th characters: DR1
- a space
- 17 characters: the file name, padded with spaces on the right
- 3 digit number: 128 or 080 (don't know what it is)
- space
- 5 digit number: start position on the disk
    - 2 digits: track (starting from 1, track 0 is reserved)
    - 1 digit: usually 0 (might be used for sector or side)
    - 2 digits: sector (starting from 1)
- space
- 5 digit number: end position on the disk

### Unitel file organisation

Unitel uses 5 files:

- FICVID: the video pages
- FICSTR: ???
- FICUTI: management pages
- FICMAC: pages location
- FIDEVI: ???

The `FICMAC` file contains the start and length of pages contained in the 
`FICVID` file. It is important to note that the length is mandatory because
the pages are not null terminated.

The numbers are given in hexadecimal contrary to the catalog entries.