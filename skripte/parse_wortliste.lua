-- -*- coding: utf-8 -*-

--[[

Copyright 2012, 2013 Stephan Hennig

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.

--]]



--- Dieses Modul stellt Funktionen zum Zerlegen der Wortliste, zur
--- Prüfung des Aufbaus der Wortliste und zur Prüfung des Aufbaus von
--- Wörtern bereit.  Die API-Dokumentation kann mit <pre>
---
---   luadoc -d manual parse_wortliste.lua
---
--- </pre> erstellt werden.
--
-- @class module
-- @name parse_wortliste
-- @author Stephan Hennig
-- @copyright 2012, Stephan Hennig
--

--[[ just for luadoc 3.0 compatibility
module "parse_wortliste"
--]]


-- lokale Modul-Tabelle
local M = {}


-- Kürzel für Selene-Unicode-Funktionen.
local Ugsub = unicode.utf8.gsub
local Ulen = unicode.utf8.len
local Usub = unicode.utf8.sub

-- Kürzel für LPEG-Funktionen.
local P = lpeg.P
local R = lpeg.R
local S = lpeg.S
local C = lpeg.C
local Cc = lpeg.Cc
local Cf = lpeg.Cf
local Ct = lpeg.Ct
local V = lpeg.V
-- Muster für ein beliebiges Zeichen.
local any = P(1)



--
-- Beschreibung des Formats der Wortliste:
--
-- Jeder Datensatz (Zeile) entspricht einer bestimmten Schreibvariante
-- eines Wortes.  Unterschiedliche Schreibvarianten desselben Wortes
-- sind nicht miteinander verknüpft.
--
-- Feldtrenner ist das Semikolon.
local sep = P";"
--
-- Kommentare werden durch '#' eingeleitet und erstrecken sich bis zum
-- Zeilenende.  Vor dem Kommentarzeichen sind beliebige Leerzeichen
-- erlaubt.
local com = P"#"
local spc = P" "
-- Muster für ein Kommentar.
local opcomment = spc^0 * (com * any^0)^-1 * -1
-- Muster für ein Kommentar mit Capture.  Die Capture enthält den
-- Kommentartext ohne das Kommentarzeichen.
local opcommentC = spc^0 * (com * C(any^0))^-1 * -1
--
-- Leere Felder bestehen aus der Feldnummer eingeschlossen in
-- Minuszeichen, z. B. steht -2- für ein leeres Feld 2.
--
-- Muster für eine Ziffer.
local digit = R"09"
-- Muster für ein beliebiges leeres Feld.
local leerX = P"-" * digit * P"-"
-- Muster für leere Felder mit festem Inhalt.
local leer2 = P"-2-"
local leer3 = P"-3-"
local leer4 = P"-4-"
local leer5 = P"-5-"
local leer6 = P"-6-"
local leer7 = P"-7-"
local leer8 = P"-8-"
-- Kürzel für leere Felder mit voranstehendem Feldtrenner.
local _leer2 = sep * leer2
local _leer3 = sep * leer3
local _leer4 = sep * leer4
local _leer5 = sep * leer5
local _leer6 = sep * leer6
local _leer7 = sep * leer7
local _leer8 = sep * leer8
--
-- Belegte Felder bestehen aus beliebigen Zeichen außer Feldtrennern,
-- Leerzeichen oder Kommentarzeichen.  Eine präzisere Beschreibung von
-- zulässigen Wörtern in Form einer Grammatik ist weiter unten zu
-- finden.
--
-- Muster für ein Feld beliebigen Inhalts.
local feld = (any - (sep + spc + com))^1
-- Muster für ein Feld beliebigen Inhalts mit Capture.  Die Capture
-- enthält den Feldinhalt.
local feldC = C(feld)
-- Kürzel für ein Feld beliebigen Inhalts mit voranstehendem
-- Feldtrenner.
local _feldC = sep * feldC
-- Muster für ein belegtes Feld.
local bfeld = feld - leerX
-- Kürzel für ein belegtes Feld mit voranstehendem Feldtrenner.
local _bfeld = sep * bfeld
--
-- Feld 1 enthält ein Wort in ungetrennter Schreibung.
--
-- Die Felder 2, 3, 4 enthalten Wörter, die nicht ausschließlich in
-- Versalschreibung existieren.  Die Felder 3, 4 treten immer paarweise
-- auf.  Enthielten sie denselben Inhalt, so wird stattdessen Feld 2
-- verwendet.  Die Felder 3 und 4 existieren dann nicht.
--
-- Die Felder 5, 6, 7, 8 enthalten Wörter, die nur in expliziter
-- Versalschreibung existieren ('ß' durch 'ss' ersetzt).  Die Felder 6,
-- 7, 8 treten immer zu dritt auf.  Enthielten sie alle denselben
-- Inhalt, so wird stattdessen Feld 5 verwendet.  Die Felder 6, 7, 8
-- existieren dann nicht.
--
-- Feld     Beschreibung
--
--  1       * ungetrennt,
--
--  2       * keine explizite Versalschreibung,
--          * falls in allen Rechtschreibungen gleich,
--
--  3       * traditionelle Rechtschreibung,
--
--  4       * reformierte Rechtschreibung,
--
--  5       * explizite Versalschreibung,
--          * falls in allen Rechtschreibungen gleich,
--
--  6       * traditionelle Rechtschreibung in Deutschland und/oder
--            Österreich,
--
--  7       * reformierte Rechtschreibung,
--
--  8       * traditionelle Rechtschreibung in der Schweiz,
--



