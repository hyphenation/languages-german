#! /usr/bin/perl -w
#
# apply-pattern.pl
#
# Dieses Perl-Skript wendet die TeX-Trennmusterdatei $1 auf den Datenstrom
# an, wobei $2 als Translationsdatei benutzt wird (das ist diejenige Datei,
# die `patgen' als viertes Argument benötigt).
#
# Folgende Zeichen werden vor der Weiterverarbeitung aus der Eingabe
# herausgefiltert:
#
#   · - = |
#
# Ist Option `-1' nicht gegeben, werden Trennungen direkt nach dem ersten
# und vor dem letzten Buchstaben in der Ausgabe entfernt, wie z.B. bei
# deutschen Trennungen erforderlich.
#
# Dieses Skript benützt patgen, nicht TeX!  Die Trennmusterdatei darf daher
# keine TeX-Konstrukte (Makros u.ä.) enthalten.
#
# Aufruf:  perl apply-pattern.pl trennmuster german.tr < eingabe > ausgabe

use strict;
use Encode;
use File::Spec;
use File::Temp;

use Getopt::Std;
getopts('1');

our ($opt_1);

my $prog = $0;
$prog =~ s@.*/@@;

if ($#ARGV != 1) {
  die "Aufruf:  $prog trennmuster german.tr < eingabe > ausgabe\n" .
      "\n" .
      "  `eingabe', `ausgabe' in UTF-8-Kodierung,\n" .
      "  `trennmuster', `german.tr' in Latin-1-Kodierung\n";
}

sub before_exit {
  chdir($ENV{HOME}) || chdir('/');
}

$SIG{__DIE__} = 'before_exit';

my $trennmuster = File::Spec->rel2abs($ARGV[0]);
my $translation = File::Spec->rel2abs($ARGV[1]);
my $tempdir = File::Temp::tempdir(CLEANUP => 1);
my $tempdatei = "pattern";
my $null = File::Spec->devnull();
my $stdin = "input";

chdir $tempdir
|| die "$prog: Kann nicht ins temporäre Verzeichnis `$tempdir' wechseln: $!\n";

my @eingabe;

open TEMP, '>', $tempdatei
|| die "$prog: Kann temporäre Datei `$tempdatei' nicht öffnen: $!\n";

binmode(STDIN, ":encoding(utf8)");  # Eingabe (wortliste) in UTF-8
binmode(TEMP, ":encoding(latin1)"); # patgen erwartet Latin-1

while (<STDIN>) {
  s/[·=|-]//g;
  push(@eingabe, $_);
  print TEMP $_;
}
close TEMP;

open TEMP, '>', $stdin
|| die "$prog: Kann temporäre Datei `$stdin' nicht öffnen: $!\n";
print TEMP "9 8\n";
print TEMP "y\n";
close TEMP;

# Portables Umleiten von stdin, stdout und stderr ...
open STDOUT_ALT, '>&', \*STDOUT
|| die "$prog: Kann STDOUT nicht duplizieren: $!\n";
open STDERR_ALT, '>&', \*STDERR
|| die "$prog: Kann STDERR nicht duplizieren: $!\n";
open STDOUT, '>', $null
|| die "$prog: Kann STDOUT nicht zur Nullausgabe umleiten: $!\n";
open STDERR, '>', $null
|| die "$prog: Kann STDERR nicht zur Nullausgabe umleiten: $!\n";
open STDIN, $stdin
|| die "$prog: Kann `$stdin' nicht nach STDIN umleiten: $!\n";

my $status = system("patgen $tempdatei $trennmuster $null $translation");
my $fehler = $?;

open STDOUT, '>&', \*STDOUT_ALT
|| die "$prog: Kann STDOUT nicht wieder herstellen: $!\n";
open STDERR, '>&', \*STDERR_ALT
|| die "$prog: Kann STDERR nicht wieder herstellen: $!\n";

die "$prog: Aufruf von patgen fehlgeschlagen: $fehler\n" if $status;

my @muster;
my ($pattmp) = <pattmp.*>;
open PATGEN, $pattmp
|| die "$prog: Kann von patgen erzeugte Datei `$pattmp' nicht öffnen: $!\n";
while (<PATGEN>) {
  s/\./-/g;
  s/^(.)-/$1/ if not $opt_1;
  s/-(.)$/$1/ if not $opt_1;
  push(@muster, $_);
}
close PATGEN;

binmode(STDOUT, ":encoding(utf8)"); # Ausgabe ist wieder UTF-8

while (@eingabe) {
  my @vorlage = split(//, shift(@eingabe));
  my @ergebnis = split(//, shift(@muster));
  my $i = 0;
  my $j = 0;

  # letztes Zeichen ist immer \n, daher < und nicht <=
  while ($i < $#vorlage) {
    $j++ if ($ergebnis[$j] eq '-');
    $ergebnis[$j++] = $vorlage[$i++];
  }
  print @ergebnis;
}

before_exit();

# eof
