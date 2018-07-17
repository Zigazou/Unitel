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

see the docs directory for technical notes.