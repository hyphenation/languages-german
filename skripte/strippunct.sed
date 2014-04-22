# wird von prepare-wordlist.sh verwendet.

s|/| |g					 	# Slash raus
s|{[^}]*}| |g					# soll {sowas} herausfiltern
s|<[^>]*>| |g					# soll <sowas> herausfiltern
s|\[[^\]]*\]| |g				# soll [sowas] herausfilterna  ← erwischt irgendwie nicht alle. ?
s|\\[^ ]*| |g					# soll \sowas herausfiltern
s|\&[^ ]*\;| |g					# lösche Entities wie &nbsp;
s/[-,'"·*+=~.:;!?()_‚‘’„“”›‹»«@©•—…0-9]/ /g	# ersetzt (fast) alle nichtalphabetischen durch Leerzeichen
s/[IVXLDMC.]\{2,\}/ /g		      		# entfernt römische Zahlen
s/ /\n/g	    				# ersetzt Leerzeichen durch Zeilenumbruch
