#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.1 (2012-02-07)

# wortliste.py
# ***********
#
# ::

"""Hilfsmittel für die Arbeit mit der `Wortliste`"""

# .. contents::
#
# Die hier versammelten Funktionen und Klassen dienen der Arbeit an und
# mit der  freien `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lembergsche Liste")
#
# Vorspann
#
# ::

import difflib
import re
import codecs
import unicodedata

# WordFile
# ========
#
# Klasse zum Lesen und Schreiben der `Wortliste`::

class WordFile(file):

# encoding
# --------
#
# ::

    encoding = 'utf8'

# Iteration
# ---------
#
# Die spezielle Funktion `__iter__` wird aufgerufen wenn über eine
# Klasseninstanz iteriert wird.
#
# Liefer einen Iterator über die "geparsten" Zeilen (Datenfelder)::

    def __iter__(self):
        line = self.readline().rstrip().decode(self.encoding)
        while line:
            yield WordEntry(line)
            line = self.readline().rstrip().decode(self.encoding)

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

# writelines
# -----------
#
# Schreibe eine Liste von `unicode` Strings (Zeilen ohne Zeilenendezeichen)
# in die Datei `destination`::

    def writelines(self, lines, destination, encoding=None):
        outfile = codecs.open(destination, 'w',
                              encoding=(encoding or self.encoding))
        outfile.write(u'\n'.join(lines))
        outfile.write(u'\n')

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
# >>> from wortliste import WordEntry
#
# >>> aalbestand = WordEntry(u'Aalbestand;Aal=be<stand # Test')
# >>> print aalbestand
# Aalbestand;Aal=be<stand # Test
#
# ::

class WordEntry(list):

# Argumente
# ---------
#
# Kommentare (aktualisiert, wenn Kommentar vorhanden)::

    comment = u''

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

# eventuell vorhandenen Kommentar abtrennen und speichern::

        if '#' in line:
            line = line.split(u'#')
            self.comment = u'#'.join(line[1:])
            line = line[0].rstrip()

# Zerlegen in Datenfelder, in Liste eintragen::

        list.__init__(self, line.split(delimiter))


# Rückverwandlung in String
# -----------------------------------
#
# Erzeugen eines Eintrag-Strings (Zeile) aus der Liste der Datenfelder und
# dem Kommentar
#
# >>> unicode(aalbestand)
# u'Aalbestand;Aal=be<stand # Test'
#
# ::

    def __unicode__(self):
        line = ';'.join(self)
        if self.comment:
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
# >>> aalbestand.lang_index('de-x-GROSS')
# 1
# >>> aalbestand.lang_index('de-1901-x-GROSS')
# 1
# >>> aalbestand.lang_index('de-1996-x-GROSS')
# 1
# >>> abbeissen = WordEntry(
# ...     u'abbeissen;-2-;-3-;-4-;-5-;ab<bei-ssen;ab<beis-sen;ab<beis-sen')
# >>> print abbeissen.lang_index('de')
# None
# >>> print abbeissen.lang_index('de-x-GROSS')
# None
# >>> abbeissen.lang_index('de-CH-1901')
# 7
# >>> urlaubstipp = WordEntry(u'Urlaubstipp;-2-;-3-;Ur<laubs=tipp')
# >>> print urlaubstipp.lang_index('de')
# None
# >>> print urlaubstipp.lang_index('de-1901')
# None
# >>> print urlaubstipp.lang_index('de-1996')
# 3
# >>> print urlaubstipp.lang_index('de-x-GROSS')
# None
# >>> print urlaubstipp.lang_index('de-1901-x-GROSS')
# None

# ::

    def lang_index(self, lang):

        assert lang in self.sprachvarianten, \
            'Sprachvariante "%s" nicht in %s' % (lang,
                                self.sprachvarianten.keys())

# Einfacher Fall: eine allgemeine Schreibweise::

        if len(self) == 2:
            return 1

