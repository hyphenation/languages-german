#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich mit alter Version (Rückgängigmachen von Fehlern).
# ==========================================================
#
# ::

from copy import deepcopy
import re, sys
from werkzeug import WordFile, WordEntry, join_word, udiff


# Master-Wortliste::
    
wordfile = WordFile('../../wortliste')
wortliste = list(wordfile)

# "Original-Liste" vor Beginn der Kategorisierung mit Python-Skripts
# als Wörterbuch::

o_words = WordFile('../../wortliste-original').asdict()

# Sammelbox::

neu = []


# gelöschte Sprachvarianten in der "kategorisierten" Liste
# ---------------------------------------------------------

# Iteration über die aktuelle Liste::

for entry in wortliste:
    
    # entsprechenden "Originaleintrag" holen:
    key = entry[0]
    o_entry = o_words.get(key, [])
    
    # Original hat nicht mehr Sprachvarianten -> so lassen:
    if len(o_entry) <= len(entry):
        neu.append(entry)
        continue
        
    # Gerechtfertigte Bereinigungen (gleiches Wort, gleiche Trennungen aber
    # evt. verschiedene Trennzeichen):
    if len(o_entry) == 4:
        silben1 = re.split(u'[-·._|=]+', o_entry.get('de-1901') or '')
        silben2 = re.split(u'[-·._|=]+', o_entry.get('de-1996') or '')
        if silben1 == silben2:
            if len(entry) == 2:
                print "Bereinigt:", str(o_entry)
            else:
                print "noch offen", str(o_entry)
            neu.append(entry) # so lassen
            continue
    
    # Übernahme des Originaleintrags aber mit traditioneller Schreibung aus
    # aktueller Liste
    o_entry.set(entry.get('de-1901'), 'de-1901')
    neu.append(o_entry)
    # print str(o_entry)

# Patch erstellen::
    
patch = udiff(wortliste, neu, 'wortliste', 'wortliste-neu')
if patch:
    # print patch
    patch = patch.decode('utf8').encode(wordfile.encoding)
    patchfile = open('wortliste.patch', 'w')
    patchfile.write(patch + '\n')
else:
    print "empty patch"
