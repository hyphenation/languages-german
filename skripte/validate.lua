-- -*- coding: utf-8 -*-

local pwl = require("parse_wortliste")

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

-- Iteriere über stdin.
for line in io.lines() do
   total = total + 1
   local type, field, msg = pwl.validate_record(line)
   -- Datensatz zulässig?
   if type then
      -- Zähle Vorkommen des Typs.
      count[type] = count[type] + 1
   else
      invalid = invalid + 1
      if type == false then print("Feld " .. tostring(field) .. ": " .. msg .. ": " .. line)
      else print("ungültiger Datensatz: " .. line)
      end
   end
end

-- Ausgabe.
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
io.stderr:write("gesamt    ", total, "\n")
io.stderr:write("ungültig  ", invalid, "\n")
