python=python3
export PYTHONPATH=./src




# rewrite to incorporate a in b => a.in_(b)
# and scopes and tracing.
build/%_parser.py: sample/%.py | build
	$(python) src/rewriter.py $< > $@_
	mv $@_ $@


# Now use the rewritten source to generate trace
arg=
build/%_trace.py: build/%_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@

build/calc_trace.py: arg='(123+133+(12-3))+33'
build/calc_trace.py: build/calc_parser.py | build
	$(python) $< $(arg) > $@_
	mv $@_ $@


# Get the derivation tree out
build/%_tree.json: build/%_trace.py | build
	$(python) src/mine.py $<  > $@_
	mv $@_ $@

build/%_refine.json: build/%_tree.json | build
	$(python) src/refine.py $< > $@_
	mv $@_ $@


build: ; mkdir -p $@
