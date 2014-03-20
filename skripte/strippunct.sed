# wird von prepare-wordlist.sh verwendet.

s/[-,'"·*+=~.:;!?()_‚‘’„“”›‹»«@©•—…0-9]/ /g	# ersetzt (fast) alle nichtalphabetischen durch Leerzeichen
s|/| |g					 	# Slash kommt auch mal vor
s|{[^}]*}| |g					# soll {sowas} herausfiltern
s|<[^>]*>| |g					# soll <sowas> herausfiltern
s|\[[^\]]*\]| |g				# soll [sowas] herausfiltern
s|\\[^ ]*| |g					# soll \sowas herausfiltern
s/[IVXLDMC.]\{2,\}/ /g		      		# entfernt römische Zahlen
s/ /\n/g	    				# ersetzt Leerzeichen durch Zeilenumbruch