# Spezielle Schreibung::

        try:
            i = self.sprachvarianten[lang]
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
# u'Aal=be<stand'
# >>> aalbestand.get('de-1901')
# u'Aal=be<stand'
# >>> aalbestand.get('de-1996')
# u'Aal=be<stand'
# >>> aalbestand.get('de-x-GROSS')
# u'Aal=be<stand'
# >>> aalbestand.get('de-1901-x-GROSS')
# u'Aal=be<stand'
# >>> aalbestand.get('de-1996-x-GROSS')
# u'Aal=be<stand'
# >>> aalbestand.get('de-CH-1901')
# u'Aal=be<stand'
#
# >>> print abbeissen.get('de')
# None
# >>> print abbeissen.get('de-x-GROSS')
# None
# >>> print abbeissen.get('de,de-x-GROSS')
# None
# >>> abbeissen.get('de-1901-x-GROSS')
# u'ab<bei-ssen'
# >>> abbeissen.get('de,de-1901,de-1901-x-GROSS')
# u'ab<bei-ssen'
# >>> abbeissen.get('de-CH-1901')
# u'ab<beis-sen'
#
# ::

    def get(self, sprachvarianten):
        for lang in sprachvarianten.split(','):
            i = self.lang_index(lang) # integer>0 or None
            if i:
                return self[i]
        return None

# Trennmuster für Sprachvariante setzen
#
# >>> abbeissen.set('test', 'de-1901-x-GROSS')
# >>> print abbeissen
# abbeissen;-2-;-3-;-4-;-5-;test;ab<beis-sen;ab<beis-sen
#
# >>> abbeissen.set('test', 'de-1901')
# Traceback (most recent call last):
# ...
# IndexError: kann kein leeres Feld setzen
#
# >>> abbeissen.set('test', 'de-1901,de-1901-x-GROSS')
# >>> print abbeissen
# abbeissen;-2-;-3-;-4-;-5-;test;ab<beis-sen;ab<beis-sen
#
# ::

    def set(self, wort, sprachvarianten):
        for lang in sprachvarianten.split(','):
            i = self.lang_index(lang)
            if i is None:
                continue
            if wort is None:
                wort = u'-%d-' % i+1
            self[i] = wort
            return
        raise IndexError, "kann kein leeres Feld setzen"

# Felder für alle Sprachvarianten ausfüllen
#
# >>> print str(aalbestand), len(aalbestand)
# Aalbestand;Aal=be<stand # Test 2
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
# Aalbestand;Aal=be<stand # Test
# >>> auffrass.conflate_fields()
# >>> print auffrass
# auffrass;-2-;-3-;-4-;auf-frass
# >>> entry = WordEntry(u'distanziert;-2-;di-stan-ziert;di-stan-ziert')
# >>> entry.conflate_fields()
# >>> print entry
# distanziert;di-stan-ziert
#
# Aber nicht, wenn die Trennstellen sich unterscheiden:
#
# >>> abenddienste = WordEntry(
# ...    u'Abenddienste;-2-;Abend=dien-ste;Abend=diens-te')
# >>> abenddienste.conflate_fields()
# >>> print abenddienste
# Abenddienste;-2-;Abend=dien-ste;Abend=diens-te
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


