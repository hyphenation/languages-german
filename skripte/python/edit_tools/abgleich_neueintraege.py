#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2014 Günter Milde.
#             Released without warranty under the terms of the
#             GNU General Public License (v. 2 or later)
# :Id:        $Id:  $

# Versuche Trennstellen neuer Wörter aus vorhandenen zu ermitteln
# ===============================================================

u"""Trenne neue Wörter durch Ableitung von Einträgen der Wortliste.

Eingabe: 1 ungetrenntes Wort oder Eintrag im Wortliste-Format pro Zeile.

Ausgabe: Wortliste-Einträge (Vorschläge), sortiert nach:
  identisch (falls Eingabe bereits Wortliste-Eintrag ist und eindeutig ist), 
  eindeutig abgeleitet
  eindeutig abgeleitet (andere Großschreibung),
  mehrdeutig abgeleitet,
  Rest.
  
Bsp: python abgleich_neueintraege.py < dict-fail.txt > todo.txt

     (``neu.todo`` kann (nach Durchsicht!!) mit `prepare_patch.py neu` 
     in die Wortliste eingepflegt werden.)
"""

# ::

import sys, os, codecs, optparse
from collections import defaultdict  # Wörterbuch mit Default
from wortliste import WordFile, WordEntry, join_word, toggle_case, sortkey_duden
from expand_teilwoerter import expand_wordfile

# Funktionen
# -----------

# Übertrag von Praefixen auf Wörter ohne Präfix::

def praefixabgleich(key, praefix, grossklein=False):

    if key.istitle():
        praefix = praefix.title()

    if not key.startswith(join_word(praefix)):
        return ''

    altkey = key[len(join_word(praefix)):]

    if grossklein:
        altkey = toggle_case(altkey)

    try:
        altentry = words[altkey]
    except KeyError:
        return ''

    entry = WordEntry(key)
    # print "fundum", key, unicode(entry)
    for wort in altentry[1:]:
        if not wort.startswith(u'-'):
            wort = wort.lower()
            wort = u'<'.join([praefix, wort])
        entry.append(wort)

    return entry

