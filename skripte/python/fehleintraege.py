#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# fehleintraege.py: Fehlerhafte Einträge entfernen
# ================================================

# Erstelle einen Patch zum Entfernen der Einträge aus einer Liste
# von Fehleinträgen (ein Wort oder getrenntes Wort pro Zeile)

from copy import deepcopy
from werkzeug import WordFile, join_word, unified_diff


# Menge der Fehleinträge aus Datei::

fehleintraege = open('fehleintraege.todo').readlines()


fehleintraege = set(join_word(line.decode('utf8').strip()) 
                    for line in fehleintraege)

# print fehleintraege


# Die `Wortliste`::

wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
wortliste = list(wordfile)
wortliste_neu = []

for entry in wortliste:
    if entry[0] not in fehleintraege:
        wortliste_neu.append(entry)



patch = unified_diff(wortliste, wortliste_neu, 'wortliste', 'wortliste-neu')
if patch:
    print patch
    patchfile = open('../../wortliste.patch', 'w')
    patchfile.write(patch + '\n')
else:
    print "empty patch"