-- Tabelle mit Capture-Ersetzungen.  Bilde leere Felder auf den Wert
-- 'false' ab.
local _replace_empty_fields = {} for i = 1,8 do _replace_empty_fields["-"..i.."-"] = false end
-- Muster für ein Feld mit Ersetzung.  Die Capture enthält den Feldinhalt
-- oder 'false' für leere Felder.
local feldRC = leerX / _replace_empty_fields + feldC
local _feldRC = sep * feldRC
-- Muster für eine Zeile mit bis zu acht Feldern (mit Table-Capture) und
-- einem optionalen Kommentar.
local split_record = Ct(C(bfeld) * _feldRC^-7) * opcommentC
--
--- Zerlege einen Datensatz in einzelne Felder und speichere diese in
--- einer Tabelle.
--
-- @param record Datensatz
--
-- @return Tabelle, die einen Datensatz repräsentiert.  Nummerische
-- Indizes korrespondieren mit Feldnummern.  Leere Felder entsprechen
-- dem Wert <code>false</code>.  Der Schlüssel 'comment' enthält
-- gegebenenfalls einen Kommentar.
local function split(record)
   local t, comment = split_record:match(record)
   if comment then t.comment = comment end
   return t
end
M.split = split



--
-- Prüfmuster für Datensatzstruktur
--
-- Im folgenden werden unterschiedliche Typen von zulässigen Datensätzen
-- durch Zeichenketten repräsentiert.  Zeichenpositionen korrespondieren
-- dabei mit Feldernummern.  Das Zeichen an einer Position beschreibt,
-- ob das jeweilige Feld belegt ist oder leer.
--
-- Leere Felder werden durch '_' oder 'x' repräsentiert, wobei 'x' nur
-- aus Gründen der Lesbarkeit für die Felder 2 und 5 verwendet wird.
--
-- Belegte Felder werden durch einen beschreibenden Buchstaben
-- gekennzeichnet.  Folgende Buchstaben werden verwendet:
--
-- Feld     Zeichen     Beschreibung
--
--  1        u          ungetrennt
--  2        a          alle
--  3        t          traditionelle Rechtschreibung
--  4        r          reformierte Rechtschreibung
--  5        c          Versalschreibung, alle
--  6        t          Versalschr., trad. Rechtschr. (D, AT)
--  7        r          Versalschr., reform. Rechtschr.
--  8        s          Versalschr., trad. Rechtschr. (CH)
--
-- Beispiele:
--
--   * Ein Wort, welches in allen Rechtschreibungen gleich getrennt
-- wird: Die Felder 1 und 2 sind belegt, gekennzeichnet durch die
-- Zeichen 'u' und 'a'.  Die Felder 3 bis 8 existieren nicht.  Typ:
-- 'ua'.
--
--   * Ein Wort, welches nicht nur in Versalschreibung existiert (also
-- ein Wort in normaler Schreibung), welches jedoch in traditioneller
-- und reformierter Rechtschreibung unterschiedlich getrennt wird: Die
-- Felder 1, 3 und 4 sind belegt ('u', 't', 'r').  Feld 2 ist leer
-- ('x').  Die Felder 5 bis 8 existieren nicht. Typ: 'uxtr'.
--
--   * Ein Wort, welches nur in Versalschreibung existiert und dort für
-- alle Rechtschreibungen gleich getrennt wird: Die Felder 1 und 5 sind
-- belegt ('u' und 'c').  Die Felder 2 bis 4 sind leer ('x' und '_').
-- Die Felder 6 bis 8 existieren nicht.  Typ: 'ux__c'.
--
--   * Ein Wort, welches nur in (deutsch-)schweizerischer
-- Versalschreibung existiert: Die Felder 1 und 8 sind belegt ('u' und
-- 's').  Die Felder 2 bis 7 sind leer ('x' und '_').  Typ: 'ux__x__s'.
--
--
-- Diese Tabelle bildet Positionen (Indizes von 1-8) auf Tabellen
-- zulässiger Zeichen ab.  Die Untertabellen enthalten die an der
-- jeweiligen Position zulässigen Zeichen und bilden diese auf
-- Teilmuster ab.
local valid_flags = {
   [1] = { u = bfeld },-- ungetrennt
   [2] = { a = _bfeld, x = _leer2 },-- alle
   [3] = { t = _bfeld, _ = _leer3 },-- trad. RS
   [4] = { r = _bfeld, _ = _leer4 },-- reform. RS
   [5] = { c = _bfeld, x = _leer5 },-- Versalschr., alle
   [6] = { t = _bfeld, _ = _leer6 },-- Versalschr., trad. RS (D, AT)
   [7] = { r = _bfeld, _ = _leer7 },-- Versalschr., reform. RS
   [8] = { s = _bfeld, _ = _leer8 },-- Versalschr., trad. RS (CH)
}
--
-- Diese Variable enthält ODER-verknüpft (+) sämtliche Muster, die
-- zulässige Datensätze repräsentieren.
local valid_records
--
--- <strong>nicht-öffentlich</strong> Füge der Liste aller Muster
--- zulässiger Datensätze ein neues Muster hinzu.  Die Captures der
--- Muster enthalten jeweils eine Zeichenkette, die den Datensatztyp
--- repräsentiert.
--
-- @param rec_type Zeichenkette, die ein Muster für einen zulässigen
-- Datensatz repräsentiert
local function _add_to_valid_records(rec_type)
   local ch = string.sub(rec_type, 1, 1)
   local pat = valid_flags[1][ch]
   for i = 2,#rec_type do
      local ch = string.sub(rec_type, i, i)
      pat = pat * valid_flags[i][ch]
   end
   pat = Cc(rec_type) * pat * opcomment
   if valid_records then
      valid_records = valid_records + pat
   else
      valid_records = pat
   end
