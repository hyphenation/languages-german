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



--- Dieses Modul stellt die folgende Funktionalität zur Manipulation der
--- Wortliste bereit:
--
-- <ul>
-- <li>Prüfen von Wörtern auf Wohlgeformtheit,</li>
-- <li>Normalisieren von Wörtern (Übertragen in ein für <a href="http://tug.org/docs/liang/">Patgen</a> geeignetes Format):<br />
-- <code>Lei-nen==be[t=tu-/{tt/tt=t}u.]ches</code> &emsp;&rarr;&emsp; <code>Lei-nen-bettuches</code>,</li>
-- </ul>
--
-- @class module
-- @name helper_words
-- @author Stephan Hennig
-- @copyright 2012, 2013, Stephan Hennig

-- Die API-Dokumentation kann mit <pre>
--
--   luadoc -d API *.lua
--
-- </pre> erstellt werden.



--[[ just for luadoc 3.0 compatibility
module "helper_words"
--]]
-- lokale Modul-Tabelle
local M = {}



-- Lade Module.
local lpeg = require("lpeg")
local unicode = require("unicode")



-- Kürzel für Funktionen der Standardbibliotheken.
local Tconcat = table.concat
-- Kürzel für LPEG-Funktionen.
local P = lpeg.P
local R = lpeg.R
local C = lpeg.C
local V = lpeg.V
-- Kürzel für Unicode-Funktionen.
local Ugsub = unicode.utf8.gsub
local Ulen = unicode.utf8.len
local Usub = unicode.utf8.sub



--
-- Hilfsfunktionen und -variablen für LPEG-Mustersuche.
--
-- Eine Tabelle, in der während der Mustersuche Eigenschaften des
-- untersuchten Wortes gespeichert werden.
local word_property
--
--- <strong>nicht-öffentlich</strong> Diese Funktion wird zu Beginn
--- einer erfolgreichen Prüfung der Wortgrammatik gegen einen String
--- ausgeführt.
-- Initialisiert Tabelle mit Worteigenschaften.
local function _at_word_start()
   word_property = {}
end
--
--- <strong>nicht-öffentlich</strong> Diese Funktion wird am Ende einer
--- erfolgreichen Prüfung der Wortgrammatik gegen einen String
--- ausgeführt.
--  Verwirft alle ausstehenden Captures.
--
-- @param ... Variable Anzahl an Strings
--
-- @return Tabelle mit Worteigenschaften
local function _at_word_end(...)
   word_property.norm_word = Tconcat({...})
   return word_property
end
--
--- <strong>nicht-öffentlich</strong> Merke Eigenschaft
--- 'Spezialtrennung enthalten'.
-- Die Capture wird nicht verändert.
--
-- @param c Capture
--
-- @return Capture
local function _property_has_nonstd(c)
   word_property.has_nonstd = true
   return c
end
--
--- <strong>nicht-öffentlich</strong> Merke Eigenschaft
--- 'Dreikonsonantenregel für s enthalten'.
-- Die Capture wird nicht verändert.
--
-- @param c Capture
--
-- @return Capture
local function _property_has_nonstd_sss(c)
   word_property.has_nonstd_sss = true
   return c
end
--
--- <strong>nicht-öffentlich</strong> Merke Eigenschaft 'ß enthalten'.
local function _property_has_eszett()
   word_property.has_eszett = true
end
--
--- <strong>nicht-öffentlich</strong> Füge eine beliebige Zahl von
--- Strings zusammen.
-- Diese Funktion wird in einer Funktionscapture genutzt, um Cluster
-- zusammenzufügen.  Vorhandene normalisierte Trennzeichen werden aus
-- der Ergebniscapture entfernt.
--
-- @param ... Variable Anzahl an Strings
--
-- @return zusammengesetzter String
local function _concatenate_alt_part_word(...)
--   io.stderr:write("conc: ",Tconcat({...}, ","),"\n")-- For debugging purposes.
   return ( Ugsub(Tconcat({...}), "-", "") )
