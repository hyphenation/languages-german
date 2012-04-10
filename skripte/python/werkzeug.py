#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.1 (2012-02-07)

# werkzeug.py
# ***********
#
# ::

"""Hilfsmittel für die Arbeit mit der `Wortliste`"""

# .. contents::
#
# Die hier versammelten Funktionen und Klassen dienen der Arbeit an und
# mit der  freien `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lehmansche Liste")
#
# Vorspann
#
# ::

import difflib
import re

# WordFile
# ========
#
# Klasse zum Lesen und Schreiben der `Wortliste`::

class WordFile(file):

# Argumente
# ---------
#
# encoding
# ~~~~~~~~
#
# Die originale Wortlisten-Datei ist mit 'latin-1' kodiert,
# lokal existiert eine nach utf8 konvertierte Variante::

    encoding = 'utf8'


# readlines
# ---------
#
# Lies die Datei in eine Liste von Zeilen
# (`unicode` Strings ohne Zeilenendezeichen)::

    def readlines(self, keepends=False):

# Lesen als `bytes` String::

        inhalt = self.read()

# Dekodieren: Versuche zunächst 'utf8', bei Fehlern erneut mit 'latin-1'::

        try:
            inhalt = inhalt.decode(self.encoding)
        except UnicodeError:
            if self.encoding != 'latin1':
                self.encoding = 'latin1'
                inhalt = inhalt.decode(self.encoding)
            else:
                raise

# Splitten in eine Liste der Zeilen und zurückgeben::

        inhalt = inhalt.splitlines(keepends)
        if inhalt and not inhalt[-1]:
            # letzte Zeile leer wegen abschließendem \n
            del inhalt[-1]

        return inhalt

# Iteration
# ---------
#
# Die spezielle Funktion `__iter__` wird aufgerufen wenn über eine
# Klasseninstanz iteriert wird.
#
# Liefer einen Iterator über die "geparsten" Zeilen (Datenfelder)::

    def __iter__(self):
        lines = self.readlines()
        for line in lines:
            yield WordEntry(line)

# asdict
# ------
#
# Lies Datei und trage die Zeilen mit ungetrenntem Wort
# als `key` und den Datenfeldern als `value` in ein `dictionary`
# (assoziatives Array) ein::

    def asdict(self):
        words = dict()
        for entry in self:
            words[entry[0]] = entry
        return words

# write_lines
# -----------
#
# Schreibe eine Liste von `unicode` Strings (Zeilen ohne Zeilenendezeichen)
# in die Datei `destination`::

    def writelines(self, lines, destination, encoding=None):
        if encoding is None:
            encoding = self.encoding
        outfile = open(destination, 'w')
        outfile.write(u'\n'.join(lines).encode(encoding))
        outfile.write('\n')

# write_entry
# ------------
#
# Schreibe eine Liste von Datenfeldern (geparste Zeilen) in die Datei
# `destination`::

    def write_entry(self, wortliste, destination, encoding=None):
        lines = [unicode(entry) for entry in wortliste]
        self.writelines(lines, destination, encoding)


# WordEntry
# =========
#
# Klasse für Einträge (Zeilen) der Wortliste
#
# Beispiel:
#
# >>> from werkzeug import WordEntry
#
# >>> aalbestand = WordEntry(u'Aalbestand;Aal=be-stand # Test')
# >>> print aalbestand
# Aalbestand;Aal=be-stand # Test
#
# ::

class WordEntry(list):

# Argumente
# ---------
#
# Kommentare (aktualisiert, wenn Kommentar vorhanden)::

    comment = None