end
--
-- Erstelle ein Muster, welches sämtliche zulässigen Datensätze
-- repräsentiert.
--
-- Muster für Wörter, die nicht nur in Versalschreibung existieren.
-- (Die Felder 5 bis 8 existieren nicht.)
--
_add_to_valid_records("ua")
-- einfach;ein·fach
--
_add_to_valid_records("uxt_")
-- Abfallager;-2-;Ab·fa{ll/ll·l}a·ger;-4-
-- Abfluß;-2-;Ab-fluß;-4-
--
_add_to_valid_records("ux_r")
-- Abfalllager;-2-;-3-;Ab-fall=la-ger
--
_add_to_valid_records("uxtr")
-- abgelöste;-2-;ab-ge-lö-ste;ab-ge-lös-te
--
--
-- Muster für Wörter, die nur in Versalschreibung existieren ('ß' durch
-- 'ss' ersetzt).
--
_add_to_valid_records("ux__c")
-- Abstoss;-2-;-3-;-4-;Ab·stoss
--
_add_to_valid_records("ux__xt__")
-- Litfasssäulenstilleben;-2-;-3-;-4-;-5-;Lit-fass-säu-len-sti{ll/ll-l}e-ben;-7-;-8-
--
_add_to_valid_records("ux__x_r_")
-- Fussballliga;-2-;-3-;-4-;-5-;-6-;Fuss·ball·li·ga;-8-
--
_add_to_valid_records("ux__x__s")
-- Litfassäule;-2-;-3-;-4-;-5-;-6-;-7-;Lit·fa{ss/ss·s}äu·le
--
_add_to_valid_records("ux__xtr_")
-- süsssauer;-2-;-3-;-4-;-5-;süss·sau·er;süss·sau·er;-8-
--
_add_to_valid_records("ux__xt_s")
-- Fussballiga;-2-;-3-;-4-;-5-;Fuss·ba{ll/ll·l}i·ga;-7-;Fuss·ba{ll/ll·l}i·ga
--
_add_to_valid_records("ux__xtrs")
-- Füsse;-2-;-3-;-4-;-5-;Fü·sse;Füs·se;Füs·se
--
--
-- Muster für Wörter, die in der reformierten Rechtschreibung
-- existieren, in der traditionellen Rechtschreibung jedoch nur in
-- Versalschreibweise ('ß' durch 'ss' ersetzt).
--
_add_to_valid_records("ux_rc")
-- Abfluss;-2-;-3-;Ab-fluss;Ab·fluss
--
_add_to_valid_records("ux_rxtr_")
-- Litfasssäule;-2-;-3-;Lit·fass·säu·le;-5-;Lit·fass·säu·le;Lit·fass·säu·le;-8-
--
_add_to_valid_records("ux_rxtrs")
-- dussligste;-2-;-3-;duss·ligs·te;-5-;duss·lig·ste;duss·ligs·te;duss·lig·ste
--
--
--- Ermittle den Typ eines Datensatzes.
--
-- @param record Datensatz
--
-- @return Zeichenkette, die den Datensatztyp repräsentiert.
local function identify_record(record)
   return valid_records:match(record)