end
--
--- <strong>nicht-öffentlich</strong> Prüfe zwei Alternativen auf
--- Gleichheit.
-- Diese Funktion wird in einer Funktionscapture verwendet, um die
-- Gleichheit zweier Alternativen zu prüfen.  Falls die Alternativen
-- ungleich sind, so wird dies als Worteigenschaft vermerkt.  Ergebnis
-- ist das erste Argument.
--
-- @param a Capture 1
--
-- @param b Capture 2
--
-- @return Capture 1
local function _is_equal_two_alternatives(a, b)
   word_property.has_invalid_alt = word_property.has_invalid_alt or (a ~= b)
   return a
end



--
-- Die Grammatik eines Wortes.
--
-- Diese Grammatik beschreibt die Struktur zulässiger Wörter.  Durch
-- Prüfen eines Strings gegen diese Grammatik kann festgestellt werden,
-- ob dieser ein Wort im Sinne der Grammatik enthält.
--
-- Bei positivem Ergebnis ist der Rückgabewert der Funktion `match` eine
-- Tabelle, in welcher während der Prüfung die folgenden Eigenschaften
-- des betrachteten Wortes gespeichert werden.
--
--    Feld                 Bedeutung
--
--    has_invalid_alt      Alternativen sind nicht identisch
--    has_eszett           Wort enthält Buchstaben 'ß'
--    has_nonstd           Wort enthält Spezialtrennung
--    has_nonstd_sss       Wort enthält Spezialtrennung für das 's'
--    norm_word            normalisiertes Wort
--
-- Die Grammatik beschreibt die Zulässigkeit von Wörtern nicht
-- erschöpfend.  So wird beispielsweise nicht darauf eingegangen, ob
-- Trennstellen einen Mindestabstand vom Wortrand haben müssen.  Die
-- Zulässigkeit von Wörtern sollten daher mit zusätzlichen,
-- nachgeschalteten Prüfungen festgestellt werden (siehe Funktion
-- `validate_word()`).
--
-- Weitere Informationen können der Datei `README.wortliste` entnommen
-- werden.
--
local word = P{
   -- Initialregel.
   "property_table",
   --
   -- Wort
   --
   -- Am Anfang der Prüfung wird die Tabelle mit Worteigenschaften
   -- zurückgesetzt.  Am Ende werden alle ausstehenden Captures
   -- verworfen.
   property_table = P(true) / _at_word_start * V"word" * -1 / _at_word_end,
   -- Ein Wort beginnt mit einem Wortanfang.  Darauf folgt ein Wortrest.
   word = V"word_head" * V"word_tail",
   -- Ein Wortanfang besteht aus einem Kluster.
   word_head = V"cluster",
   -- Ein Wortrest besteht aus einer normalisierten
   -- Trennstellenmarkierung gefolgt von einem Kluster.  Der gesamte
   -- Ausdruck ist optional.
   word_tail = (V"norm_hyphen" * V"cluster")^0,
   --
   -- Trennstellen
   --
   -- Die Markierung von Trennstellen erfolgt zunächst nach deren
   -- morphologischer Struktur.  Wahlweise kann auch eine (zusätzliche)
   -- qualitative Bewertung erfolgen.
   --
   -- morphologische Markierungen
   --
   -- innerhalb von Wortstämmen oder vor Suffixen
   hyphen_inner = V"hyphen_ch_inner"^1,
   -- nach Präfixen oder Verbalpartikeln
   hyphen_prefix = V"hyphen_ch_prefix"^1,
   -- an Wortfugen
   hyphen_compound = V"hyphen_ch_compound"^1,
   -- nach Präfix eines zusammengesetzten Wortes
   hyphen_compound_prefix = V"hyphen_ch_prefix" * V"hyphen_compound",
   -- vor Suffix eines zusammengesetzten Wortes
   hyphen_compound_suffix = V"hyphen_ch_inner" * V"hyphen_compound",
   -- eine morphologische Markierung (Achtung: In der folgenden Regel
   -- ist die Reihenfolge der Prüfung relevant.  Gemischte Trennzeichen
   -- müssen vor reinen Trennzeichen geprüft werden.)
   hyphen_morph =
      V"hyphen_compound_prefix"
      + V"hyphen_compound_suffix"
      + V"hyphen_inner"
      + V"hyphen_prefix"
      + V"hyphen_compound",
   --
   -- qualitative Markierungen (Bewertung)
   --
   -- eine Bewertung
   hyphen_quality = V"hyphen_ch_quality" * V"hyphen_ch_quality"^-2,
   -- eine optionale Bewertung
   hyphen_opt_quality = V"hyphen_quality"^-1,
   --
   -- unkategorisierte Markierungen
   --
   hyphen_uncategorized = V"hyphen_ch_uncategorized",
   --
   -- Eine beliebige Trennstellenmarkierung ist entweder unkategorisiert
   -- oder morphologisch markiert mit optional folgender Bewertung.  Die
   -- Bewertung kann auch alleinstehen.
   hyphen = V"hyphen_uncategorized"
      + V"hyphen_morph" * V"hyphen_opt_quality"
      + V"hyphen_quality"
,
   --
   -- Eine normalisierte Trennstellenmarkierung ist eine
   -- Trennstellenmarkierung, deren Capture ein für Patgen geeignetes
   -- Trennzeichen ist.
   norm_hyphen = V"hyphen" / "-",
   --
   -- Die folgenden Zeichen werden zur Trennstellenmarkierung verwendet:
   hyphen_ch_inner = P"-",
   hyphen_ch_prefix = P"|",
   hyphen_ch_compound = P"=",
   hyphen_ch_quality = P".",
   hyphen_ch_uncategorized = P"·",
   --
   -- Kluster
   --
   -- Ein Kluster besteht aus einem oder mehreren aufeinanderfolgenden
   -- `fundamentalen Klustern` ohne Unterbrechung durch Trennzeichen.
   -- Es gibt drei Arten von fundamentalen Klustern:
   --
   --   * Buchstabenkluster,
   --   * Ausdrücke für Alternativen,
   --   * Ausdrücke für Spezialtrennungen,
   --
   --                 Bü-cher   E{ck/k-k}e   Sto{ff/ff-f}et-zen   Wach[-s/s-]tu-be
   -- Kluster         11-2222   1111111111   11111111111111-222   1111111111111-22
   -- fund. Kluster   11-2222   1222222223   11122222222233-444   1111222222233-44
   --
   cluster = (V"cl_letter" + V"cl_nonstd" + V"cl_alt")^1,
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
   + P"ß" / _property_has_eszett
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
   -- Ausdrücke für Alternativen
   --
   -- Eine Alternative beschreibt mehrdeutige Wortteile, die
   -- unterschiedlich getrennt werden können.
   --
   -- Ausdrücke für Alternativen werden in begrenzende Zeichen
   -- (Klammern) eingeschlossen.
   cl_alt = V"alt_open" * V"alt_rule" * V"alt_close",
   -- Teilausdrücke einer Alternative werden durch ein spezielles
   -- Zeichen voneinander getrennt.  Beide Alternativen werden auf
   -- Buchstabengleichheit geprüft.  Die Capture enthält abschließend
   -- die Buchstaben der ersten Alternative.
   alt_rule = (V"alt_1st" * V"alt_sep" * V"alt_2nd") / _is_equal_two_alternatives,
   -- Alternativen enthalten Alternativteilwörter.  Die Unterschiede
   -- zwischen Wörtern und Alternativteilwörtern sind:
   --
   -- * Alternativteilwörter können eine führende oder abschließende
   --   Trennstellenmarkierung haben.
   -- * Die Capture von Alternativteilwörter enthält keine Trennzeichen.
   alt_1st = V"alt_part_word",
   alt_2nd = V"alt_part_word",
   -- Ein Alternativteilwort ist ein Wort, welches eine führende und
   -- abschließende Trennstellenmarkierung enthalten kann.
   alt_part_word = V"ophyphen" * V"word" / _concatenate_alt_part_word * V"ophyphen",
   -- Eine optionale Trennstellenmarkierung.
   ophyphen = V"hyphen"^-1,
   -- Zeichen, welches einen Ausdruck für Alternativen einführt.
   alt_open = P"[",
   -- Zeichen, welches einen Ausdruck für Alternativen abschließt.
   alt_close = P"]",
   -- Zeichen, welches Teilausdrücke einer Alternative voneinander
   -- trennt.
   alt_sep = P"/",
   --
   -- Ausdrücke für Spezialtrennungen
   --
   -- Spezialtrennungen (non-standard hyphenation) beschreiben
   -- Trennregeln, die über das bloße Einfügen eines Trennzeichens
   -- hinausgehen.  Dazu gehören die ck-Trennung und die
   -- Dreikonsonantenregel(n).  Spezialtrennungen sind jeweils
   -- eingeschlossen in Klammern.  Die Capture enthält eine
   -- Zeichenkette, die der jeweils ungetrennten Spezialtrennung
   -- entspricht (z. B. 'ck' für die ck-Trennung).
   --
   -- Ausdrücke für Spezialtrennungen werden in begrenzende Zeichen
   -- (Klammern) eingeschlossen.
   cl_nonstd = V"nonstd_open" * V"nonstd_rule" * V"nonstd_close",
   -- Aufzählung sämtlicher Spezialtrennungen.  Das Auftreten von
   -- Spezialtrennungen wird als Worteigenschaft vermerkt.
   nonstd_rule = (V"ck" + V"bbb" + V"fff" + V"lll" + V"mmm" + V"nnn" + V"ppp" + V"rrr" + V"ttt" + V"nonstd_sss") / _property_has_nonstd,
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
   -- Das Auftreten der Dreikonsonantenregel für 's' wird als
   -- Worteigenschaft vermerkt.
   nonstd_sss = V"sss" / _property_has_nonstd_sss,
   -- Zeichen, welches einen Ausdruck für Spezialtrennungen einführt.
   nonstd_open = P"{",
   -- Zeichen, welches einen Ausdruck für Spezialtrennungen abschließt.
   nonstd_close = P"}",
   -- Zeichen, welches Teilausdrücke einer Spezialtrennung voneinander
   -- trennt.
   nonstd_sep = P"/",
}



