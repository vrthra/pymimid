python=python3
export PYTHONPATH=./src:./lib

.SECONDARY:

target=urlpy

all: all-$(target)
	@echo

all-%: build/%_refine.json
	@echo


# rewrite to incorporate a in b => a.in_(b)
# and scopes and tracing.
build/%_parser.py: sample/%.py | build
	$(python) src/rewriter.py $< > $@_
	mv $@_ $@


# Now use the rewritten source to generate trace
arg=
build/%_trace.json: build/%_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@

build/calc_trace.json: arg='(123+133*(12-3)/9+8)+33'
build/calc_trace.json: build/calc_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@

build/microjson_trace.json: arg='{"mykey1": [1, 2, 3], "mykey2": null}'
build/microjson_trace.json: build/microjson_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@

build/urljava_trace.json: arg='http://me:mexico@www.google.com:8080/my/path/q?searc=key&attr=newkey\#frag'
build/urljava_trace.json: build/urljava_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@

build/urlpy_trace.json: arg='http://me:mexico@www.google.com:8080/my/path/q?searc=key&attr=newkey\#frag'
build/urlpy_trace.json: build/urlpy_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@

#build/datetime_trace.json: arg='HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]'
#build/datetime_trace.json: arg='10:20:41.142561+11:21:29.161278'
build/datetime_trace.json: arg='10:20:41.142561'
build/datetime_trace.json: build/datetime_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@

build/netrc_trace.json: arg='machine mymachine.labkey.org login user@labkey.org password mypassword'
build/netrc_trace.json: build/netrc_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@


# Get the derivation tree out
build/%_tree.json: build/%_trace.json | build
	$(python) src/mine.py $<  > $@_
	mv $@_ $@

# Learn the right hand regular expressions from trees.
build/%_generalize.json: build/%_tree.json | build
	$(python) src/generalize_iter.py $< > $@_
	mv $@_ $@

# Get the grammar out
build/%_refine.json: build/%_generalize.json | build
	$(python) src/refine.py $< > $@_
	mv $@_ $@


# |
# Learn the right hand regular expressions from trees.
build/%_learn.json: build/%_refine.json | build
	$(python) src/active_learn.py $< > $@_
	mv $@_ $@

show: all-$(target)
	@for i in build/*_refine.json; do echo $$i; ./bin/show $$i grammar; done

build: ; mkdir -p $@

clean:
	rm -rf build


save:
	mkdir -p .backup
	for i in build/*_refine.json; do j="$$(basename $$i)";k="$$(md5 -q $$i)"; cp $$i ./.backup/"$$j"_"$$k"; done


calc-merge:
	for i in $$(cat sample/calc.csv); do echo $$i; make clean; make build/calc_refine.json arg='"$$i"'; make save; done
	$(python) ./src/merge.py .backup/calc_* > build/calc-grammar.py
	cat build/calc-grammar.py | ./src/show_grammar.py

test:
	set -e; for i in calc urljava urlpy microjson; do echo $$i; make clean; make show target=$$i; done
