#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id:        $Id:  $

# "Korporavergleich (Wortliste vs. diverse Rechtschreibprüfprogramme)
# ===================================================================
# 
# Liste Differenz der Stichproben in der "wortliste" und dem "Dumping" von
# aspell/hunspell.
# 
# ::

import re, sys, codecs, copy
from werkzeug import WordFile, WordEntry, join_word, udiff
# from abgleich_teilwoerter import wortliste_to_teilwoerter

# Konfiguration
# -------------
# 
# Sprachvarianten
# ~~~~~~~~~~~~~~~
# Sprach-Tag nach [BCP47]_::

# sprachvariante = 'de-1901'         # "traditionell"
sprachvariante = 'de-1996'         # Reformschreibung
# sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")

# Vergleichsbasis
# ~~~~~~~~~~~~~~~
# 
# ::

spelldatei = '../../spell/aspell-de-1996-compact'

korrekturdatei = '../../spell/korrekturen'

# Funktionen
# -----------
# ::

if __name__ == '__main__':
    
    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)
   
# `Wortliste` einlesen::

    wordfile = WordFile('../../wortliste')
    words = wordfile.asdict()

# Korrekturen einlesen::

    korrekturen = []
    for line in open(korrekturdatei, 'r'):
        if not line.startswith('-'):
            continue
        # Dekodieren, Zeilenende entfernen
        line = line.decode('utf8')
        korrekturen.append(line[1:].strip())

# Vergleichswörter einlesen::

    for line in open(spelldatei, 'r'):
        # if line.startswith('#'):
        #     continue
        # Dekodieren, Zeilenende entfernen
        line = line.decode('utf8').strip()
        # Tags entfernen (bei "-compact")
        key = line.split(u'/')[0]
        
        # kurze Wörter haben wir nicht:
        if len(key) < 4:
            continue

# Ausgabe "neuer" Wörter::

        if (key not in words 
            and key.lower() not in words 
            and key.title() not in words
            and key not in korrekturen
           ):
            print key
        