--- Prüfe String gegen Wortgrammatik.
-- Falls der String ein zulässiges Wort darstellt, wird eine Tabelle mit
-- Eigenschaften des Wortes zurückgegeben.
--
-- @param rawword unbehandeltes Wort
--
-- @return <code>nil</code>, falls das Wort eine unzulässige Struktur
-- hat;<br /> eine Tabelle mit Eigenschaften des betrachteten Wortes,
-- sonst.
local function parse_word(rawword)
   return word:match(rawword)
end
M.parse_word = parse_word



--- Normalisiere ein Wort.
--  Resultat ist ein Wort in einem für Patgen geeigneten Format, falls
-- das Wort zulässig ist.  Sämtliche Trennzeichen werden durch
-- '<code>-</code>' ersetzt.  Spezialtrennungen und Alternativen werden
-- aufgelöst.
--
-- @param rawword unbehandeltes Wort
--
-- @return <code>nil</code>, falls das Wort eine unzulässige Struktur
-- hat;<br /> eine Tabelle mit Eigenschaften des betrachteten Wortes,
-- sonst.
local function normalize_word(rawword)
   -- Prüfung der Wortstruktur und Ermittlung der Worteigenschaften.
   local props = parse_word(rawword)
   -- Hat das Wort eine zulässige Struktur?
   if not props then return nil end
   -- Prüfe auf unzulässige Alternativen.
   if props.has_invalid_alt then return nil end
   return props
