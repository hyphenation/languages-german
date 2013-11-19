#!/usr/bin/env python
# -*- coding: utf8 -*-
# :Copyright: © 2012 Günter Milde.
# :Licence:   This work may be distributed and/or modified under
#             the conditions of the `LaTeX Project Public License`,
#             either version 1.3 of this license or (at your option)
#             any later  version.
# :Version:   0.2 (2012-02-07)

# ===================================================================
# Langes oder rundes S: Automatische Konversion nach Silbentrennung
# ===================================================================
# 
# ::

"""
Automatische Bestimmung der S-Schreibung auf Basis der Silbentrennung
in der `Wortliste der deutschsprachigen Trennmustermannschaft`.
"""

# .. contents::
# 
# Vorspann
# ========
# 
# Lade Funktionen und Klassen für reguläre Ausdrücke::

import re
from werkzeug import WordFile, join_word

# Ausgangsbasis
# =============
# 
# Die freie `Wortliste der deutschsprachigen Trennmustermannschaft`_
# ("Lembergsche Liste")
# 
# ::

wordfile = WordFile('../../wortliste') # volle Liste (≅ 400 000 Wörter
# wordfile = WordFile('../../wortliste-binnen-s') # vorsortierte Liste (≅ 200 000 Wörter)

# Trennzeichen
# ------------
# 
# Die Trennzeichen der Wortliste sind
# 
# == ================================================================
# \· ungewichtete Trennstellen (solche, wo noch niemand sich um die
#    Gewichtung gekümmert hat)
# .  unerwünschte Trennstellen (sinnverwirrend), z.B. Ur-in.stinkt
# =  Haupttrennstellen
# \- Nebentrennstellen
# |  Trennstellen nach Vorsilben.
# == ================================================================
# 
# 
# Funktionen
# ==========
# 
# ſ-Regeln
# --------
# 
# Siehe [wikipedia]_ und ("DDR"-) [Duden]_ (Regeln K 44,45)::

def s_ersetzen(word):

# ſ steht im Silbenanlaut::

    word = re.sub(ur'^s', ur'ſ', word)
    word = re.sub(ur'([-|=·.])s', ur'\1ſ', word)

# ſ steht im Inlaut als stimmhaftes s zwischen Vokalen
# (gilt auch für ungetrenntes ss zwischen Selbstlauten, z.B. Hausse, Baisse)::

    word = re.sub(ur'([AEIOUYÄÖÜaeiouäöü])s([aeiouyäöü])', ur'\1ſ\2', word)
    word = re.sub(ur'([AEIOUYÄÖÜaeiouäöü])ss([aeiouyäöü])', ur'\1ſſ\2', word)

# ſ steht in den Verbindungen sp, st, sch und in Digraphen::

    word = word.replace(u'st', u'ſt')
    word = word.replace(u'sp', u'ſp')
    word = word.replace(u'sch', u'ſch')

    word = word.replace(u'ps', u'pſ')  # ψ
    word = word.replace(u'Ps', u'Pſ')  # Ψ

    word = word.replace(u'ſsſt', u'ſſſt') # Pssst!

# ſ vor Trennstellen
# ~~~~~~~~~~~~~~~~~~
# 
# Die Verbindungen ss, sp, st und sz werden zu ſſ, ſp, ſt und ſz auch
# wenn sie durch eine Nebentrennstelle (Trennung innerhalb eines
# Wortbestandteiles) getrennt sind.
# 
# s bleibt rund vor einer Haupttrennstelle (Trennung an der Grenze zweier
# Wortbestandteile (Vorsilb<=Stamm, Bestimmungswort=Grundwort), im Auslaut
# und nach Vorsilben wie aus-, dis-,  (mit ``|`` markiert)::

    word = word.replace(u's-ſ', u'ſ-ſ')
    word = word.replace(u's.ſ', u'ſ.ſ')
    word = word.replace(u's-p', u'ſ-p')
    word = word.replace(u's.p', u'ſ.p')
    word = word.replace(u's-t', u'ſ-t') # Reformschreibung
    word = word.replace(u's.t', u'ſ.t')

    # für sz/ſz wurden Spezialregeln erstellt, die Vorkommnisse
    # in der Wortliste erfassen

