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
--- <strong>nicht-öffentlich</strong> Diese Funktion wird in einer
--- Funktionscapture genutzt, um Captures zusammenzufügen.
--
-- @param ... eine beliebige Zahl von Captures
--
-- @return Ergebniscapture (String)
local function _concatenate_captures(...)
--   io.stderr:write("conc: ",Tconcat({...}, ","),"\n")-- For debugging purposes.
   return Tconcat({...})
end
--
--- <strong>nicht-öffentlich</strong> Diese Funktion wird in einer
--- Funktionscapture verwendet, um die Gleichheit zweier Captures
--- festzustellen.  Falls zwei Captures ungleich sind, so wird dies in
--- Tabelle <code>word_property</code> vermerkt.  Die zweite Capture
--- wird immer verworfen.
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
   part_word = V"ophyphen" * (V"cluster" * (V"hyphen" * V"cluster")^0) / _concatenate_captures * V"ophyphen",
   -- Ein Kluster besteht aus mehreren aneinandergereihten fundamentalen
   -- Klustern ohne Unterbrechung durch Trennzeichen.  Es gibt drei
   -- Arten von fundamentalen Klustern: Buchstabenkluster,
   -- Spezialtrennungen und Alternativen:
   --
   --                 Bü-cher   E{ck/k-k}e   Sto{ff/ff-f}et-zen   Wach[-s/s-]tu-be
   -- fund. Kluster   11-2222   1222222223   11122222222233-444   1111222222233-44
   -- Kluster         11-2222   1111111111   11111111111111-222   1111111111111-22
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
   alt_rule = (V"alt_1st" * V"alt_sep" * V"alt_2nd") / _is_equal_two_alternatives,
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
   --
   -- Trennstellen
   --
   -- Die Markierung von Trennstellen erfolgt zunächst nach deren
   -- morphologischer Struktur.  Wahlweise kann auch eine zusätzliche,
   -- qualitative Bewertung erfolgen.
   --
   -- morphologisch
   --
   -- innerhalb von Wortstämmen oder vor Suffixen
   hyphen_inner = V"hyphen_ch_inner"^1,
   -- nach Präfixen oder Verbalpartikeln
   hyphen_prefix = V"hyphen_ch_prefix"^1,
   -- an Wortfugen
   hyphen_compound = V"hyphen_ch_compound"^1,
   -- Präfix eines zusammengesetzten Wortes
   hyphen_compound_prefix = V"hyphen_ch_prefix" * V"hyphen_compound",
   -- Suffix eines zusammengesetzten Wortes
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
   -- qualitativ
   --
   -- eine Bewertung
   hyphen_quality = V"hyphen_ch_quality" * V"hyphen_ch_quality"^-2,
   -- eine optionale Bewertung
   hyphen_opt_quality = V"hyphen_quality"^-1,
   --
   -- unkategorisiert
   --
   hyphen_uncategorized = V"hyphen_ch_uncategorized",
   --
   -- Eine beliebige Trennstelle ist entweder unkategorisiert oder
   -- morphologisch markiert mit optional folgender Bewertung.  Die
   -- Bewertung kann auch alleinstehen.
   hyphen = V"hyphen_uncategorized"
      + V"hyphen_morph" * V"hyphen_opt_quality"
      + V"hyphen_quality"
,
   --
   -- Ein beliebiges, optionales Trennzeichen.
   ophyphen = V"hyphen"^-1,
   --
   -- Die folgenden Trennzeichen werden verwendet:
   hyphen_ch_inner = P"-",
   hyphen_ch_prefix = P"|",
   hyphen_ch_compound = P"=",
   hyphen_ch_quality = P".",
   hyphen_ch_uncategorized = P"·",
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
   -- Ersetze Alternativen durch erste Alternative (ohne Trennzeichen).
   rawword = Ugsub(rawword, "%[(.-)/.-%]",
                   -- Entferne Trennzeichen im Fluge.
                   function (capture)
                      return Ugsub(capture, "[-|=%.·]+", "")
                   end
   )
   -- Ersetze Trennzeichen durch "-".
   rawword = Ugsub(rawword, "[|=%.·]+", "-")
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



-- Exportiere Modul-Tabelle.
return M