end
M.normalize_word = normalize_word



--- Prüfe ein Wort auf Wohlgeformtheit.
--
-- @param rawword Wort (normiert oder unbehandelt)
--
-- @return <code>nil, msg</code>, falls das Wort eine unzulässige
-- Struktur hat;<br /> eine Tabelle mit Eigenschaften des betrachteten
-- Wortes, sonst.<br /> <code>msg</code> ist ein String, der die
-- Unzulässigkeit näher beschreibt.
local function validate_word(rawword)
   -- Normalisiere Wort.
   local props = normalize_word(rawword)
   -- Zulässiges Wort?
   if not props then return nil, "ungültiges Wort" end
   -- Ermittle normalisiertes Wort.
   local word = props.norm_word
   -- Prüfe minimale Wortlänge.
   local len = Ulen(Ugsub(word, "-", ""))
   if len < 4 then return nil, "weniger als vier Buchstaben" end
   -- Prüfe Wortenden auf unzulässige Trennzeichen.
   local len = Ulen(word)
   for i = 2,2 do
      local ch = Usub(word, i, i)
      if ch == "-" then return nil, "Trennzeichen am Wortanfang" end
   end
   for i = len-1,len-1 do
      local ch = Usub(word, i, i)
      if ch == "-" then return nil, "Trennzeichen am Wortende" end
   end
   return props
end
M.validate_word = validate_word



-- Exportiere Modul-Tabelle.
return M
