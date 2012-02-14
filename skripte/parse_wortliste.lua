-- -*- coding: utf-8 -*-

--- Diese Modul stellt Funktionen zur Zerlegung der Wortliste in einzelne
-- Felder bereit.
-- @class module
-- @name parse_wortliste


-- lokale Modul-Tabelle
local M = {}


-- Kürzel für LPEG-Funktionen.
local P = lpeg.P
local R = lpeg.R
local C = lpeg.C
local Cc = lpeg.Cc
local Ct = lpeg.Ct
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
-- zulässigen Wörtern in Form einer Grammatik wird später hinzugefügt.
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



-- Exportiere Modul-Tabelle.
return M