# Prüfe auf Vorkommen von Regeländerungen der Orthographiereform 1996.
#
# >>> entry = WordEntry(u'Würste;Wür-ste')
# >>> entry.regelaenderungen()
# >>> print unicode(entry)
# Würste;-2-;Wür-ste;Würs-te
# >>> entry = WordEntry(u'Würste;Würs-te')
# >>> entry.regelaenderungen()
# >>> print unicode(entry)
# Würste;-2-;Wür-ste;Würs-te
# >>> entry = WordEntry(u'Hecke;He-cke')
# >>> entry.regelaenderungen()
# >>> print unicode(entry)
# Hecke;-2-;He{ck/k-k}e;He-cke
# >>> entry = WordEntry(u'Ligusterhecke;Ligu-ster=he{ck/k-k}e')
# >>> entry.regelaenderungen()
# >>> print unicode(entry)
# Ligusterhecke;-2-;Ligu-ster=he{ck/k-k}e;Ligus-ter=he-cke
# >>> entry = WordEntry(u'Hass;Hass')
# >>> entry.regelaenderungen()
# >>> print unicode(entry)
# Hass;-2-;-3-;Hass;Hass
# >>> entry = WordEntry(u'fasst;fasst')
# >>> entry.regelaenderungen()
# >>> print unicode(entry)
# fasst;-2-;-3-;fasst;fasst
# >>> entry = WordEntry(u'Missbrauch;Miss<brauch')
# >>> entry.regelaenderungen()
# >>> print unicode(entry)
# Missbrauch;-2-;-3-;Miss<brauch;Miss<brauch
# >>> entry = WordEntry(u'schlifffest;schliff=fest')
# >>> entry.regelaenderungen()
# >>> print unicode(entry)
# schlifffest;-2-;-3-;schliff=fest
#
# ::

    def regelaenderungen(self):
        # Trennregeländerungen:
        r1901 = (u'-st', u'{ck/k-k}')
        r1996 = (u's-t', u'-ck')

        w1901 = self.get('de-1901')
        w1996 = self.get('de-1996')
        w_x_GROSS = None

        if w1901 is None or w1996 is None:
            return

        for r1, r2 in zip(r1901, r1996):
            w1901 = w1901.replace(r2,r1)
            w1996 = w1996.replace(r1,r2)

        # kein Schluss-ss und sst in de-1901 (ungetrenntes "ss" nur in Ausnahmen)
        # aber: 'ßt' und Schluß-ß auch in de-1996 möglich (langer Vokal)
        if u'ss' in w1901:
            w_x_GROSS = w1901
            w1901 = None

        # Dreikonsonantenregel:
        if w1901 and re.search(ur'(.)\1=\1', w1901):
            w1901 = None

        # Speichern:
        if w1901 == w1996: # keine Regeländerung im Wort
            if len(self) > 2:
                self.conflate_fields()
            return

        if w1901 is None:
            self.extend( ['']*(4-len(self)) )
            self[1] = u'-2-'
            self[2] = u'-3-'
            self[3] = w1996
        else:
            self.extend( ['']*(4-len(self)) )
            self[1] = u'-2-'
            self[2] = w1901
            self[3] = w1996
        if w_x_GROSS:
            self.append(w_x_GROSS)



# Funktionen
# ==========
#
# join_word
# ---------
#
# Trennzeichen entfernen::

def join_word(word, assert_complete=False):

# Einfache Trennzeichen:
#
# ==  ================================================================
# \·  ungewichtete Trennstelle (solche, wo sich noch niemand um die
#     Gewichtung gekümmert hat)
# \.  unerwünschte Trennstelle (sinnentstellend), z.B. Ur·in.stinkt
#     oder ungünstige Trennstelle (verwirrend), z.B. Atom·en.er·gie
#     in ungewichteten Wörtern
# \=  Trennstelle an Wortfugen (Wort=fu-ge)
# \<  Trennstelle nach Präfix  (Vor<sil-be)
# \>  Trennstelle vor Suffix   (Freund>schaf-ten)
# \-  Nebentrennstelle         (ge-hen)
# ==  ================================================================
#
# ::

    table = {}
    for char in u'·.=|-_<>':
        table[ord(char)] = None
    key = word.translate(table)

# Spezielle Trennungen für die traditionelle Rechtschreibung
# (siehe ../../dokumente/README.wortliste)::

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
        key = re.sub(ur'\[(.*)/\1\]', ur'\1', key)
        # schon getrennt:
        key = re.sub(ur'\[([^/\[]+)$', ur'\1', key)
        key = re.sub(ur'^([^/\]]+)\]', ur'\1', key)

# Test auf verbliebene komplexe Trennstellen::

    if assert_complete:
        for spez in u'[{/}]':
            if  spez in key:
                raise AssertionError('Spezialtrennung %s, %s' %
                                     (word.encode('utf8'), key.encode('utf8')))

    return key

# zerlege
# -------
#
# Zerlege ein Wort mit Trennzeichen in eine Liste von Silben und eine Liste
# von Trennzeichen)
#
# >>> from wortliste import zerlege
#
# >>> zerlege(u'Haupt=stel-le')
# ([u'Haupt', u'stel', u'le'], [u'=', u'-'])
# >>> zerlege(u'Ge<samt=be<triebs=rats==chef')
# ([u'Ge', u'samt', u'be', u'triebs', u'rats', u'chef'], [u'<', u'=', u'<', u'=', u'=='])
# >>> zerlege(u'an<stands>los')
# ([u'an', u'stands', u'los'], [u'<', u'>'])
# >>> zerlege(u'An<al.pha-bet')
# ([u'An', u'al', u'pha', u'bet'], [u'<', u'.', u'-'])
#
# ::

def zerlege(wort):
    silben = re.split(u'[-·._<>=]+', wort)
    trennzeichen = re.split(u'[^-·._|<>=]+', wort)
    return silben, [tz for tz in trennzeichen if tz]

