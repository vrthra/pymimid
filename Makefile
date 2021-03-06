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
build/%_parser.py: subjects/%.py | build
	$(python) src/rewriter.py $< > $@_
	mv $@_ $@


# Now use the rewritten source to generate trace
arg=*.csv
build/%_trace.json: build/%_parser.py | build
	$(python) $< sample/input/$*/$(arg) > $@_
	mv $@_ $@

#build/datetime_trace.json: arg='HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]'
#build/datetime_trace.json: arg='10:20:41.142561+11:21:29.161278'

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

build/%-grammar.json: build/%_refine.json
	$(python) ./src/merge.py $< > $@_
	mv $@_ $@

build/%-readable.json: build/%-grammar.json
	$(python) ./src/readable.py $< > $@_
	mv $@_ $@

readable-%: build/%-readable.json
	@cat $< | jq .

test:
	set -e; for i in calc urljava urlpy microjson; do echo $$i; make clean; make show target=$$i; done