end
M.identify_record = identify_record



--
-- Prüfmuster für Wortstruktur
--
local word_property = {}
--
--- <strong>nicht-öffentlich</strong> Lösche alle Worteigenschaften.
--
-- @return Tabelle <code>word_property</code>
local function _init_word_prop()
   word_property.has_invalid_alt = false
   word_property.has_nonstd = false
   word_property.has_nonstd_sss = false
   word_property.has_eszett = false
   return word_property
end
--
--- <strong>nicht-öffentlich</strong> Merke Eigenschaft
--- 'Spezialtrennung gefunden'.
--
-- @param c Capture
--
-- @return Capture
local function _word_prop_has_nonstd(c)
   word_property.has_nonstd = true
   return c
end
--
--- <strong>nicht-öffentlich</strong> Merke Eigenschaft
--- 'Dreikonsonantenregel für s gefunden'.
--
-- @param c Capture
--
-- @return Capture
local function _word_prop_has_nonstd_sss(c)
   word_property.has_nonstd_sss = true
   return c
end
--
--- <strong>nicht-öffentlich</strong> Merke Eigenschaft
--- 'ß gefunden'.
--
-- @param c Capture
--
-- @return Capture
local function _word_prop_has_eszett(c)
   word_property.has_eszett = true
   return c
end
--
--- <strong>nicht-öffentlich</strong> Füge Strings zusammen.  Diese
--- Funktion akkumuliert Zeichen in einer Faltungscapture
--- (<code>lpeg.Cf</code>).
--
-- @param acc bisheriger Akkumulator
--
-- @param newvalue nächster Capturewert
--
-- @return neuer Akkumulatorzustand
local function _conc_cluster(acc, newvalue)
--   io.stderr:write("'",acc,"'..'",newvalue,"'\n")-- For debugging purposes.
   return acc..newvalue
end
--
--- <strong>nicht-öffentlich</strong> Vergleiche Strings.  Diese
--- Funktion wird in einer Faltungscapture (<code>lpeg.Cf</code>)
--- verwendet, um die Gleichheit zweier Captures festzustellen.  Falls
--- zwei Strings ungleich sind, so wird dies in Tabelle
--- <code>word_property</code> vermerkt.
--
-- @param a String 1
--
-- @param b String 2
--
-- @return String 1
local function _is_equal_part_word(a, b)
   word_property.has_invalid_alt = word_property.has_invalid_alt or (a ~= b)
   return a