# TransferError
# -------------
#
# Fehler beim Übertragen von Trennstellen mit uebertrage_::

class TransferError(ValueError):
    def __init__(self, wort1, wort2):
        msg = u'Inkompatibel: %s %s' % (wort1, wort2)
        ValueError.__init__(self, msg.encode('utf8'))

    def __unicode__(self):
        return str(self).decode('utf8')


# uebertrage
# ----------
#
# Übertrage die Trennzeichen von `wort1` auf `wort2`:
#
# >>> from wortliste import uebertrage, TransferError
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
# >>> print uebertrage(u'Aus<stel-ler', u'Aus-stel-ler')
# Aus<stel-ler
#
# >>> print uebertrage(u'Freund>schaf·ten', u'Freund-schaf-ten')
# Freund>schaf-ten
#
# Übertragung doppelter Marker:
#
# >>> print uebertrage(u'ver<<aus<ga-be',  u'ver<aus<ga-be')
# ver<<aus<ga-be
#
# >>> print uebertrage(u'freund>lich>>keit',  u'freund>lich>keit')
# freund>lich>>keit

# >>> print uebertrage(u'Amts==haupt=stel-le', u'Amts=haupt=stel-le')
# Amts==haupt=stel-le

# Kein Überschreiben doppelter Marker:
# >>> print uebertrage(u'ver<aus<ga-be',  u'ver<<aus<ga-be')
# ver<<aus<ga-be
#
# >>> print uebertrage(u'Amts=haupt=stel-le', u'Amts==haupt=stel·le')
# Amts==haupt=stel-le
#
# Erhalt des Markers für ungünstige Stellen:
# >>> print uebertrage(u'An·al.pha·bet', u'An<al.pha-bet')
# An<al.pha-bet
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
# >>> uebertrage(u'ab>bei-ßen', u'ab>beis·sen', strict=False)
# u'ab>beis-sen'
# >>> print uebertrage(u'Aus<tausch=dien-stes', u'Aus-tausch=diens-tes', False)
# Aus<tausch=diens-tes
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
# >>> uebertrage(u'Drei=ecks=ecke', u'Drei=ecks==e{ck/k-k}e', strict=False)
# u'Drei=ecks==e{ck/k-k}e'
#
# Mit ``upgrade=False`` werden nur unspezifische Trennstellen überschrieben:
#
# >>> print uebertrage(u'an=stel-le', u'an<stel·le', upgrade=False)
# an<stel-le
#
# >>> print uebertrage(u'Aus<stel-ler', u'Aus-stel-ler', upgrade=False)
# Aus-stel-ler
#
# >>> print uebertrage(u'Aus-stel-ler', u'Aus<stel-ler', upgrade=False)
# Aus<stel-ler
#
# >>> print uebertrage(u'vor<an<<stel-le', u'vor-an<stel·le', upgrade=False)
# vor-an<stel-le
#
# ::

selbstlaute = u'aeiouäöüAEIOUÄÖÜ'

def uebertrage(wort1, wort2, strict=True, upgrade=True):

    silben1, trennzeichen1 = zerlege(wort1)
    silben2, trennzeichen2 = zerlege(wort2)
    # Prüfe strikte Übereinstimmung:
    if silben1 != silben2 and strict:
        if u'<' in trennzeichen1 or u'·' in trennzeichen2:
            raise TransferError(wort1, wort2)
        else:
            return wort2
    # Prüfe ungefähre Übereinstimmung:
    if len(trennzeichen1) != len(trennzeichen2):
        # Selbstlaut + st oder ck?
        for s in selbstlaute:
            if (wort2.find(s+u'{ck/k·k}') != -1 or
                wort2.find(s+u'{ck/k-k}') != -1):
                wort1 = re.sub(u'%sck([%s])'%(s,selbstlaute),
                               ur'%s-ck\1'%s, wort1)
                silben1, trennzeichen1 = zerlege(wort1)
            if wort2.find(s+u's·t') != -1:
                wort1 = wort1.replace(s+u'st', s+u's-t')
                silben1, trennzeichen1 = zerlege(wort1)
            elif wort1.find(s+u's-t') != -1:
                wort1 = wort1.replace(s+u's-t', s+u'st')
                silben1, trennzeichen1 = zerlege(wort1)
                # print u'retry:', silben1, trennzeichen1
        # immer noch ungleiche Zahl an Trennstellen?
        if len(trennzeichen1) != len(trennzeichen2):
            raise TransferError(wort1, wort2)

    # Baue wort3 aus silben2 und spezifischeren Trennzeichen:
    wort3 = silben2.pop(0)
    for t1,t2 in zip(trennzeichen1, trennzeichen2):
        if ((t2 == u'·' and t1 != u'.') # unspezifisch
            or upgrade and
            ((t2 in (u'-', u'<') and t1 in (u'<', u'<<', u'<=')) # Praefixe
             or (t2 in (u'-', u'>') and t1 in (u'>', u'>>', u'=>')) # Suffixe
             or (t2 in (u'-', u'=') and t1 in (u'=', u'==', u'===')) # W-fugen
            )
           ):
            wort3 += t1
        elif t2 == u'.' and t1 not in u'·.':
            wort3 += t1 + t2
        else:
            wort3 += t2
        wort3 += silben2.pop(0)
    return wort3