# Spezialfälle
# ~~~~~~~~~~~~
# 
# ſz trotz Trennzeichen::

    word = word.replace(u'es-zen', ur'eſ-zen') # Adoleszenz, ...
    word = word.replace(u's-zi-n', ur'ſ-zi-n') # faszinieren, ...
    word = word.replace(u'as-zi', u'aſ-zi')    # [Ll]asziv, ...
    word = word.replace(u's-zil', ur'ſ-zil')   # Os-zil-la-ti-on

# ſ wird geschrieben, wenn der S-Laut nur scheinbar im Auslaut steht weil ein
# folgendes unbetontes e ausfällt::

   # Basel, Beisel, Pilsen, drechseln, wechseln, häckseln
    word = word.replace(u'Bas-ler', u'Baſ-ler')
    word = word.replace(u'Pils-ner', u'Pilſ-ner')
    word = word.replace(u'echs-ler', u'echſ-ler') # Dechsler, Wechsler
    word = word.replace(u'äcks-ler', u'äckſ-ler') # Häcksler
    word = word.replace(u'Rössl', u'Röſſl')

    # Insel (Rheininsler), zünseln (Maiszünsler)
    word = word.replace(u'ins-ler', u'inſ-ler')
    word = word.replace(u'üns-ler', u'ünſ-ler')

    # unsre, unsrige, ...
    word = word.replace(u'uns-r', u'unſ-r')

    # Häusl, Lisl, bissl, Glasl, Rössl
    word = word.replace(u'sl', u'ſl')
    word = word.replace(u'ssl', u'ſſl')

# ſ steht auch am Ende von Abkürzungen, wenn es im abgekürzten Wort steht
# (Abſ. - Abſatz/Abſender, (de)creſc. - (de)creſcendo, das. - daselbst ...)

    word = word.replace(u'cresc', u'creſc')

# Alternativtrennung wo beide Fälle ſ verlangen:

    word = word.replace(u'er.]sa', u'er.]sa') # Kind=er|satz/Kin-der=satz


# Fremdwörter
# ~~~~~~~~~~~
# 
# Schreibung nach Regeln der Herkunftssprache. Dabei ist zu bedenken, daß zu
# der Zeit als das lange s im Antiquasatz noch üblich war (bis ca. 1800) die
# Rechtschreibung freier gehandhabt wurde und mehrfach Wandlungen unterworfen
# war [West06]_.
# 
# Im Deutschen werden im Fraktursatz nicht eingedeutschte Fremdwörter in
# Antiqua mit rund-s geschrieben.
# 
# English:
#   The long, medial, or descending ess, as distinct from the short or
#   terminal ess. In Roman script, the long ess was used everywhere except at
#   the end of words, where the short ess was used, and frequently in what is
#   now the digraph «ss», which was often written «ſs» rather than «ſſ»
#   [en.wiktionary.org]_. See also [Typefounder08]_ and [West06]_.
# 
# ::

    word = word.replace(u'sh', u'ſh')       # (englisch)
    # word = word.replace(u'sc', u'ſc')     # (englisch) Diſc oder Disc?
    word = word.replace(u'Csar', u'Cſar')   # Cs -> Tsch (ungarisch)
    # word = word.replace(u'sz', u'ſz')     # polnisch, ungarisch
    word = word.replace(u'Liszt', u'Liſzt') # ungarisch
    word = word.replace(u'Pusz', u'Puſz')   # Pusz-ta ungarisch
    word = re.sub(ur'([Tt])s([aeiouy])', ur'\1ſ\2', word) # ts (chinesisch)
    
