#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich mit Zweig "keine Trennstellen in zweisilbigen Wörtern
# ==================================================================
# ::

from copy import deepcopy
import re, sys
from werkzeug import WordFile, WordEntry, join_word, udiff


if __name__ == '__main__':

# Die Wortlisten::

    # Master als Wörterbuch (dict Instanz):
    wordfile = WordFile('../../wortliste')
    words = wordfile.asdict()

    # Branch "keine Trennstellen ..." als Listen (alt/neu):
    wortfile_gewichtet = WordFile('../../wortliste-gewichtet')
    gewichtet = list(wortfile_gewichtet)
    gewichtet_neu = []

# zusätzliche/andere Einträge in der "gewichteten" Liste::

    for entry in gewichtet:
        key = entry[0]
        if key in words:
            gewichtet_neu.append(entry)
        else:
            if key.lower() in words:
                print '-', entry
                print '+', words[key.lower()]
                gewichtet_neu.append(words[key.lower()])
            elif key.title() in words:
                print '-', entry
                print '+', words[key.title()]
                gewichtet_neu.append(words[key.title()])
            else:
                print '!', entry
                gewichtet_neu.append(entry)


# Einträge die in der "gewichteten" liste fehlen::

    # for entry in
    #     wort = entry[0]
    #     if wort not in gewichtet:
    #         if wort.lower() in gewichtet:
    #             print '-', gewichtet[wort.lower()]
    #         elif wort.title() in gewichtet:
    #             print '-', gewichtet[wort.title()]
    #         print '+', entry


# Patch erstellen::

    patch = udiff(gewichtet, gewichtet_neu, 'wortliste', 'wortliste-neu')
    if patch:
        # print patch
        if wortfile_gewichtet.encoding != 'utf8':
            patch = patch.decode('utf8').encode(wortfile_gewichtet.encoding)
        patchfile = open('../../gewichtet.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print "empty patch"
