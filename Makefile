PY_VERSION := 3
VENV_PATH  := venv
VENV_RPATH := $(shell readlink -m $(VENV_PATH))

.PHONY : venv
venv   :
	virtualenv -qp python$(PY_VERSION) $(VENV_PATH)

.PHONY : xlib
xlib   : venv
	git clone \
		--quiet \
		--depth 1 \
		https://github.com/python-xlib/python-xlib.git $@
	cd $@ && $(VENV_RPATH)/bin/python setup.py install

.PHONY : clean
clean  :
	rm -fr xlib/
