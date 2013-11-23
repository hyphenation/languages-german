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


-- Lese Konfigurationdaten aus.
local path_dirsep, path_sep, path_subst = string.match(package.config, "(.-)\n(.-)\n(.-)\n")
-- Erweitere Modulsuchpfad.
package.path = package.path
   .. path_sep .. "lua" .. path_dirsep .. path_subst .. ".lua"
   .. path_sep .. "skripte" .. path_dirsep .. "lua" .. path_dirsep .. path_subst .. ".lua"

-- Lade Module aus Lua-Pfad.
local hrecords = require("helper_records")

-- Lade Module aus TEXMF-Baum.
kpse.set_program_name('luatex')
local alt_getopt = require("alt_getopt")


-- Erkläre zulässige Optionen.
local long_opts = {
   help = "h",
   statistics = "s",
}
local opt = alt_getopt.get_opts(arg, "hs", long_opts)


-- Option --help
if opt.h then
   print([[
Aufruf: texlua validate.lua [OPTIONEN]
Dieses Skript prüft eine Wortliste auf Wohlgeformtheit.  Die Wortliste
wird von der Standardeingabe gelesen.
  -h, --help                print help
  -s, --statistics          output record statistics
]]
   )
   os.exit()
end


-- Anzahl Gesamtzeilen
local total = 0
-- Anzahl der ungültigen Zeilen.
local invalid = 0
-- Anzahl der identifizierten Zeilentypen.
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

-- Lese Ausnahmeliste.
local fname = "wortliste.ausnahmen"
fname = hrecords.read_exception_file(fname)
print("Verwende Ausnahmeliste " .. fname)

-- Iteriere über stdin.
for line in io.lines() do
   total = total + 1
   local type, field, msg = hrecords.validate_record(line)
   -- Datensatz zulässig?
   if type then
      -- Zähle Vorkommen des Typs.
      count[type] = count[type] + 1
   else
      invalid = invalid + 1
      if type == false then io.stderr:write("Feld ", tostring(field), ": ", msg, ": ", line, "\n")
      else io.stderr:write("ungültiger Datensatz: ", line, "\n")
      end
   end
end

-- Ausgabe.
if opt.s then
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
print("gesamt    ", total)
print("ungültig  ", invalid)


-- Ende mit Fehlerkode?
if invalid > 0 then os.exit(1) end
