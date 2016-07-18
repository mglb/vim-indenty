PLUGIN_NAME := indenty

VIMRC := $(PLUGIN_NAME).vimrc

define VIMRC_CONTENT
so /etc/vim/vimrc
so $$HOME/.vimrc
set runtimepath^=$(CURDIR)
endef
export VIMRC_CONTENT


all: test_vim

$(VIMRC): Makefile
	echo "$$VIMRC_CONTENT" > $@

test_vim: $(VIMRC)
	vim --not-a-term -u $(VIMRC)


clean:
	rm -f $(VIMRC)

.PHONY: test_vim clean