praefixe = [u'abo',
            u'ab',
            u'ab<zu',
            u'auf<zu',
            u'aus<zu',
            u'ein<zu',
            u'mit<zu',
            u'um<zu',
            u'un-ter<zu',
            u'weg<zu',
            u'aber',
            u'ad',
            u'aero',
            u'af-ro',
            u'ag-ro',
            u'al-lergo',
            u'al-lein',
            u'all',
            u'als',
            u'am-bi',
            u'ami-no',
            u'an-dro',
            u'an-gio',
            u'an-thro-po',
            u'an-ti',
            u'ang-lo',
            u'an',
            u'apo',
            u'ar-chaeo',
            u'ar-che',
            u'ar-chäo',
            u'ar-terio',
            u'ar-thro',
            u'asyn',
            u'at-mo',
            u'au-ßer',
            u'auf',
            u'aus',
            u'aus<zu',
            u'aut',
            u'ba-ro',
            u'bak-te-rio',
            u'be',
            u'bei',
            u'ben-zo',
            u'bi-blio',
            u'bio',
            u'che-mo',
            u'chi-ro',
            u'chlo-ro',
            u'cho-reo',
            u'chro-mo',
            u'chro-no',
            u'cy-ano',
            u'dar',
            u'de-ka',
            u'de-zi',
            u'demo',
            u'der-ma-to',
            u'des',
            u'di-cho',
            u'di-no',
            u'dia',
            u'dis',
            u'dis-ko',
            u'down',
            u'drein',
            u'durch',
            u'dys',
            u'e-tho',
            u'ego',
            u'ein',
            u'elek-tro',
            u'em-por',
            u'emp',
            u'en-do',
            u'en-te-ro',
            u'ent',
            u'epi',
            u'er-go',
            u'er',
            u'es-chato',
            u'eth-no',
            u'ety-mo',
            u'ext-ro',
            u'ex',
            u'fe-ro',
            u'fem-to',
            u'fer-ro',
            u'fo-no',
            u'fort',
            u'fran-ko',
            u'für',
            u'ga-so',
            u'ge-gen',
            u'ge-no',
            u'ge-ron-to',
            u'geo',
            u'ge',
            u'gi-ga',
            u'gi-gan-to',
            u'go-no',
            u'gra-fo',
            u'gra-pho',
            u'gy-nä-ko',
            u'he-lio',
            u'he-te-ro',
            u'he-xa',
            u'hek-to',
            u'hekt',
            u'hemi',
            u'her',
            u'hier',
            u'hin',
            u'hin-ter',
            u'hint',
            u'ho-lo',
            u'ho-mo',
            u'ho-möo',
            u'hoch',
            u'hy-dro',
            u'hy-per',
            u'hy-po',
            u'hym-no',
            u'hyp-no',
            u'hä-ma-to',
            u'hä-mo',
            u'ideo',
            u'idio',
            u'iko-no',
            u'il',
            u'im',
            u'im-mu-no',
            u'in',
            u'in-fra',
            u'in-ter',
            u'in-tra',
            u'ins',
            u'int-ro',
            u'io-no',
            u'kar-dio',
            u'kar-to',
            u'kata',
            u'klep-to',
            u'kli-no',
            u'kon',
            u'kon-tra',
            u'kor-re',
            u'kos-mo',
            u'kri-mi-no',
            u'kri-no',
            u'kryp-to',
            u'leu-ko',
            u'leuk',
            u'le-xi-ko',
            u'li-tho',
            u'lim-no',
            u'lo-go',
            u'los',
            u'lym-pho',
            u'ma-gne-to',
            u'mak-ro',
            u'mam-mo',
            u'me-ga',
            u'me-lo',
            u'me-so',
            u'me-ta',
            u'me-teo-ro',
            u'me-tho-do',
            u'mik-ro',
            u'mil-li',
            u'miss',
            u'mit',
            u'mo-no',
            u'mor-pho',
            u'mu-si-ko',
            u'mul-ti',
            u'my-co',
            u'my-tho',
            u'na-no',
            u'nach',
            u'ne-ben',
            u'neo',
            u'neu-ro',
            u'neur',
            u'nie-der',
            u'no-wo',
            u'non',
            u'nost',
            u'ob',
            u'oben',
            u'ober',
            u'off',
            u'ohn',
            u'oli-go',
            u'olig',
            u'om-ni',
            u'on-ko',
            u'on-to',
            u'op-to',
            u'or-tho',
            u'oszil-lo',
            u'out',
            u'over',
            u'oxy',
            u'ozea-no',
            u'pa-ra',
            u'pa-tho',
            u'pa-tri',
            u'pan-to',
            u'pe-re',
            u'pen-ta',
            u'pet-ro',
            u'phar-ma',
            u'phar-ma-ko',
            u'phi-lo',
            u'phil',
            u'pho-no',
            u'pho-to',
            u'phra-seo',
            u'phy-lo',
            u'phy-sio',
            u'phy-to',
            u'phä-no',
            u'pneu-mo',
            u'po-eto',
            u'po-li-to',
            u'po-ly',
            u'po-ten-tio',
            u'pro-to',
            u'prä',
            u'pseud',
            u'psy-cho',
            u'py-ro',
            u'pä-do',
            u'päd',
            u'raus',
            u're',
            u'rein',
            u'ret-ro',
            u'ri-bo',
            u'rä-to',
            u'rück',
            u'sa-mo',
            u'sak-ro',
            u'se-mi',
            u'seis-mo',
            u'selb',
            u'ser-bo',
            u'si-no',
            u'so',
            u'so-zio',
            u'sou',
            u'spek-tro',
            u'ste-no',
            u'ste-reo',
            u'ste-tho',
            u'stra-to',
            u'su-per',
            u'sub',
            u'sup-ra',
            u'sus',
            u'syn',
            u'ta-xo',
            u'tau-to',
            u'te-leo',
            u'te-ra',
            u'tech-no',
            u'tele',
            u'telo',
            u'ter-mi-no',
            u'tet-ra',
            u'ther-mo',
            u'throm-bo',
            u'to-mo',
            u'to-po',
            u'to-xi-ko',
            u'tra-gi',
            u'trans',
            u'tro-po',
            u'tur-bo',
            u'ty-po',
            u'ul-tra',
            u'um',
            u'un',
            u'un-der',
            u'un-ter',
            u'uni',
            u'ur',
            u'uro',
            u'ver',
            u'vi-no',
            u'vi-ro',
            u'vib-ra',
            u'voll',
            u'von',
            u'vor',
            u'vorn',
            u'vul-ka-no',
            u'weg',
            u'wi-der',
            u'xe-no',
            u'xy-lo',
            u'zen-ti',
            u'zen-tri',
            u'zer',
            u'zu',
            u'zwie',
            u'zy-klo',
            u'zy-to',
            u'ägyp-to',
            u'öko',
            u'über',
           ]

