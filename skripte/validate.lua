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


-- Lese Ausnahmeliste.
local fname = "wortliste.ausnahmen"
fname = hrecords.read_exception_file(fname)
print("Verwende Ausnahmeliste " .. fname)


-- Prüfe Wortliste auf Standardeingabe.
local info = hrecords.validate_file(io.stdin)


-- Ausgabe.
if opt.s then
   hrecords.output_record_statistics(info.cnt_rectypes)
end
print("gesamt    ", info.cnt_total)
print("ungültig  ", info.cnt_invalid)


-- Ende mit Fehlerkode?
if info.cnt_invalid > 0 then os.exit(1) end