# Feldbelegung:
#
# 1. Wort ungetrennt
# 2. Wort mit Trennungen, falls für alle Varianten identisch,
#    anderenfalls leer
# 3. falls Feld 2 leer, Trennung nach traditioneller Rechtschreibung
# 4. falls Feld 2 leer, Trennung nach reformierter Rechtschreibung (2006)
# 5. falls Feld 2 leer, Trennung für Wortform, die entweder in
#    der Schweiz oder mit Großbuchstaben oder Kapitälchen benutzt wird
#    und für traditionelle und reformierte Rechtschreibung identisch ist
# 6. falls Feld 5 leer, Trennung für Wortform, die entweder in
#    der Schweiz oder mit Großbuchstaben oder Kapitälchen benutzt wird,
#    traditionelle Rechtschreibung
# 7. falls Feld 5 leer, Trennung für Wortform, die entweder in
#    der Schweiz oder mit Großbuchstaben oder Kapitälchen benutzt wird,
#    reformierte Rechtschreibung (2006)
# 8. falls Feld 5 leer, Trennung nach (deutsch)schweizerischer
#    Rechtschreibung; insbesondere Wörter mit "sss" gefolgt von
#    einem Vokal, die wie andere Dreifachkonsonanten gehandhabt wurden
#    (also anders, als der Duden früher vorgeschrieben hat), z.B.
#    "süssauer"
#
# Sprachvarianten (Tags nach [BCP47]_) (Die Zählung der Indizes beginn in
# Python bei 0)::

    sprachvarianten = {
        'de':         1, # Deutsch, allgemeingültig
        'de-1901':    2, # "traditionell" (nach Rechtschreibreform 1901)
        'de-1996':    3, # reformierte Reformschreibung (1996)
        'de-x-GROSS':      4, # ohne ß (Schweiz oder GROSS) allgemein
        'de-1901-x-GROSS': 5, # ohne ß (Schweiz oder GROSS) "traditionell"
        'de-1996-x-GROSS': 6, # ohne ß (Schweiz oder GROSS) "reformiert"
        # 'de-CH-1996':      6, # Alias für 'de-1996-x-GROSS'
        'de-CH-1901':      7, # ohne ß (Schweiz) "traditionell" ("süssauer")
        }


# Initialisierung::

    def __init__(self, line, delimiter=';'):
        self.delimiter = delimiter

# eventuell vorhandenen Kommentar abtrennen,
# Zerlegen in Datenfelder,
# in Liste eintragen::

        if '#' in line:
            line, self.comment = line.split('#')
            line = line.rstrip()

        entry = line.split(delimiter)

# Liste mit Datenfeldern initialisieren::

        list.__init__(self, entry)


# Rückverwandlung in String
# -----------------------------------
#
# Erzeugen eines Eintrag-Strings (Zeile) aus der Liste der Datenfelder und
# dem Kommentar
#
# >>> unicode(aalbestand)
# u'Aalbestand;Aal=be-stand # Test'
#
# ::

    def __unicode__(self):
        line = ';'.join(self)
        if self.comment is not None:
            line += ' #' + self.comment
        return line


    def __str__(self):
        return unicode(self).encode('utf8')

# lang_index
# ---------------
#
# Index des zur Sprachvariante gehörenden Datenfeldes:
#
# >>> aalbestand.lang_index('de')
# 1
# >>> aalbestand.lang_index('de-1901')
# 1
# >>> aalbestand.lang_index('de-1996')
# 1
# >>> abbeissen = WordEntry(
# ...     u'abbeissen;-2-;-3-;-4-;-5-;ab|bei-ssen;ab|beis-sen;ab|beis-sen')
# >>> print abbeissen.lang_index('de')
# None
# >>> print abbeissen.lang_index('de-x-GROSS')
# None
# >>> abbeissen.lang_index('de-CH-1901')
# 7
#
# ::

    def lang_index(self, sprachvariante):

        assert sprachvariante in self.sprachvarianten, \
            'Sprachvariante nicht in ' + str(self.sprachvarianten.keys())

# Einfacher Fall: eine allgemeine Schreibweise::

        if len(self) == 2:
            return 1

# Spezielle Schreibung::

        try:
            i = self.sprachvarianten[sprachvariante]
            feld = self[i]
        except IndexError:
            if i > 4 and len(self) == 5:
                return 4 # Allgemeine Schweiz/GROSS Schreibung:
            return None  # Feld nicht vorhanden

        if feld.startswith('-'):   # '-1-', '-2-', ...
            return None  # leeres Feld

        return i

# Trennmuster für Sprachvariante ausgeben
#
# >>> aalbestand.get('de')
# u'Aal=be-stand'
# >>> aalbestand.get('de-1901')
# u'Aal=be-stand'
# >>> aalbestand.get('de-1996')
# u'Aal=be-stand'
# >>> aalbestand.get('de-x-GROSS')
# u'Aal=be-stand'
# >>> aalbestand.get('de-1901-x-GROSS')
# u'Aal=be-stand'
# >>> aalbestand.get('de-1996-x-GROSS')
# u'Aal=be-stand'
# >>> aalbestand.get('de-CH-1901')
# u'Aal=be-stand'
#
# >>> print abbeissen.get('de')
# None
# >>> print abbeissen.get('de-x-GROSS')
# None
# >>> abbeissen.get('de-1901-x-GROSS')
# u'ab|bei-ssen'
# >>> abbeissen.get('de-CH-1901')
# u'ab|beis-sen'
#
# ::

    def get(self, sprachvariante):
        try:
            return self[self.lang_index(sprachvariante)]
        except TypeError:  # Muster in `sprachvariante` nicht vorhanden
            return None