# Nach Länge sortieren, damit spezifischere zuerst Probiert werden:
praefixe.sort(key = len)
praefixe.reverse()


# Übertrag von Einträgen auf Wörter mit anderer Endung::

def endungsabgleich(key, alt, neu, grossklein=False):

    if not key.endswith(join_word(neu)):
        return ''
    OK = True
    altkey = key[:-len(join_word(neu))] + join_word(alt)
    if grossklein:
        altkey = toggle_case(altkey)

    try:
        altentry = words[altkey]
    except KeyError:
        return ''

    entry = WordEntry(key)
    # print "fundum", key, unicode(entry)
    for wort in altentry[1:]:
        if not wort.startswith(u'-'):
            if alt:
                wort = wort[:-len(alt)]
            wort += neu
            if grossklein:
                wort = toggle_case(wort)
            if join_word(wort) != key:
                OK = False
        entry.append(wort)
    if OK is False:
        print u"# Übertragungsproblem: %s -> %s (%s,%s) %s" % (
                                            altkey, key, alt, neu, unicode(entry))
        return ''

    entry.regelaenderungen()
    return entry


# Endungen
# --------
# ``(<alt>, <neu>)`` Paare von Endungen::

endungen = [
            (u'', u'-de'),
            # (u'', u'-en'),
            # (u'', u'-er'),
            # (u'', u'-is-mus'),
            # (u'', u'-ität'),
            (u'', u'-lein'),
            (u'', u'-ne'),
            (u'', u'-nem'),
            (u'', u'-nen'),
            (u'', u'-ner'),
            (u'', u'-sche'),
            (u'', u'-tum'),
            (u'', u'>ar-tig'),
            (u'', u'>chen'),
            (u'', u'>heit'),
            (u'', u'>keit'),
            (u'', u'>los'),
            (u'', u'>schaft'),
            (u'', u'>schaft'),
            (u'', u'>wei-se'),
            # (u'', u'd'),
            # (u'', u'e'),
            # (u'', u'e-rin'),
            # (u'', u'er'),
            # (u'', u'is-mus'),
            # (u'', u'm'),
            # (u'', u'n'),
            # (u'', u'ner'),
            # (u'', u'r'),
            # (u'', u's'),
            # (u'', u's-te'),
            # (u'', u's-te'),
            # (u'', u's>los'),
            # (u'', u'st'),
            # (u'', u't'),
            # (u'', u't-te'),
            (u'-al', u'a-le'),
            (u'-an', u'a-ne'),
            (u'-at', u'a-te'),
            (u'-ben', u'b-ne'),
            # (u'-che', u'ch'),
            (u'-de', u'd'),
            (u'-en', u'>bar>keit'),
            # (u'-en', u'e'),
            (u'-en', u'e-ne'),
            (u'-er', u'e-rei'),
            (u'-er', u'e-rin'),
            (u'-ern', u'e-re'),
            (u'-ge', u'g'),
            (u'-gen', u'g'),
            (u'-in', u'i-ne'),
            (u'-on', u'o-nen'),
            (u'-re', u'r'),
            (u'-re', u'rt'),
            (u'-ren', u'r-ne'),
            (u'-ren', u'rt'),
            (u'-sche', u'sch'),
            (u'-sen', u's-ne'),
            (u'-sten', u's-mus'),
            (u'-te',u't'),
            (u'-tern', u't-re'),
            (u'-ös', u'ö-se'),
            (u'a', u'ar'),
            (u'a', u'as'),
            (u'b', u'-be'),
            (u'b', u'-ber'),
            (u'bar', u't'),
            (u'bt', u'b-te'),
            (u'ce', u'-cen'),
            (u'ch', u'-che'),
            (u'ch', u'-cher'),
            (u'ck', u'-cke'),
            (u'ck', u'-cker'),
            (u'd', u'-de'),
            (u'd', u'-dem'),
            (u'd', u'-den'),
            (u'd', u'-der'),
            (u'd', u'-des'),
            (u'd', u'>heit'),
            (u'e', u'en'),
            (u'e-ren', u'-ti-on'),
            (u'e-ren', u'sch'),
            (u'el', u'le'),
            # (u'en', u'e'),
            (u'en', u'em'),
            (u'en', u'en-de'),
            (u'en', u'end'),
            (u'en', u'er'),
            (u'en', u'es'),
            (u'en', u'est'),
            (u'en', u't'),
            (u'en', u'te'),
            (u'en', u'us'),
            (u'end',u'en' ),
            # (u'er', u'e'),
            (u'er', u'e-rei'),
            (u'er', u'ens'),
            (u'er', u'in'),
            (u'er', u'ung'),
            (u'es', u'est'),
            (u'es', u's-te'),
            (u'f', u'-fe'),
            (u'f', u'-fer'),
            (u'g', u'-ge'),
            (u'g', u'-gen'),
            (u'g', u'-ger'),
            (u'g', u'-ger'),
            (u'g', u'-ges'),
            (u'g', u'-gung'),
            (u'ie', u'e'),
            (u'in', u'en'),
            (u'isch', u'i-sche'),
            (u'ck', u'-cke'),
            (u'k', u'-ke'),
            (u'k', u'-ken'),
            (u'k', u'-ker'),
            (u'l', u'-le'),
            (u'l', u'-len'),
            (u'l', u'-ler'),
            (u'l', u'-lis-mus'),
            (u'le', u'-ler'),
            (u'li-che', u'tem'),
            (u'li-che', u'ten'),
            (u'ln', u'-le'),
            (u'lt', u'-le'),
            (u'm', u'-me'),
            (u'm', u'-mer'),
            (u'me', u'men'),
            (u'mus', u'men'),
            (u'mus', u'ten'),
            (u'mus', u'tik'),
            (u'n', u'-at'),
            (u'n', u'-er'),
            (u'n', u'-ne'),
            (u'n', u'-nen'),
            (u'on', u'o-nis-mus'),
            (u'n', u'-nis-mus'),
            (u'n', u'r'),
            (u'n', u'st'),
            (u'n', u't'),
            (u'n',u'-ner'),
            (u'nd',u'n'),
            (u'ne',u'ner'),
            # (u'ne',u'n'),
            (u'o',u'-on'),
            (u'o',u'-os'),
            (u'o',u'en'),
            (u'on',u'o-nen'),
            (u'p', u'-pe'),
            (u'p', u'-pen'),
            (u'p', u'-per'),
            (u'ph', u'-phen'),
            (u'ph', u'-phis-mus'),
            (u'r', u'-re'),
            (u'r', u'-rei'),
            (u'r', u'-ren'),
            (u'r', u'-rin'),
            (u'r', u'-ris-mus'),
            (u'r', u'-rung'),
            (u're', u'ste'),
            (u'ren', u'r-te'),
            (u'ren', u'rst'),
            (u'ren', u'rt'),
            (u'rn', u'-re'),
            (u'rn', u'-rung'),
            (u'rn', u'-rung'),
            (u'rt', u'-re'),
            (u'rt', u'r-te'),
            (u's', u''),
            (u's', u'-se'),
            (u's', u'-se-re'),
            (u's', u'-se-res'),
            (u's', u'-ser'),
            (u's', u's-se'),
            (u's', u's-ses'),
            (u'sch', u'-sche'),
            (u'sch', u'-schen'),
            (u'sch', u'-scher'),
            (u'st', u'-ste'),
            (u'st', u'-sten'),
            (u'st', u'n'),
            (u't', u'-ba-re'),
            (u't', u'>bar'),
            (u't', u'-te'),
            (u't', u'-te'),
            (u't', u'-ten'),
            (u't', u'-ter'),
            (u't', u'-tes'),
            (u't', u'-tin'),
            (u't', u'-tis-mus'),
            # (u't', u'e'),
            (u't', u'n'),
            (u't', u'st'),
            (u'te', u'le'),
            # (u'te', u't'),
            (u'ten', u'mus'),
            (u'ten', u'ren'),
            (u'ten', u'tung'),
            (u'ter', u'te-ren'),
            (u'ti-on', u'tor'),
            (u'um', u'a'),
            (u'us', u'en'),
            (u'v', u'-ve'),
            (u'v', u'-ver'),
            (u'v', u'-vis-mus'),
            (u'-ve', u'v'),
            (u'z', u'-ten'),
            (u'z', u'-ze'),
            (u'z', u'-zen'),
            (u'z', u'-zer'),
            (u'ß', u'-ße'),
            (u'ß', u's-se'),
            (u'ös', u'ö-se'),
           ]

