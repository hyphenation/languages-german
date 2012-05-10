#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2011 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id: $Id:  $

# Abgleich der Trennstellen zwischen Teilwoertern
# ===============================================
#
# Übertragen von kategorisierten Trennstellen von Teilwörtern auf
# Vorkommen dieser Teilwörter mit unkategorisierten Trennstellen.
#
# ::

from copy import deepcopy
import re, sys, codecs
from werkzeug import WordFile, WordEntry, join_word, udiff
from analyse import read_teilwoerter

# Sprachvarianten
# ---------------
# Sprach-Tag nach [BCP47]_::

sprachvariante = 'de-1901'         # "traditionell"
# sprachvariante = 'de-1996'         # Reformschreibung
# sprachvariante = 'de-x-GROSS'      # ohne ß (Großbuchstaben und Kapitälchen)
# sprachvariante = 'de-1901-x-GROSS'   # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS)
# sprachvariante = 'de-CH-1901'     # ohne ß (Schweiz) ("süssauer")



# Funktionen
# -----------
#
# Zerlege ein Wort mit Trennzeichen in eine Liste von Silben und eine Liste
# von Trennzeichen)
#
# >>> from abgleich_teilwoerter import zerlege
#
# >>> zerlege(u'Haupt=stel-le')
# ([u'Haupt', u'stel', u'le'], [u'=', u'-'])
# >>> zerlege(u'Ge|samt||be|triebs=rats==chef')
# ([u'Ge', u'samt', u'be', u'triebs', u'rats', u'chef'], [u'|', u'||', u'|', u'=', u'=='])
#
# ::

def zerlege(wort):
    silben = re.split(u'[-·._|=]+', wort)
    trennzeichen = re.split(u'[^-·._|=]+', wort)
    return silben, [tz for tz in trennzeichen if tz]


# Übertrage die Trennzeichen von `wort1` auf `wort2`:
#
# >>> from abgleich_teilwoerter import uebertrage, TransferError
#
# >>> uebertrage(u'Haupt=stel-le', u'Haupt·stel·le')
# u'Haupt=stel-le'
#
# Auch teilweise Übertragung, von "kategorisiert" nach "unkategorisiert":
#
# >>> print uebertrage(u'Haupt=stel-le', u'Haupt=stel·le')
# Haupt=stel-le
#
# >>> print uebertrage(u'Haupt·stel-le', u'Haupt=stel·le')
# Haupt=stel-le
#
# >>> print uebertrage(u'Aus|stel-ler', u'Aus-stel-ler')
# Aus|stel-ler
#
# >>> print uebertrage(u'Aus|tausch=dien-stes', u'Aus-tausch=diens-tes', False)
# Aus|tausch=diens-tes
#
# Keine Übertragung, wenn die Zahl oder Position der Trennstellen
# unterschiedlich ist oder bei unterschiedlichen Wörtern:
#
# >>> try:
# ...     uebertrage(u'Ha-upt=stel-le', u'Haupt=stel·le')
# ...     uebertrage(u'Haupt=ste-lle', u'Haupt=stel·le')
# ...     uebertrage(u'Waupt=stel-le', u'Haupt=stel·le')
# ... except TransferError:
# ...     pass
#
# Übertragung auch bei unterschiedlicher Schreibung oder Position der
# Trennstellen mit `strict=False` (für Abgleich zwischen Sprachvarianten):
#
# >>> uebertrage(u'er-ster', u'ers·ter', strict=False)
# u'ers-ter'
# >>> uebertrage(u'Fluß=bett', u'Fluss·bett', strict=False)
# u'Fluss=bett'
#
# Auch mit `strict=False` muß die Zahl der Trennstellen übereinstimmen
# (Ausnahmen siehe unten):
#
# >>> try:
# ...     uebertrage(u'Ha-upt=ste-lle', u'Haupt=stel·le', strict=False)
# ... except TransferError:
# ...     pass
#
# Akzeptiere unterschiedliche Anzahl von Trennungen bei st und ck nach
# Selbstlaut:
#
# >>> uebertrage(u'acht=ecki-ge', u'acht·e{ck/k·k}i·ge', strict=False)
# u'acht=e{ck/k-k}i-ge'
# >>> uebertrage(u'As-to-ria', u'Asto·ria', strict=False)
# u'Asto-ria'
# >>> uebertrage(u'Asto-ria', u'As·to·ria', strict=False)
# u'As-to-ria'
# >>> uebertrage(u'So-fa=ecke', u'So·fa=e{ck/k-k}e', strict=False)
# u'So-fa=e{ck/k-k}e'
#
# ::