# Übertrag kategorisierter Trennstellen zwischen den Feldern aller Einträge
# in `wortliste`::

def sprachabgleich(entry, vorbildentry=None):

    if len(entry) <= 2:
        return # allgemeine Schreibung

    mit_affix = None       # < oder >
    kategorisiert = None   # kein ·
    unkategorisiert = None # mindestens ein ·
    gewichtet = None       # == oder <= oder =>
    for field in entry[1:]:
        if field.startswith('-'): # -2-, -3-, ...
            continue
        if u'{' in field and u'[' in field: # Bi-ber==be[t=t/{tt/tt=t}]uch
            continue # zu komplex
        if u'·' in field:
            unkategorisiert = field
        elif u'<' in field or u'>' in field:
            mit_affix = field
        else:
            kategorisiert = field
        if u'==' in field or u'<=' in field or u'=>' in field:
            gewichtet = field
    if vorbildentry:
        for field in vorbildentry[1:]:
            if field.startswith('-'): # -2-, -3-, ...
                continue
            if u'{' in field and u'[' in field: # Bi-ber==be[t=t/{tt/tt=t}]uch
                continue # zu komplex
            if not mit_affix and u'<' in field or u'>' in field :
                mit_affix = field
            elif not kategorisiert and unkategorisiert and u'·' not in field:
                kategorisiert = field
            if not gewichtet and u'==' in field or u'<=' in field or u'=>' in field:
                gewichtet = field
        # print 've:', mit_affix, kategorisiert, unkategorisiert
    if mit_affix and (kategorisiert or unkategorisiert or gewichtet):
        for i in range(1,len(entry)):
            if entry[i].startswith('-'): # -2-, -3-, ...
                continue
            if u'<' not in entry[i] or u'·' in entry[i]:
                try:
                    entry[i] = uebertrage(mit_affix, entry[i], strict=False)
                except TransferError, e:
                    if not '/' in entry[i]:
                        print u'Sprachabgleich:', unicode(e)
        # print mit_affix+u':', unicode(entry)
    elif kategorisiert and unkategorisiert:
        for i in range(1,len(entry)):
            if u'·' in entry[i]:
                try:
                    entry[i] = uebertrage(kategorisiert, entry[i], strict=False)
                except TransferError, e:
                    print u'Sprachabgleich:', unicode(e)
        # print kategorisiert, unicode(entry)
    elif gewichtet:
        for i in range(1,len(entry)):
            if u'=' in entry[i] and not (
                                u'{' in entry[i] and u'[' in entry[i]):
                try:
                    entry[i] = uebertrage(gewichtet, entry[i], strict=False)
                except TransferError, e:
                    print u'Sprachabgleich:', unicode(e)



# Großschreibung in Kleinschreibung wandeln und umgekehrt
#
# Diese Version funktioniert auch für Wörter mit Trennzeichen (während
# str.title() nach jedem Trennzeichen wieder groß anfängt)
#
# >>> from wortliste import toggle_case
# >>> toggle_case(u'Ha-se')
# u'ha-se'
# >>> toggle_case(u'arm')
# u'Arm'
# >>> toggle_case(u'frei=bier')
# u'Frei=bier'
# >>> toggle_case(u'L}a-ger')
# u'l}a-ger'
#
# Keine Änderung bei Wörtern mit Großbuchstaben im Inneren:
#
# >>> toggle_case(u'USA')
# u'USA'
# >>> toggle_case(u'iRFD')
# u'iRFD'
#
# >>> toggle_case(u'gri[f-f/{ff/ff')
# u'Gri[f-f/{ff/ff'
# >>> toggle_case(u'Gri[f-f/{ff/ff')
# u'gri[f-f/{ff/ff'
#
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