# Zerlege einen String mit von vorn bis hinten wandernder Bruchstelle::
#
# >>> from abgleich_neueintraege import zerlege
# >>> list(zerlege(u'wolle'))
# [(u'w', u'olle'), (u'wo', u'lle'), (u'wol', u'le'), (u'woll', u'e')]
#
# ::

def zerlege(s):
    for i in range(1, len(s)):
        yield s[:i], s[i:]

# Zerlege Kompositum in gleichberechtigte Teile::

# >>> from abgleich_neueintraege import split_composits
# >>> from wortliste import WordEntry
# >>> split_composits(WordEntry(u'Blockheizkraftwerk;Block===heiz==kraft=werk'))
# [u'Block', u'heiz', u'kraft', u'werk']
#
# ::

def split_composits(entry):
    return [w for w in entry[1].split(u'=') if w]

# Zerlege String, wenn die Teile in der Wortliste vorhanden sind, setze
# sie neu zusammen und übernehme die Trennmarkierer:


def trenne_key(key, grossklein = False):
    entries = []
    sep = u'='
    for k1, k2 in zerlege(key):
        if grossklein:
            k1 = toggle_case(k1)
        if k1.istitle():
            k2 = k2.title()
        e1 = words.get(k1)
        e2 = words.get(k2)
        if not e2:
            e2 = words.get(toggle_case(k2))
        if e1 and e2:
            if len(e1) != len(e2):
                if len(e1) == 2:
                    e1 = [e1[1]] * len(e2)
                elif len(e2) == 2:
                    e2 = [e2[1]] * len(e1)
                else:
                    continue
            entry = WordEntry(key)
            for w1, w2 in zip(e1,e2)[1:]:
                if w1.startswith(u'-'): # empty column -2-, -3-, ...
                    wort = w1
                elif w2.startswith(u'-'):
                    wort = w2
                else:
                    if grossklein:
                        w1 = toggle_case(w1)
                    w2 = w2.lower()
                    level = 1
                    while (level*sep in w1) or (level*sep in w2):
                        level += 1
                    wort = (level*sep).join([w1, w2])
                entry.append(wort)
            entry.conflate_fields()
            entries.append(entry)
            # Teste auf 3-teilige Composita und entferne die Wichtung:
            # ['Kau==zahn=weh', 'Kau=zahn=weh'] -> ['Kau=zahn=weh']
            if len(entries) == 2:
                teile = [split_composits(entry) for entry in entries]
                if teile[0] == teile[1]:
                    level = 1
                    while level*sep in teile[0]:
                        level += 1
                    entries = [entries[0]]
                    entries[0][1] = entries[0][1].replace((level+1)*sep, level*sep)
    return entries

