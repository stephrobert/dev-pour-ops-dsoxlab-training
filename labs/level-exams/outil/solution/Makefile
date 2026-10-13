# certcheck : installation et tests.
#
#   make install PREFIX=/opt/certcheck   installe PREFIX/bin/certcheck
#   make test                            joue la suite (./test.sh)
#
# L'installation copie le script dans PREFIX/lib/certcheck et écrit un lanceur
# dans PREFIX/bin : l'outil installé ne dépend plus du clone qui l'a construit.

PREFIX ?= /usr/local
DESTINATION := $(abspath $(PREFIX))

.PHONY: install test

install:
	install -d "$(DESTINATION)/bin" "$(DESTINATION)/lib/certcheck"
	install -m 0644 certcheck.py "$(DESTINATION)/lib/certcheck/certcheck.py"
	printf '#!/usr/bin/env bash\nexec python3 "%s/lib/certcheck/certcheck.py" "$$@"\n' "$(DESTINATION)" > "$(DESTINATION)/bin/certcheck"
	chmod 0755 "$(DESTINATION)/bin/certcheck"

test:
	./test.sh