end
--
-- Grammatik für ein Wort.
--
-- Diese Grammatik prüft nicht, ob die ersten und letzten beiden Zeichen
-- eines Wortes Buchstaben sind.  Die vollständige Gültigkeit von
-- Wörtern sollte mit zusätzlichen, nachgeschalteten Prüfungen erfolgen.
--
local word = P{
   -- Initialregel.
   "word_with_property_table",
   --
   -- Wort
   --
   -- Während des Mustervergleichs werden verschiedene Eigenschaften des
   -- betrachteten Wortes in einer modullokalen Tabelle gespeichert.
   -- Die Flags innerhalb dieser Tabelle werden vor dem Mustervergleich
   -- gelöscht.
   word_with_property_table = P"" / _init_word_prop * V"word" * -1,
   -- Ein Wort ist ein Teilwort, kann also führende oder abschließende
   -- Trennzeichen enthalten.  Diese Generalisierung vereinfacht die
   -- Grammatik im Zusammenhang mit Alternativen etwas.
   word = V"part_word" * -1,
   -- Ein Teilwort besteht aus zusammenhängenden Zeichenketten,
   -- sogenannten Klustern, die durch Trennzeichen voneinander getrennt
   -- sind.  Ein Teilwort kann ein optionales führendes und schließendes
   -- Trennzeichen enthalten.  Die Capture enthält das Wort ohne
   -- jegliche Trennzeichen.
   part_word = V"ophyphen" * Cf(V"cluster" * (V"hyphen" * V"cluster")^0, _conc_cluster) * V"ophyphen",
   -- Ein Kluster besteht aus mehreren aneinandergereihten fundamentalen
   -- Klustern ohne Unterbrechung durch Trennzeichen.  Es gibt drei
   -- Arten von fundamentalen Klustern: Buchstabenkluster,
   -- Spezialtrennungen und Alternativen:
   --
   --                 Bü-cher   E{ck/k-k}e   Sto{ff/ff-f}et-zen   Wach[-s/s-]tu-be
   -- fund. Kluster   11-2222   1222222223   11122222222233-444   1111222222233-44
   -- Kluster         11-2222   1111111111   11111111111111-222   1111111111111-22
   --
   -- Die Capture enthält sämltliche Zeichen der aufeinanderfolgenden
   -- Kluster.
   cluster = Cf((V"cl_letter" + V"cl_nonstd" + V"cl_alt")^1, _conc_cluster),
   --
   -- Trennzeichen
   --
   -- Verschiedene Arten von Trennstellen werden durch unterschiedliche
   -- Trennzeichen markiert.
   --
   -- Die folgenden Trennzeichen werden verwendet:
   hyphen = S"-|=_." + P"·",
   -- Ein beliebiges, optionales Trennzeichen.
   ophyphen = V"hyphen"^-1,
   --
   -- Buchstabenkluster
   --
   -- Ein Buchstabenkluster besteht aus aufeinanderfolgenden Buchstaben.
   -- Die Capture sammelt alle Buchstaben.
   cl_letter = C(V"letter"^1),
   -- Die folgenden Buchstaben sind zulässig:
   letter = R("az", "AZ")
   + P"Ä"
   + P"Ö"
   + P"Ü"
   + P"ß" / _word_prop_has_eszett
   + P"à"
   + P"á"
   + P"â"
   + P"ä"
   + P"ç"
   + P"è"
   + P"é"
   + P"ê"
   + P"ë"
   + P"í"
   + P"î"
   + P"ñ"
   + P"ó"
   + P"ô"
   + P"ö"
   + P"ü"
,
   --
   -- Spezialtrennung
   --
   -- Spezialtrennungen (non-standard hyphenation) beschreiben
   -- Trennregeln, die über das bloße Einfügen eines Trennzeichens
   -- hinausgehen.  Dazu gehören die ck-Trennung und die
   -- Dreikonsonantenregel(n).  Spezialtrennungen sind jeweils
   -- eingeschlossen in Klammern.  Die Capture enthält eine
   -- Zeichenkette, die der jeweils ungetrennten Spezialtrennung
   -- entspricht (z. B. 'ck' für die ck-Trennung).
   cl_nonstd = V"nonstd_open" * V"nonstd_rule" * V"nonstd_close",
   -- Aufzählung sämtlicher Spezialtrennungen.  Das Auftreten von
   -- Spezialtrennungen wird in Tabelle <code>word_property</code>
   -- gespeichert.
   nonstd_rule = (V"ck" + V"bbb" + V"fff" + V"lll" + V"mmm" + V"nnn" + V"ppp" + V"rrr" + V"ttt" + V"nonstd_sss") / _word_prop_has_nonstd,
   -- ck-Trennung: Die Capture enthält die Zeichenfolge 'ck'.
   ck = C(P"ck") * V"nonstd_sep" * P"k" * V"hyphen" * P"k",
   -- Dreikonsonantenregel: Die Capture enthält die Zeichenfolge für die
   -- ungetrennte Konsonantenfolge.
   bbb = C(P"bb") * V"nonstd_sep" * P"bb" * V"hyphen" * P"b",
   fff = C(P"ff") * V"nonstd_sep" * P"ff" * V"hyphen" * P"f",
   lll = C(P"ll") * V"nonstd_sep" * P"ll" * V"hyphen" * P"l",
   mmm = C(P"mm") * V"nonstd_sep" * P"mm" * V"hyphen" * P"m",
   nnn = C(P"nn") * V"nonstd_sep" * P"nn" * V"hyphen" * P"n",
   ppp = C(P"pp") * V"nonstd_sep" * P"pp" * V"hyphen" * P"p",
   rrr = C(P"rr") * V"nonstd_sep" * P"rr" * V"hyphen" * P"r",
   ttt = C(P"tt") * V"nonstd_sep" * P"tt" * V"hyphen" * P"t",
   sss = C(P"ss") * V"nonstd_sep" * P"ss" * V"hyphen" * P"s",
   -- Das Auftreten der Dreikonsonantenregel für 's' wird in Tabelle
   -- <code>word_property</code> gespeichert.
   nonstd_sss = V"sss" / _word_prop_has_nonstd_sss,
   -- Klammer, die eine Spezialtrennung einführt.
   nonstd_open = P"{",
   -- Klammer, die eine Spezialtrennung abschließt.
   nonstd_close = P"}",
   -- Trennzeichen innerhalb einer Spezialtrennung.
   nonstd_sep = P"/",
   --
   -- Alternative
   --
   -- Eine Alternative beschreibt mehrdeutige Wortteile, die
   -- unterschiedlich getrennt werden können.  Die Capture enthält die
   -- Zeichen der jeweils ersten Alternative ohne jegliche Trennzeichen.
   --
   -- Alternativen sind eingeschlossen in Klammern.
   cl_alt = V"alt_open" * V"alt_rule" * V"alt_close",
   -- Alternative Teilwörter werden durch ein spezielles Trennzeichen
   -- voneinander getrennt.  Beide Alternativen werden auf
   -- Buchstabengleichheit geprüft.  Die Capture enthält abschließend
   -- die Buchstaben der ersten Alternative.
   alt_rule = Cf(V"alt_1st" * V"alt_sep" * V"alt_2nd", _is_equal_part_word),
   -- Die erste Alternative ist ein Teilwort (mit Capture).
   alt_1st = V"part_word",
   -- Die zweite Alternative ist ebenfalls ein Teilwort.  Diese Capture
   -- wird später verworfen.
   alt_2nd = V"part_word",
   -- Klammer, die eine Alternative einführt.
   alt_open = P"[",
   -- Klammer, die eine Alternative abschließt.
   alt_close = P"]",
   -- Trennzeichen innerhalb einer Alternative.
   alt_sep = P"/",
}
--
--- Ermittle Eigenschaften eines Wortes.
--
-- @param rawword unbehandeltes Wort
--
-- @return <code>nil</code>, falls das Wort eine unzulässige Struktur
-- hat;<br /> eine Tabelle mit Eigenschaften des betrachteten Wortes,
-- sonst.
local function parse_word(rawword)
   -- Verwirf eventuelle weitere Captures.
   return ( word:match(rawword) )
