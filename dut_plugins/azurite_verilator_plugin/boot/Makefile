
include ./Makefile.inc

default:
	@python create_boot.py $(XLEN)

.PHONY: clean
clean:
	@rm -f azurite.dtb boot.hex config.azurite azurite.dump