class TransferError(ValueError):
    def __init__(self, wort1, wort2):
        msg = u'Inkompatibel: %s %s' % (wort1, wort2)
        ValueError.__init__(self, msg.encode('utf8'))
        
    def __unicode__(self):
        return str(self).decode('utf8')

selbstlaute = u'aeiouäöüAEIOUÄÖÜ'

def uebertrage(wort1, wort2, strict=True):

    silben1, trennzeichen1 = zerlege(wort1)
    silben2, trennzeichen2 = zerlege(wort2)
    # Prüfe strikte Übereinstimmung:
    if silben1 != silben2 and strict:
        if u'|' in trennzeichen1 or u'·' in trennzeichen2:
            raise TransferError(wort1, wort2)
        else:
            return wort2
    # Prüfe ungefähre Übereinstimmung:
    if len(trennzeichen1) != len(trennzeichen2):
        # Selbstlaut + st oder ck?
        for s in selbstlaute:
            if (wort2.find(s+u'{ck/k·k}') != -1 or
                wort2.find(s+u'{ck/k-k}') != -1):
                wort1 = wort1.replace(s+u'ck', s+u'-ck')
                silben1, trennzeichen1 = zerlege(wort1)
            if wort2.find(s+u's·t') != -1:
                wort1 = wort1.replace(s+u'st', s+u's-t')
                silben1, trennzeichen1 = zerlege(wort1)
            elif wort1.find(s+u's-t') != -1:
                wort1 = wort1.replace(s+u's-t', s+u'st')
                silben1, trennzeichen1 = zerlege(wort1)
        # immer noch ungleiche Zahl an Trennstellen?
        if len(trennzeichen1) != len(trennzeichen2):
            raise TransferError(wort1, wort2)

    # Baue wort3 aus silben2 und spezifischeren Trennzeichen:
    wort3 = silben2.pop(0)
    for t1,t2 in zip(trennzeichen1, trennzeichen2):
        if (t2 == u'·' and t1 != u'.' # unspezifisch
            or t2 in (u'-', u'|') and t1 in (u'|', u'||')  # Vorsilben
            or t2 in (u'-', u'|', u'||') and t1 in (u'|||')  # Vorsilben
            or t1 in (u'=', u'==')   # Wortfugen
           ):
            wort3 += t1
        else:
            wort3 += t2
        wort3 += silben2.pop(0)
    return wort3

# Großschreibung in Kleinschreibung wandeln und umgekehrt
#
# Diese Version funktioniert auch für Wörter mit Trennzeichen (während
# str.title() nach jedem Trennzeichen wieder groß anfängt)
#
# >>> from abgleich_teilwoerter import toggle_case
# >>> toggle_case(u'Ha-se')
# u'ha-se'
# >>> toggle_case(u'arm')
# u'Arm'
# >>> toggle_case(u'frei=bier')
# u'Frei=bier'
# >>> toggle_case(u'L}a-ger')
# u'l}a-ger'
#
# Keine Änderung bei wörtern mit Großbuchstaben im Inneren:
#
# >>> toggle_case(u'USA')
# u'USA'
#
# >>> toggle_case(u'gri[f-f/{ff/ff')
# u'Gri[f-f/{ff/ff'
# >>> toggle_case(u'Gri[f-f/{ff/ff')
# u'gri[f-f/{ff/ff'

# ::

def toggle_case(wort):
    try:
        key = join_word(wort, assert_complete=True)
    except AssertionError:
        key = wort[0]
    if key.istitle():
        return wort.lower()
    elif key.islower():
        return wort[0].upper() + wort[1:]
    else:
        return wort

# Übertrag kategorisierter Trennstellen aus Teilwort-Datei auf die
# `wortliste`::

def teilwortabgleich(wort, grossklein=False, strict=True):
        teile = [teilabgleich(teil, grossklein, strict)
                 for teil in wort.split(u'=')]
        return u'='.join(teile)

def teilabgleich(teil, grossklein=False, strict=True):
    if grossklein:
        return toggle_case(teilabgleich(toggle_case(teil), strict=strict))
    try:
        key = join_word(teil)
    except AssertionError, e:
        print e
        return teil
    if key not in words.trennungen:
        # print teil, u'not in words'
        return teil
    # Gibt es eine eindeutige Trennung für Teil?
    if len(words.trennungen[key]) > 2:
            print u'Mehrdeutig:', words.trennungen[key]
            # return teil
    for wort in words.trennungen[key]:
        # Übertrag der Trennungen
        try:
            teil = uebertrage(wort, teil, strict)
        except TransferError, e: # Inkompatible Wörter
            print unicode(e)
            
    return teil
    
# Übertrag kategorisierter Trennungen auf Grundwörter mit anderer Endung:
# ::