#   Der 1971er [Duden]_ führt zu englischen Fremdwörtern mit Schluß-ß die
#   österreichische Schreibung mit "ss" auf (Miß, engl. und österr. Schreibung
#   Miss) wobei das Schluß-s nicht unterstrichen (also lang) ist.
#   So auch Boss, Business, Stewardess,
#   TODO so machen, oder ſs? ::
    
    # word = re.sub(ur'ness$', 'neſſ') # Buſineſſ, Fairneſſ
    # word = re.sub(ur'ness=', 'neſſ=')
    # word = re.sub(ur'dress$', 'dreſſ') # Dreſſ
    # word = re.sub(ur'Dress=', 'Dreſſ=')
    # word = word.replace(u'Miss', u'Miſſ')

    return word

# s-Regeln
# --------
# 
# Test auf verbliebene Unklarheiten
# 
# Wenn ein Wort "s" nur an Stellen enthält wo die Regeln rundes S vorsehen,
# ist die automatische Konversion abgeschlossen.
# 
# Ausnahmen und spezielle Regeln
#
# Liste von Teilstrings, welche stets rund-s behalten ::

spezialfaelle_rund_s = [

# Abkürzungen::
                        
    u'Ausg', u'ausſchl', u'insb', u'desgl', u'hrsg', u'insb',
                        
# ausgelassenes flüchtiges e::
   
    u'Dresd-ne', # Dresd·ner/Dresd·ner·in
    
# s steht auch in einigen Fremdwörtern vor z::

    u'on-fis-zie', # konfiszieren
    u'le-bis-z',
    u'is-zi-pl', # Disziplin
# ss im Auslaut
    (u'Gauss'),  # vgl. "Briefwechsel zwischen C.F. Gauss und H.C. Schumacher, herausg. von C.A.F. Peters"
                 # aber Boſſ, Busineſſ, Dreſſ
                       
                       ]
    
spezialfaelle_rund_s = [(fall, fall.replace('s', '~')) 
                        for fall in spezialfaelle_rund_s]

def is_complete(word):

# Ersetze s an Stellen wo es rund zu schreiben ist durch ~ und teste auf
# verbliebene Vorkommen:
# 
# Einzelfälle mit rundem S (substrings)::


    for fall, ersatz in spezialfaelle_rund_s:
        word = word.replace(fall, ersatz)

# s steht am Wortende, auch in Zusammensetzungen (vor Haupttrennstellen).
# Dasselbe gilt für Doppel-s (aus Fremdwörtern) in der traditionellen
# Rechtschreibung::

    word = re.sub(ur's(=|$)', ur'~\1', word)
    word = re.sub(ur'ss(=|$)', ur'~~\1', word)

# s steht am Silbenende (nach Nebentrennstellen), wenn kein p, t, z oder ſ
# folgt (in der traditionellen Schreibung, wird st nicht getrennt)::

    # word = re.sub(ur'ss?([·.\-][^ptzſ])', ur'~\1', word) # konservativ
    word = re.sub(ur'ss?([·.\-][^pzſ])', ur'~\1', word)   # traditionell

# s steht nach Vorsilben (wie aus|, dis|) auch wenn s, p, t, oder z folgt::

    word = word.replace(u's|', u'|~')

# s steht im Inlaut vor k, n, w::

    word = re.sub(ur's([knw])', ur'~\1', word)

# und suche nach übrigen Vorkommen::

    return 's' not in word


# Globale Variablen
# =================
# 
# Rechtschreibvariante
# --------------------
# 
# Angabe der Sprachvariante nach [BCP47]_ (Reformschreibung 'de' oder 'de-1996',
# Schweiz 'de-CH', ...)
# 
# Zur Zeit werden nur Wörter in traditioneller Schreibweise behandelt::

sprachvariante = 'de-1901'


