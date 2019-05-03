python=python3
export PYTHONPATH=./src

.SECONDARY:

all: build/calc_refine.json
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

show:
	./bin/show build/calc_refine.json grammar

build: ; mkdir -p $@

clean:
	rm -rf build
