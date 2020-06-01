RULESFILES:=$(shell find . -name '*.txt')
PREFIX=/usr/local
bindir=$(PREFIX)/bin
INSTALL=install

all: user-install

user-install:
	@mkdir -p ~/.latex-rules/
	@for p in $(RULESFILES); do \
		$(INSTALL) -m0644 $$p ~/.latex-rules/; \
	done
	@mkdir -p $(bindir)
	@$(INSTALL) -m0755 latex-lint.py $(bindir);
	