# Kategorien
# ----------
# 
# Der Algorithmus sortiert die Wörter der Trennliste in die folgenden
# Kategorien:
# 
# Menge aller Wörter der Liste (ohne Trennmuster)::

words = set()

# Automatisch konvertierte Wörter (ohne Trennmuster)::

completed = []

# Offene Fälle mit Trennmuster-Feldern wie im Original:
# 
# Zur automatischen Konvertierung fehlt die Unterscheidung in Haupt- und
# Nebentrennstellen (Wichtung)::

ungewichtet = []

# Der Algorithmus kann die Schreibweise (noch) nicht ermitteln
# (mit teilweisen Ersetzungen)::

offen = []

# Hauptschleife
# =============
# 
# Iteration über alle Zeilen der Wortliste::

for entry in wordfile:

    word = entry.get(sprachvariante)  # Wort mit Trennstellen
    if word is None: # Wort existiert nicht in der Sprachvariante
        continue

# Menge aller Wörter der gewählten Schreibweise (ohne Trennstellen)::

    words.add(entry[0])

# Vorsortieren
# ------------
# 
# Wörter ohne Binnen-s müssen nicht konvertiert werden. Damit wird die
# Wortliste ungefähr um die Hälfte kürzer::

    if 's' not in entry[0][:-1]:
        completed.append(entry[0])
        continue

    # # nur vorsortieren:
    # offen.append(entry)
    # continue

# Regelbasierte s-ſ-Schreibung::

    word = s_ersetzen(word)

# Einsortieren nach Vollständigkeit der Ersetzungen::

    if is_complete(word):
        try:
            completed.append(join_word(word))
        except AssertionError:
            # Aufgelöste Mehrdeutigkeit:
            if u'[·ſ/s·]' in word: # z.B. Wach[·ſ/s·]tu·be
                completed.append(join_word(word.replace(u'[·ſ/s·]', u'ſ')))
                completed.append(join_word(word.replace(u'[·ſ/s·]', u's')))
            else:
                raise                
        continue

    entry.set(word, sprachvariante) # Rückschreiben von teilweisen Ersetzungen

    if word.find(u's·') != -1:
        ungewichtet.append(entry)
    else:
        offen.append(entry)


# Ausgabe
# =======
# 
# Wortliste mit automatisch bestimmter S-Schreibung, ohne Trennstellen::

completed_file = file('wortliste-lang-s', 'w')
completed_file.write(u'\n'.join(completed).encode('utf8') + '\n')

# Wortlisten mit noch offenen Fällen::

for todo in ['ungewichtet', 'offen']:
    todo_file = file('wortliste-lang-s-'+todo, 'w')
    todo = globals()[todo] # get variable from string
    todo = [unicode(entry) for entry in todo]
    # todo = [entry[0] for entry in todo]
    todo_file.write(u'\n'.join(todo).encode('utf8') + '\n')


# Auswertung
# ==========
# 
# ::

print "Gesamtwortzahl (traditionelle Rechtschreibung):", len(words)
print "Automatisch konvertiert:", len(completed)
print "Kategorisierung der Trennstellen fehlt:", len(ungewichtet)
print "noch offen:", len(offen)

print "\nkonvertiert+nichtklassifiziert+offen:", 
print len(completed) + len(ungewichtet) + len(offen)



