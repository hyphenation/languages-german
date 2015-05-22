#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# hyphenate_neueintraege.py: kategorisierte Trennung mit patgen-patterns.
# =======================================================================

u"""Trenne Wörter mittels "hyphenation"-Algorithmus und patgen-patterns¹.

Eingabe: Ein ungetrenntes Wort oder Eintrag im Wortliste-Format pro Zeile.²

Ausgabe: Wortliste-Einträge (Neueintrag;Neu=ein-trag)
         ohne Unterscheidung von Sprachvarianten (!)³
         getrennt nach:
         
         identisch rekonstruiert 
           wenn die vorhandene Trennmarkierung der ermittelten
           entspricht.
         mit Pattern getrennt
           wenn die Eingabe ungetrennt ist oder eine abweichende
           Trennmarkierung aufweist

Bsp: python hyphenate_neueintraege.py < missing-words.txt > neu.todo

     ``neu.todo`` kann (nach Durchsicht!!) mit `prepare_patch.py neu`
     in die Wortliste eingepflegt werden.³

¹ Verwendet Pattern-Dateien welche über die "make" Ziele
  `make pattern-refo`, `make major pattern-refo`, `make fugen pattern-refo`
  und `make suffix pattern-refo` im Wurzelverzeichnis der Wortliste generiert
  werden können (die Fehler bei `make fugen pattern-refo` und `make suffix
  pattern-refo` können ignoriert werden).

² Tip: mit `abgleich_neueintraege.py --filter < neue.txt > wirklich-neue.txt`
  können in der WORTLISTE vorhandene Wörter aussortiert werden.

³ `prepare_patch.py neu` nimmt auch eine Unterscheidung nach de-1901/de-1996
  anhand der wesentlichen Regeländerungen (-st/s-t, ck/c-k, ss/ß)
  vor. (Schweizer Spezialitäten und andere Grenzfälle müssen per Hand
  eingepflegt werden.)
"""

import sys, os, codecs, glob, copy, optparse

# path for local Python modules (parent dir of this file's dir)
sys.path.insert(0, 
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from wortliste import WordFile, WordEntry, join_word, toggle_case, sortkey_duden
from abgleich_neueintraege import print_proposal
import patuse
from patuse.hyphenation import Hyphenator

# Trenne mit Hyphenator::

def trenne(entry):
    key = entry[0]
    parts_fugen = h_fugen.split_word(key)
    parts_major = h_major.split_word(key)
    parts_suffix = h_suffix.split_word(key)
    parts_all = h_all.split_word(key)

    parts = [] # Liste von Silben und Trennzeichen, wird am Ende zusammengefügt.
    p_major = '' # zum Vergleich mit parts_major
    p_fugen = ''
    p_suffix = ''
    # Kategorisierung der Trennstellen
    for part_all in parts_all[:-1]:
        parts.append(part_all)
        p_major += part_all
        p_fugen += part_all
        p_suffix += part_all
        if p_fugen == parts_fugen[0]:
            parts_fugen.pop(0)
            p_fugen = ''
            parts.append(u'=')
        elif p_suffix == parts_suffix[0]:
            parts_suffix.pop(0)
            p_suffix = ''
            parts.append(u'>')
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
    newentry = WordEntry(key + u';' + word)
    newentry.comment = entry.comment
    return newentry


# Hauptfunktion::

if __name__ == '__main__':

# Optionen::

# Die neuesten Pattern-Dateien, welche über die "make"-Ziele
#
#     make pattern-refo
#     make major pattern-refo
#     make fugen pattern-refo
#     make suffix pattern-refo
#
# im Wurzelverzeichnis der wortliste generiert werden::

    p_all = glob.glob('../../../dehyphn-x/dehyphn-x-*.pat')[-1]
    p_major = glob.glob('../../../dehyphn-x-major/dehyphn-x-major-*.pat')[-1]
    p_fugen = glob.glob('../../../dehyphn-x-fugen/dehyphn-x-fugen-*.pat')[-1]
    p_suffix = glob.glob('../../../dehyphn-x-suffix/dehyphn-x-suffix-*.pat')[-1]


    usage = '%prog [Optionen]\n' + __doc__
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-p', '--patterns',
                      help='Pattern-Datei (alle Trennstellen), '
                      'Vorgabe "%s"'%p_all, default=p_all)
    parser.add_option('--patterns_major',
                      help='Pattern-Datei (Trennstellen an Morphemgrenzen), '
                      'Vorgabe "%s"'%p_major, default=p_major)
    parser.add_option('--patterns_fugen',
                      help='Pattern-Datei (Trennstellen an Wortfugen), '
                      'Vorgabe "%s"'%p_fugen, default=p_fugen)
    parser.add_option('--patterns_suffix',
                      help='Pattern-Datei (Trennstellen vor Suffixen), '
                      'Vorgabe "%s"'%p_suffix, default=p_suffix)
    (options, args) = parser.parse_args()

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# Trenner-Instanzen::

    h_all = Hyphenator(options.patterns)
    h_major = Hyphenator(options.patterns_major)
    h_fugen = Hyphenator(options.patterns_fugen)
    h_suffix = Hyphenator(options.patterns_suffix)
    


# Erstellen der neuen Einträge::

    proposals = [WordEntry(line.decode('utf8').strip().replace(u'-', u''))
                 for line in sys.stdin
                 if not line.startswith('#')]

    neue = []

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
