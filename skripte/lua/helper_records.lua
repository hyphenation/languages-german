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
-- <li>Prüfen einer Datei auf Wohlgeformtheit,</li>
-- <li>Prüfen von Datensätzen auf Wohlgeformtheit,</li>
-- <li>Zerlegen von Datensätzen,</li>
-- </ul>
--
-- @class module
-- @name helper_records
-- @author Stephan Hennig
-- @copyright 2012, 2013, Stephan Hennig

-- Die API-Dokumentation kann mit <pre>
--
--   luadoc -d API *.lua
--
-- </pre> erstellt werden.



--[[ just for luadoc 3.0 compatibility
module "helper_records"
--]]
-- lokale Modul-Tabelle
local M = {}



-- Lade Module.
local lpeg = require("lpeg")
local unicode = require("unicode")
local hwords = require("helper_words")



-- Kürzel für LPEG-Funktionen.
local P = lpeg.P
local R = lpeg.R
local C = lpeg.C
local Cc = lpeg.Cc
local Ct = lpeg.Ct
-- Muster für ein beliebiges Zeichen.
local any = P(1)
-- Kürzel für Unicode-Funktionen.
local Ugmatch = unicode.utf8.gmatch
local Ugsub = unicode.utf8.gsub
-- Kürzel für Modul helper_words.
local validate_word = hwords.validate_word



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



-- Diese Liste enthält Datensätze mit bekannten "Fehlern".  Die
-- Datensätze in dieser Liste werden nicht auf Wohlgeformtheit der
-- einzelnen Wörter geprüft.  Schlüssel ist ein Datensatz.  Der Wert
-- darf nicht zu logisch `falsch` auswerten.
local whitelist = {}



--- <strong>nicht-öffentlich</strong> Öffne Ausnahmedatei.
-- Die Datei wird im aktuellen Verzeichnis gesucht, im Verzeichnis `lua`
-- und im Verzeichnis `skripte/lua`, in der angegebenen Reihenfolge.
--
-- @param fname Dateiname
--
-- @return Dateihandle und Pfad der erfolgreich geöffneten
-- Ausnahmedatei.
local function _open_exception_file(fname)
   -- Tabelle möglicher Suchpfade.
   local search_path = {
      "",
      "lua/",
      "skripte/lua/",
   }
   -- Ermittle plattformspezifischen Verzeichnistrenner.
   local dirsep = string.match(package.config, "(.-)\n")
   -- Suche Ausnahmedatei.
   local err = {}
   local f
   for i, path in ipairs(search_path) do
      -- Ersetzte `/` durch geeigneten Verzeichnistrenner.
      path = Ugsub(path, "/", dirsep)
      f, err[i] = io.open(path .. fname, 'r')
      if f then return f, path end
   end
   error(err[1])
end



--- Lese Ausnahmeliste von Datensätzen aus Datei.
--
-- @param fname Dateiname (optional mit Pfad)
--
-- @return Dateiname der erfolgreich gelesenen Datei.
local function read_exception_file(fname)
   local f, path = _open_exception_file(fname)
   -- Lese Datei in einem Rutsch.
   local s = f:read('*all')
   f:close()
   -- Füge Datensätze der Ausnahmeliste hinzu.
   for record in Ugmatch(s, "(.-)\n") do
      whitelist[record] = true
   end
   return path .. fname
end
M.read_exception_file = read_exception_file



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
   -- Verzichte auf Prüfung der Wortstruktur bei bestimmten Datensätzen.
   if whitelist[record] then
      return type
   end
   -- Zerlege Datensatz.
   local trec = split(record)
   -- Merke Inhalt von Feld 1 für Gleichheitsprüfung der belegten
   -- Felder.
   local field1 = trec[1]
   if not field1 then return false, 1, "leer" end
   for i = 1,#trec do
      local word = trec[i]
      if word then
         -- Hat das Wort eine zulässige Struktur?
         local props = validate_word(word)
         if not props then return false, i, props end
         -- Stimmt Wort mit Feld 1 überein?
         word = Ugsub(props.norm_word, "-", "")
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



--- Prüfe einen Korpus auf Wohlgeformtheit.  Geprüft werden das Format
--- der Datensätze und die Zulässigkeit sämtlicher Wörter.
-- Während der Prüfung werden die Häufigkeiten der verschiedenen
-- Datensatztypen erhoben.
--
-- @param f Dateihandle
--
-- @return Tabelle mit Häufigkeiten der Datensatztypen.
local function validate_file(f)
   -- Gesamtzahl der Datensätze.
   local total = 0
   -- Anzahl der ungültigen Datensätze.
   local invalid = 0
   -- Anzahl der identifizierten Datensatztypen.
   local count = {
      ua = 0,
      uxt_ = 0,
      ux_r = 0,
      uxtr = 0,
      ux__c = 0,
      ux__xt__ = 0,
      ux__x_r_ = 0,
      ux__x__s = 0,
      ux__xt_s = 0,
      ux__xtr_ = 0,
      ux__xtrs = 0,
      ux_rc = 0,
      ux_rxtr_ = 0,
      ux_rxtrs = 0,
   }
   -- Iteriere über Zeilen der Eingabe.
   for record in f:lines() do
      total = total + 1
      local type, field, msg = validate_record(record)
      -- Datensatz zulässig?
      if type then
         -- Zähle Vorkommen des Typs.
         count[type] = count[type] + 1
      else
         invalid = invalid + 1
         if type == false then io.stderr:write("Feld ", tostring(field), ": ", msg, ": ", record, "\n")
         else io.stderr:write("ungültiger Datensatz: ", record, "\n")
         end
      end
   end
   f.close()
   count.total = total
   count.invalid = invalid
   return count
end
M.validate_file = validate_file



--- Output record statistics.
-- This function prints all valid record types' frequency.
--
-- @param count Table containing record statistics.
local function output_record_statistics(count)
   print("ua        ", count.ua)
   print("uxt_      ", count.uxt_)
   print("ux_r      ", count.ux_r)
   print("uxtr      ", count.uxtr)
   print("ux__c     ", count.ux__c)
   print("ux__xt__  ", count.ux__xt__)
   print("ux__x_r_  ", count.ux__x_r_)
   print("ux__x__s  ", count.ux__x__s)
   print("ux__xt_s  ", count.ux__xt_s)
   print("ux__xtr_  ", count.ux__xtr_)
   print("ux__xtrs  ", count.ux__xtrs)
   print("ux_rc     ", count.ux_rc)
   print("ux_rxtr_  ", count.ux_rxtr_)
   print("ux_rxtrs  ", count.ux_rxtrs)
end
M.output_record_statistics = output_record_statistics



-- Exportiere Modul-Tabelle.
return M