# Diskussion
# ==========
# 
# Statistik
# ---------
# 
# | Gesamtwortzahl (traditionelle Rechtschreibung) 417629
# | Automatisch konvertiert 401591
# | nur in neuer Rechtschreibung 4653
# | noch offen 9612
# 
# 
# Die Mehrzahl der Wörter der Trennliste wurde nach den Regeln des Dudens in
# die Schreibung mit langem `S` (ſ) konvertiert (wobei ungefähr die Hälfte der
# Wörter kein kleines `s` enthält womit die Konversion trivial wird).
# 
# Der größte Teil der ca. 16 000 noch offenen Fälle kann durch Unterscheidung
# in Haupt- und Nebentrennstellen (z.B. mit dem SiSiSi_-Algorithmus) gelöst
# werden. CTAN enthält eine (alte) Variante mit Atomlisten im Text-Format
# (`Ur-SiSiSi`_). Die im Rahmen einer Diplomarbeit [gruber03]_ entstandene
# Variante `Java-SiSiSi` enthält eine Schnittstelle zum
# Wortanalysealgorithmus, die es ermöglicht SiSiSi als Bibliothek in fremde
# Programme einzubinden.
# 
# Für eine beschränke Anzahl offener Fälle wurden Ausnahmeregeln und Ausnahmen
# implementiert.
# 
# Das Resultat muß noch auf nicht erfaßte Ausnahmen und Sonderfälle geprüft
# werden. Fehlentscheidungen sind nicht auszuschließen.
# 
# 
# Offene Fälle
# ------------
# 
# Wörter mit ſ am Wort oder Silbenende
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# * sp, ss, st und sz wird zu ſp, ſſ, ſt und ſz, auch wenn das ſ vor einer
#   Nebentrennstelle steht (z.B. Weſ-pe, eſ-ſen, abbürſ-ten (Reformtrennung)
#   und Faſ-zination)
# 
#   **Aber** rundes s am Wortende und nach Vorsilben, z.B.
#   dis=putieren, Aus=ſage, aus=tragen, aus=zeichnen.
# 
# 
# Wörter mit identischer Schreibung ohne lang-s
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# * Wach[s/ſ]tube?
# 
# Unklare Schreibung
# ~~~~~~~~~~~~~~~~~~
# 
# * Tonarten (As-Dur oder Aſ-Dur)
# 
#   - Im Fraktur-Duden steht As in Antiqua mit rundem s, aber
#   - im 1976-er [Duden]_ steht As ohne Unterstreichung des `s`.
# 
# 
# 
# Quellen
# =======
# 
# .. [Duden] `Der Große Duden` 16. Auflage, VEB Bibliographisches Institut
#    Leipzig, 1971
# 
#    Kennzeichnet im Stichwortteil rundes s durch Unterstreichen.
# 
# .. [wikipedia] Langes s
#    http://de.wikipedia.org/wiki/Langes_s
# 
# .. [en.wiktionary.org]
#    http://en.wiktionary.org/wiki/%C5%BF
# 
# .. [Typefounder08]
#    http://typefoundry.blogspot.com/2008/01/long-s.html
# 
# .. [West06] Andrew West, `The rules for long s`, 2006
#    http://babelstone.blogspot.com/2006/06/rules-for-long-s.html
# 
# .. [BCP47]  A. Phillips und M. Davis, (Editoren.), 
#    `Tags for Identifying Languages`, http://www.rfc-editor.org/rfc/bcp/bcp47.txt
# 
# .. [gruber03] Martin Gruber, 
#    `Effiziente Gestaltung der Wortanalyse in SiSiSi`, Diplomarbeit, 2003, 
#    http://www.ads.tuwien.ac.at/publications/bib/pdf/gruber-03.pdf
# 
# .. Links:
# 
# .. _Wortliste der deutschsprachigen Trennmustermannschaft:
#    http://mirrors.ctan.org/language/hyphenation/dehyph-exptl/projektbeschreibung.pdf
# 
# .. _SiSiSi: http://www.ads.tuwien.ac.at/research/SiSiSi.html
# 
# .. _Ur-SiSiSi: ftp://ftp.dante.de/pub/tex/systems/unix/sisisi/
# 
# 
# .. Fragen, Spezialfälle, Beispiele
# 
#  http://www.e-welt.net/bfds_2003/bund/fragen/13_Langes%20oder%20rundes%20S.pdf
#  http://www.e-welt.net/bfds_2003/bund/fragen/12_hs%20und%20scharfes%20s_1.pdf