# Sortierschlüssel
# ================
#
# Duden-Sortierung für die Wortliste
#
# >>> from wortliste import sortkey_duden
# >>> sortkey_duden([u"Abflußröhren"])
# u'abflussrohren a*bflu*szroehren'
# >>> sortkey_duden([u"Abflußrohren"])
# u'abflussrohren a*bflu*szro*hren'
# >>> sortkey_duden([u"Abflussrohren"])
# u'abflussrohren'
#
# >>> s = sorted([[u"Abflußröhren"], [u"Abflußrohren"], [u"Abflussrohren"]],
# ...            key=sortkey_duden)
# >>> print ', '.join(e[0] for e in s)
# Abflussrohren, Abflußrohren, Abflußröhren
#
# Umschreibung
#
# Ligaturen auflösen und andere "normalisierunde" Ersetzungen für den
# (Haupt-)Sortierschlüssel (Akzente werden über ``unicodedata.normalize``
# entfernt)::

umschrift_skey = {
                  ord(u'æ'): u'ae',
                  ord(u'œ'): u'oe',
                  ord(u'ſ'): u's',
                 }

# "Zweitschlüssel" zur Unterscheidung von Umlauten/SZ und Basisbuchstaben::

umschrift_subkey = {
                    ord(u'a'): u'a*',
                    ord(u'å'): u'aa',
                    ord(u'ä'): u'ae',
                    ord(u'o'): u'o*',
                    ord(u'ö'): u'oe',
                    ord(u'ø'): u'oe',
                    ord(u'u'): u'u*',
                    ord(u'ü'): u'ue',
                    ord(u'ß'): u'sz',
                   }


# sortkey_duden
# -------------
#
# Sortiere nach erstem Feld, alphabetisch gemäß Duden-Regeln::

def sortkey_duden(entry):

# Sortieren nach erstem Feld (ungetrenntes Wort)::

    key = entry[0]

    if len(entry) == 1:  # ein Muster pro Zeile, siehe z.B. pre-1901
        key = join_word(key)

# Großschreibung ignorieren:
#
# Der Duden sortiert Wörter, die sich nur in der Großschreibung unterscheiden
# "klein vor groß" (ASCII sortiert "groß vor klein"). In der
# `Trennmuster-Wortliste` kommen Wörter nur mit der häufiger anzutreffenden
# Großschreibung vor, denn der TeX-Trennalgorithmus ignoriert Großschreibung.
# ::

    key = key.lower()

# Ersetzungen:
#
# ß -> ss ::

    skey = key.replace(u'ß', u'ss')

# Restliche Akzente weglassen: Wandeln in Darstellung von Buchstaben mit
# Akzent als "Grundzeichen + kombinierender Akzent". Anschließend alle
# nicht-ASCII-Zeichen ignorieren::

    skey = skey.translate(umschrift_skey)
    skey = unicodedata.normalize('NFKD', skey)
    skey = unicode(skey.encode('ascii', 'ignore'))

# "Zweitschlüssel" für das eindeutige Einsortieren von Wörtern mit
# gleichem Schlüssel (Masse/Maße, waren/wären, ...):
#
# * "*" nach aou für die Unterscheidung Grund-/Umlaut
# * ß->sz
#
# ::

    if key != skey:
        subkey = key.translate(umschrift_subkey)
        skey = u'%s %s' % (skey,subkey)

# Gib den Sortierschlüssel zurück::

    return skey



# udiff
# ------------
#
# Vergleiche zwei Sequenzen von `WordEntries`, gib einen "unified diff" als
# Byte-String zurück (weil difflib nicht mit Unicode-Strings arbeiten kann).
#
# Beispiel:
#
# >>> from wortliste import udiff
# >>> print udiff([abbeissen, aalbestand], [abbeissen], 'alt', 'neu')
# --- alt
# +++ neu
# @@ -1,2 +1 @@
#  abbeissen;-2-;-3-;-4-;-5-;test;ab<beis-sen;ab<beis-sen
# -Aalbestand;Aal=be<stand # Test
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


