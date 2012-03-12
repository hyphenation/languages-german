#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich der Trennstellen zwischen Sprachvarianten
# ====================================================
# 
# Übertragen von kategorisierten Trennstellen zwischen Sprachvarianten
# desselben Wortes. ::

from copy import deepcopy
import re, sys
from werkzeug import WordFile, WordEntry, join_word, udiff



# Übertrage die (kategorisierten) `trennzeichen` auf das (unkategorisierte)
# `wort`

def uebertrage(trennzeichen, wort):
    silben = wort.split(u'·')
    if len (trennzeichen) != len(silben) -1:
        return wort
    neuwort = silben.pop(0) 
    for t in trennzeichen:
        neuwort += t
        neuwort += silben.pop(0)
    return neuwort     

# Test:

# print uebertrage(u'=-', u'Haupt·stel·le')
# print uebertrage(u'=-', u'Haupt=stel·le').encode('utf8')
# print uebertrage(u'=--', u'Haupt·stel·le').encode('utf8')
# 
# sys.exit()

# Die `Wortliste`::

wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
wortliste = list(wordfile)

wortliste_alt = deepcopy(wortliste)


for entry in wortliste:
    
    if len(entry) <= 2:
        continue # allgemeine Schreibung

    # Felder zusammenfassen:
    entry.conflate_fields()
    continue
    
    if u'{' in unicode(entry):
        continue # Spezialtrennung    
    gewichtet = None
    ungewichtet = None
    for field in entry[1:]:
        if field.startswith('-'): # -2-, -3-, ...
            continue
        trennzeichen = re.sub(u'[^-·._|=]', '', field)
        if u'·' not in trennzeichen:
            gewichtet = trennzeichen
        else:
            ungewichtet = trennzeichen
    if gewichtet is None or ungewichtet is None:
        continue
    
    for i in range(1,len(entry)):
        if u'·' in entry[i]:
            entry[i] = uebertrage(gewichtet, entry[i])
    
    print gewichtet.encode('utf8'), str(entry)
   

# Patch erstellen::

patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu')
if patch:
    print patch
    patchfile = open('../../wortliste.patch', 'w')
    patchfile.write(patch + '\n')
else:
    print "empty patch"