def filter_neuliste(liste, words):
    for line in liste:
        line = line.decode('utf8').strip()
        if line.startswith('#'):
            yield line
            continue
        neukey = line.split(u';')[0]
        if neukey in words:
            # print 'vorhanden:', line
            continue
        if neukey.title() in words:
            # print 'Vorhanden:', line
            continue
        if neukey.lower() in words:
            # print 'vorhanden (kleingeschrieben):', line
            continue
        yield line

class SortableDict(dict):
    """Dictionary with additional sorting methods

    Tip: use key starting with with '_' for sorting before small letters
         and with '~' for sorting after small letters.
    """
    def sortedkeys(self):
        """Return sorted list of keys"""
        keys = self.keys()
        keys.sort()
        return keys

    def sortedvalues(self):
        """Return list of values sorted by keys"""
        return [self[key] for key in self.sortedkeys()]

def filter_ableitungen(liste):
    words = SortableDict()
    words['#'] = '# Ableitungen entfernt'
    for line in liste:
        line = line.decode('utf8').strip()
        if line.startswith('#'):
            words['#'] += '\n' + line
            continue
        key = line.split(u';')[0]
        gibts_schon = False
        for alt, neu in endungen:
            altkey = key[:-len(join_word(neu))] + join_word(alt)
            if altkey in words:
                gibts_schon = True
                break
        if not gibts_schon:
            words[key] = line
    return words.sortedvalues()    

