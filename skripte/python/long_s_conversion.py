#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# long_s_conversion.py: Demonstrator für die Lang-S Wandlung
# =============================================================================

u"""Rund-S nach Lang-S Wandlung über "hyphenation patterns"."""

import sys, codecs, re, optparse
from hyphenation import Hyphenator


# Konfiguration
# -------------

# Die Lang-S Pattern-Dateien welche über "make" Ziele
# im Wurzelverzeichnis der wortliste generiert werden::

pfile = '../../de-Latf/de-1901-Latf.pat'
# pfile = '../../de-Latf/de-1996-Latf.pat'

# Trenner-Instanzen::

# TODO: `pfile` konfigurierbar
h_Latf = Hyphenator(pfile) 


# ſ steht auch am Ende von Abkürzungen, wenn es im abgekürzten Wort steht
# (Abſ. - Abſatz/Abſender, (de)creſc. - (de)creſcendo, daſ. - daſelbst ...)
# s steht auch in der Mitte von Abkürzungen, wenn es im abgekürzten Wort steht
# (Ausg. - Ausgang/Ausgabe, Hrsg. - Herausgeber, ...)
# ::

exceptions = (u'Abſ', # Abſatz/Abſender
              u'Ausg', # Aus<gabe
              u'beſ',  # beſonders
              u'coſ',  # Ko<ſinus
            # u'daſ',   # da<ſelbſt (nicht von Artikel "das" zu unterscheiden!)
              u'desgl', # des<gleichen
              u'Diſſ',  # Diſſertation
              u'hrsg',  # herausgegeben
              u'Hrsg',  # Herausgeber
              u'Hſ',    # Handschrift
              u'Maſſ',  # Maſſachuſetts
            # u'Miſſ',  # Miſſiſippi (nicht von Miſs (Frln.) zu unterscheiden)
              # TODO: N-Z
             )
exceptions = dict((ex.replace(u'ſ', u's'), ex) for ex in exceptions)

# Konvertierung mit Hyphenator::

def transformiere(wort, hyphenator=h_Latf):
    
    if u's' not in wort:
        return wort
    if wort in exceptions:
        return exceptions[wort]
        
    parts = hyphenator.split_word(wort, rmin=1)

    # Wandle in jedem Teil alle klein S zu Lang-S, außer am Schluss:
    parts = [part[:-1].replace(u's', u'ſ') + part[-1] for part in parts]

    return u''.join(parts)

def transformiere_text(text, hyphenator=h_Latf):
    # Text zerlegen: finde (ggf. leere) Folgen von nicht-Wort-Zeichen
    # gefolgt von Wort-Zeichen. Der Iterator liefert Match-Objekte, mit
    # den Untergruppen 0: nicht-Wort und 1: Wort.
    it = re.finditer(r"([\W0-9_]*)(\w*)", text, flags=re.UNICODE)
    # Konvertierung und Zusammenfügen
    parts = [match.groups()[0] # nicht-Wort Zeichen
             + transformiere(match.groups()[1], hyphenator)
             for match in it]
    return u''.join(parts)

if __name__ == '__main__':

    usage = u'%prog [options] [words to be transformed]\n\n' + __doc__

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-f', '--pattern-file', dest='pattern_file',
                      help='Pattern file, Default "%s"' % pfile,
                      default=pfile)
    parser.add_option('-t', '--test', action="store_true", default=False,
                      help='Vergleiche Eingabe mit Rekonstruktion, '
                      'Melde Differenzen.')
                      
    (options, args) = parser.parse_args()

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    if len(args) > 0:
        lines = [u' '.join(args).decode('utf8')]
    else:
        lines = (line.decode('utf8') for line in sys.stdin)
    
    if options.test:
        for line in lines:
            line2 = transformiere_text(line.replace(u'ſ', u's'))
            if line2 != line:
                print line.strip(), '->', line2,
    else:
        for line in lines:
            print transformiere_text(line),
        


