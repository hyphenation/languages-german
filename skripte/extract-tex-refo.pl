#! /usr/bin/perl -w
#
# extract-tex-refo.pl
#
# Dieses Perl-Skript extrahiert aus der `wortliste'-Datei eine Eingabedatei
# für Patgen, und zwar für die reformierte deutsche Rechtschreibung.
#
# Aufruf:  perl extract-tex-refo.pl [-g] [-u] [-v] < wortliste > input.patgen
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
# Doppeldeutigkeiten (Konstrukte der Art `[.../...]') werden immer entfernt.

use strict;
use utf8;         # String-Literals direkt als UTF-8
use Getopt::Std;
getopts('guv');

our ($opt_g, $opt_u, $opt_v);

my $prog = $0;
$prog =~ s@.*/@@;

# Kodierung:
binmode(STDIN, ":encoding(utf8)");    # Eingabe (wortliste) in UTF-8
binmode(STDOUT, ":encoding(latin1)"); # patgen erwartet Latin-1

while (<>) {
  chop;
  next if /^#/;

  # entferne Kommentare
  s/#.*$//;

  # entferne Leerzeichen aller Art
  s/\s+//g;

  my @feld = split(';');
  next if $#feld < 0;

  # Felder 2, 4, 5 und 7
  my $zeile = $feld[1];
  $zeile = $feld[3] if defined $feld[3] && $feld[3] ne "-4-";
  $zeile = $feld[4] if defined $feld[4] && $feld[4] ne "-5-" && !$opt_v;
  $zeile = $feld[6] if defined $feld[6] && $feld[6] ne "-7-" && !$opt_v;
  next if $zeile eq "-2-";

  # entferne Doppeldeutigkeiten; 
  $zeile =~ s;\[ [-=|·]* (.*?) [-=|·]* / .*? \];$1;gx;

  # Ausgabe von Wörtern mit unerwünschten Trennungen?
  next if $zeile =~ /[._]/ and $opt_u;
  # entferne Markierungen für unerwünschte Trennungen
  $zeile =~ s/[._]//g;

  # Ausgabe von Wörtern mit ungewichteten Trennstellen?
  next if $zeile =~ /·/ and $opt_g;
  # reduziere Trennstellenmarker zu `-', falls gewollt
  $zeile =~ s/[·|=-]+/-/g if not $opt_g;

  print "$zeile\n";
}

# eof