def print_proposal(entry):
    proposal = getattr(entry, "proposal", u'')
    if proposal and len(proposal) > 1:
        print u' ' + unicode(entry)
        print u'#' + unicode(proposal)
    else:
        print unicode(entry)

if __name__ == '__main__':

# Pfad zu "../../../wortliste" unabhängig vom Arbeitsverzeichnis::

    default_wortliste = os.path.relpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))),
        'wortliste'))
    # 
    #     os.path.dirname(os.path.dirname(os.path.dirname(__file__))),

# Optionen::

    usage = '%prog [Optionen]\n' + __doc__

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--file', dest='wortliste',
                      help='Vergleichsdatei, Vorgabe "%s"'%default_wortliste,
                      default=default_wortliste)
    parser.add_option('-f', '--filter', action="store_true",
                      help=u'in WORTLISTE vorhandene Wörter aussortieren',
                      default=False)
    parser.add_option('-a', '--filter-ableitungen', action="store_true",
                      help=u'Ableitungen von Wörtern der Eingabe aussortieren',
                      default=False)
    (options, args) = parser.parse_args()

    wordfile = WordFile(options.wortliste)

    # sys.stdout mit UTF8 encoding.
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)

# Filtern::

    if options.filter:
        words = wordfile.asdict()
        for line in filter_neuliste(sys.stdin, words):
            print line
        sys.exit()

    if options.filter_ableitungen:
        for line in filter_ableitungen(sys.stdin):
            print line
        sys.exit()

# `Wortliste` einlesen::

    # Wörter, Teilwörter und Kombinationen (siehe expand_teilwoerter.py)
    words = expand_wordfile(wordfile)
    
