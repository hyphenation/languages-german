-- -*- coding: utf-8 -*-

--- Diese Modul stellt Funktionen zur Zerlegung der Wortliste in einzelne
-- Felder bereit.
-- @class module
-- @name parse_wortliste


-- lokale Modul-Tabelle
local M = {}


-- Kurze Beschreibung des Formats der Wortliste:
--
-- Jede Zeile enthält eine bestimmte Schreibvariante eines Wortes.
-- Unterschiedliche Schreibvarianten desselben Wortes sind nicht
-- miteinander verknüpft.
--
-- Feldtrenner ist das Semikolon.  Kommentare werden durch '#'
-- eingeleitet und erstrecken sich bis zum Zeilenende.  Vor dem
-- Kommentarzeichen sind beliebige Leerzeichen erlaubt.
--
-- Leere Felder bestehen aus der Feldnummer eingeschlossen in
-- Minuszeichen, z. B. steht -2- für ein leeres Feld 2.
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
--
-- Definiere Muster für einige Spezialzeichen.
local sep = lpeg.P ";"-- Feldtrenner
local com = lpeg.P "#"-- Kommentar
local spc = lpeg.P " "-- Leerzeichen
local num = lpeg.R "09"-- Ziffern
--
-- Muster für Felder mit festem Inhalt (leere Felder).
local leer2 = lpeg.P "-2-"
local leer3 = lpeg.P "-3-"
local leer4 = lpeg.P "-4-"
local leer5 = lpeg.P "-5-"
local leer6 = lpeg.P "-6-"
local leer7 = lpeg.P "-7-"
local leer8 = lpeg.P "-8-"
local leerX = lpeg.P "-" * num * lpeg.P "-"
-- Kürzel für leere Felder mit voranstehendem Feldtrenner.
local _leer2 = sep * leer2
local _leer3 = sep * leer3
local _leer4 = sep * leer4
local _leer5 = sep * leer5
local _leer6 = sep * leer6
local _leer7 = sep * leer7
local _leer8 = sep * leer8
--
-- Muster für ein Feld beliebigen Inhalts, welches nicht mit -[0-9]-
-- beginnt.  Die Capture enthält den Feldinhalt.
local feld = (lpeg.C((1 - (sep + spc + com))^0) - leerX)
-- Kürzel für Feld mit voranstehendem Feldtrenner.
local _feld = sep * feld
--
-- Muster für Kommentare der Form: beliebig viele Leerzeichen, gefolgt
-- von einem Kommentarzeichen, gefolgt von beliebigem Inhalt bis zum
-- Zeilenende.  Die Capture enthält den eigentlichen Kommentartext ohne
-- das Kommentarzeichen.
local opcomment = spc^0 * (com * lpeg.C(lpeg.P(1)^0))^-1 * -1
--
--
--
-- Grammatik für die Strukturprüfung der Wortliste.
-- Welche Felder sind belegt, welche unbelegt?
-- Jeder Regel folgt eine Beispielzeile.
--
-- Muster für Wörter, die keiner expliziten Versalschreibung
-- entsprechen.  (Die Felder 5 bis 8 existieren nicht.)
--
local ua = feld * _feld * opcomment
-- einfach;ein·fach
--
local uxt_ = feld * _leer2 * _feld * _leer4 * opcomment
-- Abfallager;-2-;Ab·fa{ll/ll·l}a·ger;-4-
-- Abfluß;-2-;Ab-fluß;-4-
--
local ux_r = feld * _leer2 * _leer3 * _feld * opcomment
-- Abfalllager;-2-;-3-;Ab-fall=la-ger
--
local uxtr = feld * _leer2 * _feld * _feld * opcomment
-- abgelöste;-2-;ab-ge-lö-ste;ab-ge-lös-te
--
--
-- Muster für Wörter, die expliziter Versalschreibung entsprechen ('ß'
-- durch 'ss' ersetzt).
--
local ux__c = feld * _leer2 * _leer3 * _leer4 * _feld * opcomment
-- Abstoss;-2-;-3-;-4-;Ab·stoss
--
local ux__xt__ = feld * _leer2 * _leer3 * _leer4 * _leer5 * _feld * _leer7 * _leer8 * opcomment
-- Litfasssäulenstilleben;-2-;-3-;-4-;-5-;Lit-fass-säu-len-sti{ll/ll-l}e-ben;-7-;-8-
--
local ux__x_r_ = feld * _leer2 * _leer3 * _leer4 * _leer5 * _leer6 * _feld * _leer8 * opcomment
-- Fussballliga;-2-;-3-;-4-;-5-;-6-;Fuss·ball·li·ga;-8-
--
local ux__x__s = feld * _leer2 * _leer3 * _leer4 * _leer5 * _leer6 * _leer7 * _feld * opcomment
-- Litfassäule;-2-;-3-;-4-;-5-;-6-;-7-;Lit·fa{ss/ss·s}äu·le
--
local ux__xtr_ = feld * _leer2 * _leer3 * _leer4 * _leer5 * _feld * _feld * _leer8 * opcomment
-- süsssauer;-2-;-3-;-4-;-5-;süss·sau·er;süss·sau·er;-8-
--
local ux__xt_s = feld * _leer2 * _leer3 * _leer4 * _leer5 * _feld * _leer7 * _feld * opcomment
-- Fussballiga;-2-;-3-;-4-;-5-;Fuss·ba{ll/ll·l}i·ga;-7-;Fuss·ba{ll/ll·l}i·ga
--
local ux__xtrs = feld * _leer2 * _leer3 * _leer4 * _leer5 * _feld * _feld * _feld * opcomment
-- Füsse;-2-;-3-;-4-;-5-;Fü·sse;Füs·se;Füs·se
--
--
-- Muster für Wörter, die in der reformierten Rechtschreibung
-- existieren, in der traditionellen Rechtschreibung jedoch nur in
-- Versalschreibweise ('ß' durch 'ss' ersetzt).
--
local ux_rc = feld * _leer2 * _leer3 * _feld * _feld * opcomment
-- Abfluss;-2-;-3-;Ab-fluss;Ab·fluss
--
local ux_rxtr_ = feld * _leer2 * _leer3 * _feld * _leer5 * _feld * _feld * _leer8 * opcomment
-- Litfasssäule;-2-;-3-;Lit·fass·säu·le;-5-;Lit·fass·säu·le;Lit·fass·säu·le;-8-
--
local ux_rxtrs = feld * _leer2 * _leer3 * _feld * _leer5 * _feld * _feld * _feld * opcomment
-- dussligste;-2-;-3-;duss·ligs·te;-5-;duss·lig·ste;duss·ligs·te;duss·lig·ste