# Trennmuster für Sprachvariante setzen
#
# >>> abbeissen.set('test', 'de-1901-x-GROSS')
# >>> print abbeissen
# abbeissen;-2-;-3-;-4-;-5-;test;ab|beis-sen;ab|beis-sen
#
# >>> abbeissen.set('test', 'de-1901')
# Traceback (most recent call last):
# ...
# IndexError: kann kein leeres Feld setzen
#
# ::

    def set(self, wort, sprachvariante):
        i = self.lang_index(sprachvariante)
        if i is None:
            raise IndexError, "kann kein leeres Feld setzen"
        self[i] = wort

# Felder für alle Sprachvarianten ausfüllen
#
# >>> print str(aalbestand), len(aalbestand)
# Aalbestand;Aal=be-stand # Test 2
# >>> aalbestand.expand_fields()
# >>> print len(aalbestand)
# 8
# >>> auffrass = WordEntry('auffrass;-2-;-3-;-4-;auf-frass')
# >>> auffrass.expand_fields()
# >>> print auffrass
# auffrass;-2-;-3-;-4-;auf-frass;auf-frass;auf-frass;auf-frass
#
# ::

    def expand_fields(self):
        fields = [self.get(sv) or '-%d-' % (self.sprachvarianten[sv] + 1)
                  for sv in sorted(self.sprachvarianten.keys(),
                                   key=self.sprachvarianten.get)]
        # return fields
        for i, field in enumerate(fields):
            try:
                self[i+1] = field # Feld 1 ist "key" (ungetrennt)
            except IndexError:
                self.append(field)


# Felder für Sprachvarianten zusammenfassen
#
# >>> aalbestand.conflate_fields()
# >>> print aalbestand
# Aalbestand;Aal=be-stand # Test
# >>> auffrass.conflate_fields()
# >>> print auffrass
# auffrass;-2-;-3-;-4-;auf-frass
#
# ::

    def conflate_fields(self):
        if len(self) == 8:
            if self[7] == self[6] == self[5]:
                self[4] = self[5] # umschreiben auf GROSS-allgemein
                self.pop()
                self.pop()
                self.pop()
        if len(self) == 5:
            if self[4] == self[2]: # de-x-GROSS == de-1901
                self.pop()
            else:
                return
        if len(self) >= 4:
            if self[3] == self[2]: # de-1996 == de-1901
                self[1] = self[2] # Umschreiben auf de (allgemein)
                self.pop()
                self.pop()



# Funktionen
# ==========
#
# join_word
# ---------
#
# Trennzeichen entfernen::

def join_word(word, assert_complete=False):

# Einfache Trennzeichen:

# ==  ================================================================
# \·  ungewichtete Trennstelle (solche, wo noch niemand sich um die
#     Gewichtung gekümmert hat)
# \.  unerwünschte Trennstelle (sinnentstellend), z.B. Ur·in.stinkt
#     oder ungünstige Trennstelle (verwirrend), z.B. Atom·en.er·gie
#     in ungewichteten Wörtern
# \=  Haupttrennstelle an Wortfugen (Wort=fu-ge)
# \|  Haupttrennstelle nach Vorsilbe (Vor|sil-be)
# \-  Nebentrennstelle
# ==  ================================================================

# ::

    table = {}
    for char in u'·.=|-_':
        table[ord(char)] = None
    key = word.translate(table)

# Spezielle Trennungen für die traditionelle Rechtschreibung
# (siehe ../../dokumente/dateikopf)::

    if '{' in key or '}' in key:
        key = key.replace(u'{ck/kk}',  u'ck')
        key = key.replace(u'{ck/k',  u'k')
        key = key.replace(u'k}',     u'k')
        # Konsonanthäufungen an Wortfuge: '{xx/xxx}' -> 'xx':
        key = re.sub(ur'\{(.)\1/\1\1\1\}', ur'\1\1', key)
        # schon getrennt: ('{xx/xx' -> 'xx' und 'x}' -> 'x'):
        key = re.sub(ur'\{(.)\1/\1\1$', ur'\1\1', key)
        key = re.sub(ur'^(.)\}', ur'\1', key)

