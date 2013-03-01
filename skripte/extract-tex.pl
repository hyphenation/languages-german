#! /usr/bin/perl -w
#
# extract-tex.pl
#
# Dieses Perl-Skript extrahiert aus der »wortliste«-Datei eine Eingabedatei
# für Patgen.
#
# Aufruf:  perl extract-tex.pl [Optionen...] < wortliste > input.patgen
#
# Option »-t« wählt die traditionelle deutsche Rechtschreibung aus, Option
# »-s« die traditionelle (deutsch)schweizerische Rechtschreibung.  Wenn
# weder »-s« noch »-t« gesetzt ist, wird die reformierte deutsche
# Rechtschreibung ausgewählt.
#
# Option »-g« bewirkt die Ausgabe von Wörtern mit gewichteten Trennstellen;
# Wörter mit »·« werden ignoriert.
#
# Option »-d« bewirkt die Ausgabe von Doppeldeutigkeiten (also Konstrukte
# der Art »[.../...]«).
#
# Option »-u« verhindert die Ausgabe von Wörtern mit Markern für
# unerwünschte Trennungen (z.B. »An-al.pha-bet«).
#
# Option »-v« verhindert die Ausgabe von Versalformen, wo »ß« durch »ss«
# ersetzt ist.

use strict;
use utf8;         # String-Literals direkt als UTF-8
use Getopt::Std;
getopts('dgstuv');

our ($opt_d, $opt_g, $opt_s, $opt_t, $opt_u, $opt_v);

my $prog = $0;
$prog =~ s@.*/@@;

# Kodierung:
binmode(STDIN, ":encoding(utf8)");    # Eingabe (wortliste) in UTF-8
binmode(STDOUT, ":encoding(latin1)"); # patgen erwartet Latin-1

sub entferne_marker {
  my $arg = shift;
  $arg =~ s/[-=|·]//g;
  return $arg;
}

while (<>) {
  chop;
  next if /^#/;

  # entferne Kommentare
  s/#.*$//;

  # entferne Leerzeichen aller Art
  s/\s+//g;

  my @feld = split(';');
  next if $#feld < 0;

  # reformiert:           Felder 2, 4, 5, 7
  # traditionell:         Felder 2, 3, 5, 6
  # traditionell Schweiz: Felder 2, 3, 5, 6, 8
  my $zeile = $feld[1];
  $zeile = $feld[2] if defined $feld[2]
                       && $feld[2] ne "-3-" && ($opt_t || $opt_s);
  $zeile = $feld[3] if defined $feld[3]
                       && $feld[3] ne "-4-" && !($opt_t || $opt_s);
  $zeile = $feld[4] if defined $feld[4]
                       && $feld[4] ne "-5-" && !$opt_v;
  $zeile = $feld[5] if defined $feld[5]
                       && $feld[5] ne "-6-" && ($opt_t || $opt_s) && !$opt_v;
  $zeile = $feld[6] if defined $feld[6]
                       && $feld[6] ne "-7-" && !($opt_t || $opt_s) && !$opt_v;
  $zeile = $feld[7] if defined $feld[7]
                       && $feld[7] ne "-8-" && $opt_s && !$opt_v;

  next if $zeile eq "-2-";

  # entferne spezielle Trennungen
  $zeile =~ s|\{ (.*?) / .*? \}|$1|gx if ($opt_t || $opt_s);
  # entferne Doppeldeutigkeiten
  $zeile =~ s|\[ (.*?) / .*? \]|entferne_marker($1)|egx if !$opt_d;

  # Ausgabe von Wörtern mit unerwünschten Trennungen?
  next if $zeile =~ /[._]/ and $opt_u;
  # entferne Markierungen für unerwünschte Trennungen
  $zeile =~ s/[._]//g;

  # Ausgabe von Wörtern mit ungewichteten Trennstellen?
  next if $zeile =~ /·/ and $opt_g;
  # reduziere Trennstellenmarker zu »-«, falls gewollt
  $zeile =~ s/[·|=-]+/-/g if not $opt_g;

  print "$zeile\n";
}

# eof