--- Zerlege eine Zeile der Wortliste.
-- @param line eine Zeile aus der Wortliste
-- @return Tabelle mit gültigen Feldern
local function parse(line)
  local u, a, t, r
  local ca, ct, cr, cs
  local com

  u, a, com = ua:match(line)
  if u and a then return { u = u, a = a, comment = com, type = "ua" } end

  u, t, com = uxt_:match(line)
  if u and t then return { u = u, t = t, comment = com, type = "uxt_" } end

  u, r, com = ux_r:match(line)
  if u and r then return { u = u, r = r, comment = com, type = "ux_r" } end

  u, t, r, com = uxtr:match(line)
  if u and t and r then return { u = u, t = t, r = r, comment = com, type = "uxtr" } end



  u, ca, com = ux__c:match(line)
  if u and ca then return { u = u, ca = ca, comment = com, type = "ux__c" } end

  u, ct, com = ux__xt__:match(line)
  if u and ct then return { u = u, ct = ct, comment = com, type = "ux__xt__" } end

  u, cr, com = ux__x_r_:match(line)
  if u and cr then return { u = u, cr = cr, comment = com, type = "ux__x_r_" } end

  u, cs, com = ux__x__s:match(line)
  if u and cs then return { u = u, cs = cs, comment = com, type = "ux__x__s" } end

  u, ct, cs, com = ux__xt_s:match(line)
  if u and ct and cs then return { u = u, ct = ct, cs = cs, comment = com, type = "ux__xt_s" } end

  u, ct, cr, com = ux__xtr_:match(line)
  if u and ct and cr then return { u = u, ct = ct, cr = cr, comment = com, type = "ux__xtr_" } end

  u, ct, cr, cs, com = ux__xtrs:match(line)
  if u and ct and cr and cs then return { u = u, ct = ct, cr = cr, cs = cs, comment = com, type = "ux__xtrs" } end



  u, r, ca, com = ux_rc:match(line)
  if u and r and ca then return { u = u, r = r, ca = ca, comment = com, type = "ux_rc" } end

  u, r, ct, cr, com = ux_rxtr_:match(line)
  if u and r and ct and cr then return { u = u, r = r, ct = ct, cr = cr, comment = com, type = "ux_rxtr_" } end

  u, r, ct, cr, cs, com = ux_rxtrs:match(line)
  if u and r and ct and cr and cs then return { u = u, r = r, ct = ct, cr = cr, cs = cs, comment = com, type = "ux_rxtrs" } end

  return nil
end
M.parse = parse


-- Exportiere Modul-Tabelle.
return M
