#! /usr/bin/perl -w
#
# extract-tex-trad.pl
#
# Dieses Perl-Skript extrahiert aus der `wortliste'-Datei eine Eingabedatei
# für Patgen, und zwar für die traditionelle deutsche Rechtschreibung.
#
# Aufruf:  perl extract-tex-trad.pl [-g] [-u] [-v] < wortliste > input.patgen
#
# Option `-g' bewirkt die Ausgabe von Wörtern mit gewichteten Trennstellen;
# Wörter mit `·' werden ignoriert.
#
# Option `-u' verhindert die Ausgabe von Wörtern mit Markern für
# unerwünschte Trennungen (z.B. `An-al.pha-bet').
#
# Option `-v' verhindert die Ausgabe von Versalformen, wo `ß' durch `ss'
# ersetzt ist.
#
# Konstrukte, die spezielle Trennungen (`{.../...}') und Doppeldeutigkeiten
# (`[.../...]') anzeigen, werden immer entfernt.

use strict;
use Getopt::Std;
getopts('guv');

our ($opt_g, $opt_u, $opt_v);

my $prog = $0;
$prog =~ s@.*/@@;

while (<>) {
  chop;
  next if /^#/;

  # entferne Kommentare
  s/#.*$//;

  # entferne Leerzeichen aller Art
  s/\s+//g;

  my @feld = split(';');
  next if $#feld < 0;

  # Felder 2, 3, 5 und 6
  my $zeile = $feld[1];
  $zeile = $feld[2] if defined $feld[2] && $feld[2] ne "-3-";
  $zeile = $feld[4] if defined $feld[4] && $feld[4] ne "-5-" && !$opt_v;
  $zeile = $feld[5] if defined $feld[5] && $feld[5] ne "-6-" && !$opt_v;
  next if $zeile eq "-2-";

  # entferne spezielle Trennungen
  $zeile =~ s|\{(.*?)/.*?\}|$1|g;
  # entferne Doppeldeutigkeiten; \xb7 ist `·' in
  # Latin-1-Kodierung
  $zeile =~ s;\[[-=|\xb7]*(.*?)[-=|\xb7]*/.*?\];$1;g;

  # Ausgabe von Wörtern mit unerwünschten Trennungen?
  next if $zeile =~ /[._]/ and $opt_u;
  # entferne Markierungen für unerwünschte Trennungen
  $zeile =~ s/[._]//g;

  # Ausgabe von Wörtern mit ungewichteten Trennstellen?
  next if $zeile =~ /\xb7/ and $opt_g;
  # reduziere Trennstellenmarker zu `-', falls gewollt
  $zeile =~ s/[\xb7|=-]+/-/g if not $opt_g;

  print "$zeile\n";
}

# eof
