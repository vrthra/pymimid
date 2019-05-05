export
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

build/calc_trace.json: arg=1.csv
build/calc_trace.json: build/calc_parser.py | build
	$(python) $< sample/input/calc/$(arg) > $@_
	mv $@_ $@

build/microjson_trace.json: arg=1.csv
build/microjson_trace.json: build/microjson_parser.py | build
	$(python) $< sample/input/microjson/$(arg) > $@_
	mv $@_ $@

build/urljava_trace.json: arg=1.csv
build/urljava_trace.json: build/urljava_parser.py | build
	$(python) $< sample/input/urljava/$(arg) > $@_
	mv $@_ $@

build/urlpy_trace.json: arg=1.csv
build/urlpy_trace.json: build/urlpy_parser.py | build
	$(python) $< sample/input/urlpy/$(arg) > $@_
	mv $@_ $@

#build/datetime_trace.json: arg='HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]'
#build/datetime_trace.json: arg='10:20:41.142561+11:21:29.161278'
build/datetime_trace.json: arg='10:20:41.142561'
build/datetime_trace.json: build/datetime_parser.py | build
	$(python) $< sample/input/calc/$(arg) > $@_
	mv $@_ $@

build/netrc_trace.json: arg='machine mymachine.labkey.org login user@labkey.org password mypassword'
build/netrc_trace.json: build/netrc_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@

GENERALIZE=yes
ifeq ($(GENERALIZE), yes)
# Get the derivation tree out
build/%_ngtree.json: build/%_trace.json | build
	$(python) src/mine.py $< > $@_
	mv $@_ $@

build/%_tree.json: build/%_ngtree.json | build
	$(python) src/generalize_iter.py $< > $@_
	mv $@_ $@

else
build/%_tree.json: build/%_trace.json | build
	$(python) src/mine.py $<  > $@_
	mv $@_ $@
endif

# Get the grammar out
build/%_refine.json: build/%_tree.json | build
	$(python) src/refine.py $< > $@_
	mv $@_ $@

# Now, abstract the while loops and ifs with regex so that
# we can remove redundant loop indices. We may need to remove
# looop indices beyond a certain point simply because we
# do not have enough samples.

show: all-$(target)
	@for i in build/*_refine.json; do echo $$i; ./bin/show $$i grammar; done

build: ; mkdir -p $@

clean:
	rm -rf build

clobber-%: clean
	rm -rf .backup/$*_*

clobber: clean
	rm -rf .backup

save:
	mkdir -p .backup
	for i in build/*.json; do j="$$(basename $$i)";k="$$(md5 -q $$i)"; cp $$i ./.backup/"$$j"_"$$k"_$(name); done


build/%-egrammar.json:
	for i in sample/input/$*/*.csv; do echo $$i; f="$$(basename $$i)"; echo $$f; make clean; make build/$*_refine.json arg="$$f"; make save name=$$f; done
	$(python) ./src/merge.py .backup/$*_refine* > $@_
	mv $@_ $@

build/%-grammar.json: build/%-egrammar.json
	$(python) ./src/simplify.py $< > $@_
	mv $@_ $@

build/%-readable.txt: build/%-grammar.json
	$(python) ./src/readable.py $< > $@_
	mv $@_ $@

readable-%: build/%-readable.txt
	@cat $<

test:
	set -e; for i in calc urljava urlpy microjson; do echo $$i; make clean; make show target=$$i; done