def test_keys(wortliste):
    """Teste Übereinstimmung des ungetrennten Wortes in Feld 1
    mit den Trennmustern nach Entfernen der Trennmarker.
    Schreibe Inkonsistenzen auf die Standardausgabe.

    `wortliste` ist ein Iterator über die Einträge (Klasse `WordEntry`)
    """
    is_OK = True
    for entry in wortliste:
        # Test der Übereinstimmung ungetrenntes/getrenntes Wort
        # für alle Felder:
        key = entry[0]
        for wort in entry[1:]:
            if wort.startswith(u'-'): # leere Felder
                continue
            if key != join_word(wort):
                is_OK = False
                print u"\nkey '%s' != join_word('%s')" % (key, wort),
                if key.lower() == join_word(wort).lower():
                    print(u"  Abgleich der Großschreibung mit"
                          u"`prepare-patch.py grossabgleich`."),
    return is_OK


# Test
# ====
#
# ::

if __name__ == '__main__':
    import sys

    # sys.stdout mit UTF8 encoding (wie in Python 3)
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

    print u"Test der Werkzeuge und inneren Konsistenz der Wortliste\n"

    wordfile = WordFile('../../../wortliste')
    # print 'Dateiobjekt:', wordfile

# Liste der Datenfelder (die Klasseninstanz als Argument für `list` liefert
# den Iterator über die Felder, `list` macht daraus eine Liste)::

    wortliste = list(wordfile)
    print len(wortliste), u"Einträge\n"

# Sprachauswahl::

    # Sprachtags:
    #
    # sprache = 'de-1901' # traditionell
    # sprache = 'de-1996' # Reformschreibung
    # sprache = 'de-x-GROSS'      # ohne ß (Schweiz oder GROSS) allgemein
    # sprache = 'de-1901-x-GROSS' # ohne ß (Schweiz oder GROSS) "traditionell"
    # sprache = 'de-1996-x-GROSS' # ohne ß (Schweiz oder GROSS) "reformiert"
    # sprache = 'de-CH-1901'      # ohne ß (Schweiz) "traditionell" ("süssauer")
    #
    # worte = [entry.get(sprache) for entry in wortliste if wort is not None]
    # print len(worte), u"Einträge für Sprachvariante", sprache


# Test keys::

    print u"Teste Schlüssel-Trennmuster-Übereinstimmung:",
    if test_keys(wortliste):
        print u"OK",
    print

# Doppeleinträge::

    doppelte = 0
    words = set()
    for entry in wortliste:
        key = entry[0].lower()
        if key in words:
            doppelte += 1
            print unicode(entry)
        words.add(key)
    print doppelte,
    print u"Doppeleinträge (ohne Berücksichtigung der Großschreibung)."
    if doppelte:
        print u"  Entfernen mit `prepare-patch.py doppelte`."
        print u"  Patch vor Anwendung durchsehen!"


# Ein Wörterbuch (dict Instanz)::

    # wordfile.seek(0)            # Pointer zurücksetzen
    # words = wordfile.asdict()
    #
    # print len(words), u"Wörterbucheinträge"

# Zeilenrekonstruktion::

    # am Beispiel der Scheiterbeige:
    # original = u'beige;beige # vgl. Scheiter-bei-ge'
    # entry = words[u"beige"]
    # line = unicode(entry)
    # assert original == line, "Rejoined %s != %s" % (line, original)

    # komplett:
    wordfile.seek(0)            # Pointer zurücksetzen
    OK = 0
    line = wordfile.readline().rstrip().decode(wordfile.encoding)
    while line:
        entry = WordEntry(line)
        if line == unicode(entry):
            OK +=1
        else:
            print u'-', line,
            print u'+', unicode(entry)
        line = wordfile.readline().rstrip().decode(wordfile.encoding)

    print OK, u"Einträge rekonstruiert"



# Quellen
# =======
#
# .. [BCP47]  A. Phillips und M. Davis, (Editoren.),
#    `Tags for Identifying Languages`, http://www.rfc-editor.org/rfc/bcp/bcp47.txt
#
# .. _Wortliste der deutschsprachigen Trennmustermannschaft:
#    http://mirrors.ctan.org/language/hyphenation/dehyph-exptl/projektbeschreibung.pdf