# Aussortieren von Wörtern, die zu "false positives" führen::

    # Wörter, die oft als Endungen auftauchen:
    for alt, neu in endungen:
        words.pop(join_word(neu), None)

    for unwort in [u'Em', u'Gen']:
        words.pop(unwort, None)

# Erstellen der neuen Einträge::

    neue = []
    neue_grossklein = []
    rest = []

    proposals = [WordEntry(line.decode('utf8').strip())
                 for line in sys.stdin
                 if not line.startswith('#')]

    for newentry in proposals:
        OK = False
        key = newentry[0]

        # print key, unicode(newentry)
        # continue

# Test auf vorhandene (Teil-) Wörter:

        entry = words.get(key)
        if entry:
            neue.append(entry)
            continue
        # kleingeschrieben
        entry = words.get(key.lower())
        if entry:
            neue_grossklein.append(entry)
            continue
        # Großgeschrieben
        entry = words.get(key.title())
        if entry:
            neue_grossklein.append(entry)
            continue

# Endungsabgleich::

        for alt, neu in endungen:
            entry = endungsabgleich(key, alt, neu, grossklein=False)
            if entry:
                entry.comment = newentry.comment
                neue.append(entry)
                OK = True
                # break
        if OK:
            continue

        for alt, neu in endungen:
            entry = endungsabgleich(key, alt, neu, grossklein=True)
            if entry:
                entry.comment = newentry.comment
                neue_grossklein.append(entry)
                OK = True
                # break
        if OK:
            continue

# Präfixabgleich::

        for praefix in praefixe:
            entry = praefixabgleich(key, praefix, grossklein=False)
            if entry:
                entry.comment = newentry.comment
                neue.append(entry)
                OK = True
                break
            entry = praefixabgleich(key, praefix, grossklein=True)
            if entry:
                entry.comment = newentry.comment
                neue_grossklein.append(entry)
                OK = True
                break
        if OK:
            continue

# Zerlegen und test auf Fugen::

        entries = trenne_key(key, grossklein=False)
        if entries:
            neue.extend(entries)
            continue
        entries = trenne_key(key, grossklein=True)
        if entries:
            neue_grossklein.extend(entries)
            continue

# Nicht gefundene Wörter::

        rest.append(newentry)

# Mehrdeutige aussortieren::

    alle_neuen = {}
    doppelkeys = set()
    doppelkeys_gleich = defaultdict(int)

    # doppelte keys finden:
    for entry in neue + neue_grossklein:
        key = entry[0].lower()
        if key in alle_neuen:
            if entry == alle_neuen[key]:
                doppelkeys_gleich[key] += 1
            else:
                doppelkeys.add(key)
        alle_neuen[key] = entry

    # doppelte Einträge "verlegen":
    eindeutige = []
    eindeutige_grossklein = []
    doppelte = []

    for entry in neue:
        key = entry[0].lower()
        if key in doppelkeys:
            doppelte.append(entry)
        elif doppelkeys_gleich[key] > 0:
            doppelkeys_gleich[key] -= 1
        else:
            eindeutige.append(entry)

    for entry in neue_grossklein:
        key = entry[0].lower()
        if key in doppelkeys:
            doppelte.append(entry)
        elif doppelkeys_gleich[key] > 0:
            doppelkeys_gleich[key] -= 1
        else:
            eindeutige_grossklein.append(entry)


# Vergleich mit Original::

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

    print u'\n# eindeutig abgeleitet'
    for entry in eindeutige:
        if entry[0].lower() not in identische:
            print_proposal(entry)
    print u'\n# eindeutig abgeleitet (andere Großschreibung)'
    for entry in eindeutige_grossklein:
        if entry[0].lower() not in identische:
            print_proposal(entry)

    print u'\n# mehrdeutig abgeleitet'
    for entry in doppelte:
        print_proposal(entry)


    print u'\n# Rest'

    for entry in rest:
        print_proposal(entry)