# Trennstellen in doppeldeutigen Wörtern::

    if '[' in key or ']' in key:
        key = re.sub(ur'\[(.+)/\1\]', ur'\1', key)
        # schon getrennt:
        key = re.sub(ur'\[([^/\[]+)$', ur'\1', key)
        key = re.sub(ur'^([^/\]]+)\]', ur'\1', key)

# Test auf verbliebene komplexe Trennstellen::

    if assert_complete:
        for spez in u'[{/}]':
            if  spez in key:
                raise AssertionError('Spezialtrennung %s' % key.encode('utf8'))

    return key


# udiff
# ------------
#
# Vergleiche zwei Sequenzen von `WordEntries`, gib einen "unified diff" als
# Byte-String zurück (weil difflib nicht mit Unicode-Strings arbeiten kann).
#
# Beispiel:
#
# >>> from werkzeug import udiff
# >>> print udiff([abbeissen, aalbestand], [abbeissen], 'alt', 'neu')
# --- alt
# +++ neu
# @@ -1,2 +1 @@
#  abbeissen;-2-;-3-;-4-;-5-;test;ab|beis-sen;ab|beis-sen
# -Aalbestand;Aal=be-stand # Test
#
# ::

def udiff(a, b, fromfile='', tofile='',
          fromfiledate='', tofiledate='', n=1, encoding='utf8'):

    a = [unicode(entry).encode(encoding) for entry in a]
    b = [unicode(entry).encode(encoding) for entry in b]

    diff = difflib.unified_diff(a, b, fromfile, tofile,
                                fromfiledate, tofiledate, n, lineterm='')

    if diff:
        return '\n'.join(diff)
    else:
        return None


# Test
# ====
#
# ::

if __name__ == '__main__':
    import sys

    print "Test der Werkzeuge"

    # wordfile = WordFile('../../wortliste-binnen-s')
    wordfile = WordFile('../../wortliste')
    print 'Dateiobjekt:', wordfile

# Liste der Zeilen mit readlines::

    ##
    # zeilen = wordfile.readlines()
    # print len(zeilen), "Zeilen",
    # print 'Kodierung:', wordfile.encoding  # aktualisiert beim Lesen
    # wordfile.seek(0)            # Pointer zurücksetzen

# Iteration über "geparste" Zeilen (i.e. Datenfelder)::

    ##
    for entry in wordfile:
        # Sprachauswahl:
        wort = entry.get('de-1901')
        if wort is None:
            continue
        # Test der Trennstellentfernung:
        key = join_word(wort)
        if key != entry[0]:
            print ("key %s != %s" % (key, entry[0])).encode('utf8')

    # wordfile.seek(0)            # Pointer zurücksetzen


# Liste der Datenfelder (die Klasseninstanz als Argument für `list` liefert
# den Iterator über die Felder, `list` macht daraus eine Liste)::

    wortliste = list(wordfile)

    print len(wortliste), "Einträge"

    # for entry in wortliste:
    #     # Zeilenrekonstruktion:
    #     if entry[0] == 'beige':
    #         original = u'beige;beige # vgl. Scheiter-bei-ge'
    #         line = unicode(entry)
    #         assert original == line, "Rejoined %s != %s" % (line, ur_line)

    # print "Doppeleinträge (Groß/Klein):"
    # words = set()
    # for entry in wortliste:
    #     wort = entry[0]
    #     if wort.lower() in words or wort.title() in words:
    #         print entry
    #     words.add(wort)


# Ein Wörterbuch (dict Instanz)::

    words = wordfile.asdict()

    print len(words), "Wörterbucheinträge"


# Quellen
# =======
#
# .. [BCP47]  A. Phillips und M. Davis, (Editoren.),
#    `Tags for Identifying Languages`, http://www.rfc-editor.org/rfc/bcp/bcp47.txt
#
# .. _Wortliste der deutschsprachigen Trennmustermannschaft:
#    http://mirrors.ctan.org/language/hyphenation/dehyph-exptl/projektbeschreibung.pdf
#