end
M.parse_word = parse_word



--- Normalisiere ein Wort.  Resultat ist ein Wort in einem für Patgen
--- geeigneten Format, falls das Wort zulässig ist.  Sämtliche
--- Trennzeichen werden durch '<code>-</code>' ersetzt.
--- Spezialtrennungen und Alternativen werden aufgelöst.
--
-- @param rawword unbehandeltes Wort
--
-- @return <code>nil</code>, falls das Wort eine unzulässige Struktur
-- hat;<br /> <code>word, props</code>, sonst.  <code>word</code> ist
-- das normalisierte Wort, <code>props</code> ist eine Tabelle mit
-- Eigenschaften des betrachteten Wortes.
local function normalize_word(rawword)
   -- vorbereitende Prüfung der Wortstruktur und Worteigenschaften
   local props = parse_word(rawword)
   -- Hat das Wort eine zulässige Struktur?
   if not props then return nil end
   -- Prüfe auf unzulässige Alternativen.
   if props.has_invalid_alt then return nil end

   -- Ersetze Spezialtrennungen.
   rawword = Ugsub(rawword, "{(.-)/.-}", "%1")
   -- Ersetze Alternativen.
   rawword = Ugsub(rawword, "%[[-|=_%.·]?(.-)[-|=_%.·]?/.-%]", "%1")
   -- Ersetze Trennzeichen durch "-".
   rawword = Ugsub(rawword, "[|=_%.·]", "-")
   return rawword, props