def grundwortabgleich(wort, endung, vergleichsendung=u''):

    if not wort.endswith(endung):
        return wort

    teile = wort.split('=')
    grundwort = teile[-1]
    stamm = grundwort[:-len(endung)] + vergleichsendung
    key = join_word(stamm)
    # print u' '.join([wort, key])

    if (key in words.trennungen and
        len(words.trennungen[key]) == 1):
        # print u'fundum', key
        try:
            neustamm = uebertrage(words.trennungen[key][0], stamm)
            # Vergleichsendung abtrennen
            if vergleichsendung:
                neustamm = neustamm[:-len(vergleichsendung)]
            # Mit Originalendung einsetzen
            teile[-1] =  neustamm + endung.replace(u'·', u'-')
        except TransferError, e:
            print unicode(e)

    return u'='.join(teile)


# Übertrag kategorisierter Trennstellen zwischen den Feldern aller Einträge
# in `wortliste`::

def sprachabgleich(entry):

    if len(entry) <= 2:
        return # allgemeine Schreibung

    # if u'{' in unicode(entry):
    #     continue # Spezialtrennung
    mit_vorsilbe = None
    gewichtet = None
    ungewichtet = None
    for field in entry[1:]:
        if field.startswith('-'): # -2-, -3-, ...
            continue
        if u'|' in field:
            mit_vorsilbe = field
        elif u'·' not in field:
            gewichtet = field
        else:
            ungewichtet = field
    if mit_vorsilbe and (gewichtet or ungewichtet):
        for i in range(1,len(entry)):
            if entry[i].startswith('-'): # -2-, -3-, ...
                continue
            if u'|' not in entry[i]:
                try:
                    entry[i] = uebertrage(mit_vorsilbe, entry[i], strict=False)
                except TransferError, e:
                    print u'Sprachabgleich:', unicode(e)
        print mit_vorsilbe+u':', unicode(entry)
    elif gewichtet and ungewichtet:
        for i in range(1,len(entry)):
            if u'·' in entry[i]:
                try:
                    entry[i] = uebertrage(gewichtet, entry[i], strict=False)
                except TransferError, e:
                    print unicode(e)
        print gewichtet, str(entry)


# Teste, ob ein Teilwort eine Vorsilbe (oder auch mehrsilbiger Präfix) ist
# und korrigiere die Trennstellenmarkierung::

def vorsilbentest(wort):
    teile = wort.split('=')
    # erstes Teilwort
    if teile[0] in vorsilben:
        return re.sub(r'^%s=' % teile[0], u'%s|' % teile[0], wort)
    # mittlere Teilwörter
    for teil in teile[1:-1]:
        if teil in vorsilben:
            return re.sub(r'=%s=' % teil, u'=%s|' % teil, wort)
    return wort


if __name__ == '__main__':

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# Teilwörter einlesen::

    words = read_teilwoerter(path='teilwoerter-%s.txt'%sprachvariante)

# Tests::

    # for key, value in words.trennungen.iteritems():
    #     if len(value) != 1:
    #         print key, value
    # sys.exit()

    # print grundwortabgleich(u'Aa·chen·ern', u'n')
    # sys.exit()

# Vorsilben (auch mehrsilbige Präfixe)::

    vorsilben = set(line.rstrip().decode('utf8')
                    for line in open('wortteile/vorsilben'))

# `Wortliste` einlesen::

    wordfile = WordFile('../../wortliste') # ≅ 400 000 Einträge/Zeilen
    wortliste = list(wordfile)
    wortliste_alt = deepcopy(wortliste)

# Bearbeiten der wortliste "in-place"::

    for entry in wortliste:

        # Wort mit Trennungen in Sprachvariante
        wort = entry.get(sprachvariante)
        if wort is None: # Wort existiert nicht in der Sprachvariante
            continue

        # if u'·' not in wort: # Alle Trennstellen kategorisiert
        #     continue

# Auswählen der gewünschten Bearbeitungsfunktion durch Ein-/Auskommentieren::

        wort2 = teilwortabgleich(wort, grossklein=False, strict=True)
        # wort2 = grundwortabgleich(wort, endung=u'i-ge',
        #                           vergleichsendung=u'ig')
        # wort2 = vorsilbentest(wort)

        if wort != wort2:
            entry.set(wort2, sprachvariante)
            print u'%s -> %s' % (wort, wort2)
            if len(entry) > 2:
                sprachabgleich(entry)

# Patch erstellen::

    patch = udiff(wortliste_alt, wortliste, 'wortliste', 'wortliste-neu',
                 encoding=wordfile.encoding)
    if patch:
        # print patch
        patchfile = open('wortliste.patch', 'w')
        patchfile.write(patch + '\n')
    else:
        print u'empty patch'
