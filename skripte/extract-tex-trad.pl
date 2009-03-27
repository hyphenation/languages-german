#! /usr/bin/perl -w
#
# extract-tex-trad.pl
#
# Dieses Perl-Skript extrahiert aus der `wortliste'-Datei eine Eingabedatei
# für Patgen, und zwar für die traditionelle deutsche Rechtschreibung.
#
# Aufruf:  perl extract-tex-trad.pl [-u] [-g] < wortliste > input.patgen
#
# Option `-u' verhindert die Ausgabe von Wörtern mit Markern für
# unerwünschte Trennungen (z.B. `An-al.pha-bet').
#
# Option `-g' bewirkt die Ausgabe von gewichteten Trennstellen; es wird
# also nur `·' in `-' konvertiert, nicht aber `=' und `_'.

use strict;
use Getopt::Std;
getopts('gu');

our ($opt_g, $opt_u);

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
  $zeile = $feld[4] if defined $feld[4] && $feld[4] ne "-5-";
  $zeile = $feld[5] if defined $feld[5] && $feld[5] ne "-6-";
  next if $zeile eq "-2-";

  # entferne spezielle Trennungen
  $zeile =~ s/\{(.*?)\|.*?\}/$1/g;
  # entferne Doppeldeutigkeiten
  $zeile =~ s/\[-*(.*?)-*\|.*?\]/$1/g;

  # Ausgabe von Wörtern mit unerwünschten Trennungen?
  next if /\./ and $opt_u;
  # entferne Markierungen für unerwünschte Trennungen
  $zeile =~ s/\.//g;

  # reduziere ungewichtete Trennstellen zu `-'; \xb7 ist `·' in
  # Latin-1-Kodierung
  $zeile =~ s/\xb7/-/g;
  # reduziere gewichtete und ungewichtete Trennstellen zu `-', falls gewollt
  $zeile =~ s/[=_]/-/g if not $opt_g;

  print "$zeile\n";
}

# eof
