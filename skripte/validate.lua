-- -*- coding: utf-8 -*-

--[[

Copyright 2012, 2013, 2014, 2015 Stephan Hennig

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
   blame = "b",
   help = "h",
   statistics = "s",
}
local opt = alt_getopt.get_opts(arg, "b:hs", long_opts)

-- Option --help
if opt.h then
   print([[
Aufruf: texlua validate.lua [OPTIONEN]
Dieses Skript prüft eine Wortliste auf Wohlgeformtheit.  Die Wortliste
wird von der Standardeingabe gelesen.
  -b  --blame       file    show erroneous commits
                            Reads records from file instead of stdin.
  -h, --help                print help
  -s, --statistics          output record statistics
]]
   )
   os.exit()
end


-- Lese Ausnahmeliste.
local fname_ex = "wortliste.ausnahmen"
fname_ex = hrecords.read_regular_exceptions(fname_ex)
print("Verwende Ausnahmeliste " .. fname_ex)


-- Speichere Dateinamenargument der Option --blame.
local fname_db = opt.b
-- Lese von Standardeingabe oder aus Datei.
local fin_db = fname_db and assert(io.open(fname_db, "r")) or io.stdin


-- Prüfe Wortliste.
local info = hrecords.validate_file(fin_db)


-- Ausgabe.
if opt.s then
   hrecords.output_record_statistics(info.cnt_rectypes)
end
print("gesamt    ", info.cnt_total)
print("ungültig  ", info.cnt_invalid)


-- Zeige fehlerhafte Commits.
if opt.b then
   -- Erstelle git-blame-Kommando mit verketteten Zeilennummern.
   local call = "git blame"
   for _,lineno in ipairs(info.bad_lineno) do
      call = call .. " -L " .. lineno .."," .. lineno
   end
   call = call .. " " .. fname_db
   -- Tabelle, die Commits auf Zähler abbildet.
   local bad_commits = {}
   -- Tabelle, die Commits auf Datumswerte abbildet.
   local commit_date = {}
   -- Verarbeite Ergebnis des git-blame-Kommandos.
   local f = assert(io.popen(call))
   for line in f:lines() do
      -- Extrahiere Commit-Hash und Datum.
      local commit, date = string.match(line, "^(%w+) %(.-(%d%d%d%d%-%d%d%-%d%d)")
      bad_commits[commit] = (bad_commits[commit] or 0) + 1
      commit_date[commit] = date
   end
   f:close()
   -- Sortiere Commits nach Datum.
   local commits = {}
   for commit,_ in pairs(commit_date) do
      table.insert(commits, commit)
   end
   table.sort(commits, function(a,b) return commit_date[a] < commit_date[b] end)
   -- Gebe Commits nach Datum sortiert aus.
   for _,commit in ipairs(commits) do
      io.stderr:write("Commit ", commit, " ", commit_date[commit], ": ", bad_commits[commit], "\n")
   end
end


-- Ende mit Fehlerkode?
if info.cnt_invalid > 0 then os.exit(1) end