end
M.normalize_word = normalize_word



--- Prüfe ein Wort auf Wohlgeformtheit.
--
-- @param rawword Wort (normiert oder unbehandelt)
--
-- @return <code>nil, msg</code>, falls das Wort eine unzulässige
-- Struktur hat;<br /> <code>word, props</code>, sonst.
-- <code>msg</code> ist ein String, der die Unzulässigkeit näher
-- beschreibt.  <code>word</code> ist das normalisierte Wort.
-- <code>props</code> ist eine Tabelle mit Eigenschaften des
-- betrachteten Wortes.
local function validate_word(rawword)
   -- Normalisiere Wort.
   local word, props = normalize_word(rawword)
   -- Zulässiges Wort?
   if not word then return nil, "ungültiges Wort" end
   -- Prüfe minimale Wortlänge.
   local len = Ulen(Ugsub(word, "-", ""))
   if len < 4 then return nil, "weniger als vier Buchstaben" end
   -- Prüfe Wortenden auf unzulässige Trennzeichen.
   local len = Ulen(word)
   for i = 1,2 do
      local ch = Usub(word, i, i)
      if ch == "-" then return nil, "Trennzeichen am Wortanfang" end
   end
   for i = len-1,len do
      local ch = Usub(word, i, i)
      if ch == "-" then return nil, "Trennzeichen am Wortende" end
   end
   return word, props
end
M.validate_word = validate_word



--- Prüfe einen Datensatz auf Wohlgeformtheit.  Geprüft wird das Format
--- des Datensatzes und die Zulässigkeit sämtlicher Wörter.
--
-- @param record zu prüfender Datensatz
--
-- @return Typ des Datensatzes, falls dieser wohlgeformt ist;<br />
-- <code>nil</code>, falls der Datensatz kein zulässiges Format hat;<br
-- /> <code>false, field, msg</code>, falls der Datensatz unzulässige
-- Wörter enthält.  <code>field</code> gibt die Nummer des fehlerhaften
-- Feldes an.  <code>msg</code> ist ein String, der den Fehler näher
-- beschreibt.
local function validate_record(record)
   -- Prüfe Gültigkeit des Datensatzes.
   local type = identify_record(record)
   if not type then return nil end
   -- Zerlege Datensatz.
   local trec = split(record)
   -- Merke Inhalt von Feld 1 für Gleichheitsprüfung der belegten
   -- Felder.
   local field1 = trec[1]
   if not field1 then return false, 1, "leer" end
   for i = 1,#trec do
      local word, props = trec[i]
      if word then
         -- Hat das Wort eine zulässige Struktur?
         word, props = validate_word(word)
         if not word then return false, i, props end
         -- Stimmt Wort mit Feld 1 überein?
         word = Ugsub(word, "-", "")
         if word ~= field1 then return false, i, "ungleich Feld 1" end
         -- Tritt eine Spezialtrennung an unzulässiger Feldnummer auf?
         if props.has_nonstd and (i==2 or i==4 or i==5 or i==7) then return false, i, "unzulässige Spezialtrennung" end
         -- Tritt eine Dreikonsonantenregel für 's' an unzulässiger Feldnummer auf?
         if props.has_nonstd_sss and (i ~= 8) then return false, i, "unzulässige Spezialtrennung" end
         -- Tritt 'ß' an unzulässiger Feldnummer auf?
         if props.has_eszett and (i > 4) then return false, i, "unzulässiges ß" end
      end
   end
   return type
end
M.validate_record = validate_record



-- Exportiere Modul-Tabelle.
return M
