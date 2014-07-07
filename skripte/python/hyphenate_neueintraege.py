#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# hyphenate_neueintraege.py: Versuche kategorisierte Trennung
# über "hyphenation"-Algorithmus und patgen-patterns.
# ============================================================



import sys, codecs, glob, copy
from werkzeug import WordFile, WordEntry, join_word, toggle_case, sortkey_duden
from abgleich_neueintraege import print_proposal
from hyphenation import Hyphenator


# Konfiguration
# -------------

# Pfad zur Datei mit den neu einzutragenden Wörtern::

neuwortdatei = "spell/zusatz-de-1996-aspell-compact"
neuwortdatei = "spell/unkategorisiert"
# neuwortdatei = "spell/DDR.txt"


# Die neuesten Pattern-Dateien welche über die "make" Ziele
# `make pattern-refo`, `make major pattern-refo`, `make fugen pattern-refo`
# im Wurzelverzeichnis der wortliste generiert werden::
        
pfile_all = glob.glob('../../dehyphn-x/dehyphn-x-*.pat')[-1]
pfile_major = glob.glob('../../dehyphn-x-major/dehyphn-x-major-*.pat')[-1]
pfile_fugen = glob.glob('../../dehyphn-x-fugen/dehyphn-x-fugen-*.pat')[-1]



# Trenner-Instanzen::

h_all = Hyphenator(pfile_all)
h_major = Hyphenator(pfile_major)
h_fugen = Hyphenator(pfile_fugen)
        

# Trenne mit Hyphenator::

def trenne(entry):
    key = entry[0]
    parts_fugen = h_fugen.split_word(key)
    parts_major = h_major.split_word(key)
    parts_all = h_all.split_word(key)
    
    parts = [] # Liste von Silben und Trennzeichen, wird am Ende zusammengefügt.
    p_major = '' # zum Vergleich mit parts_major
    p_fugen = ''
    # Kategorisierung der Trennstellen
    for part_all in parts_all[:-1]:
        parts.append(part_all)
        p_fugen += part_all
        p_major += part_all
        if p_fugen == parts_fugen[0]:
            parts_fugen.pop(0)
            p_fugen = ''
            parts.append(u'=')
        elif p_major == parts_major[0]:
            parts_major.pop(0)
            p_major = ''
            parts.append(u'<')
        else:
            parts.append(u'-')
    parts.append(parts_all[-1])
    word = u''.join(parts)
    
    # Alternative Kategorisierung über Zerlegung der Teilwörter/Wortteile:
    # word = u'='.join([u'<'.join([h_all.hyphenate_word(part, '-') 
    #                              for part in h_major.split_word(teilwort)])
    #                   for teilwort in h_fugen.split_word(key)])
    return WordEntry(key + u';' + word)

if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

    neue = []

# Erstellen der neuen Einträge::

    proposals = [WordEntry(line.decode('utf8').strip())
                 for line in open(neuwortdatei)
                 if not line.startswith('#')]

    for newentry in proposals:

# Trennen::
    
        entry = trenne(copy.copy(newentry))
        if entry:
            neue.append(entry)


# Vergleich mit Original::

    alle_neuen = dict((entry[0].lower(), entry) for entry in neue)

    identische = {}
    for proposal in proposals:
        key = proposal[0].lower()
        newentry = alle_neuen.get(key)
        if proposal == newentry:
            identische[key] = proposal
        else:
            if newentry:
                newentry.proposal = proposal
                
# Ausgabe::

    print u'\n# identisch rekonstruiert:'
    for entry in sorted(identische.values(), key=sortkey_duden):
        print unicode(entry)

    print u'\n# mit Pattern getrennt'
    for entry in neue:
        print_proposal(entry)
