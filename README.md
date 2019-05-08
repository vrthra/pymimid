# pymimid

Infering grammar

Loops: add an iteration index per loop, and update all if conditions and inner loops with it. At the end of derivation, during grammar inference, identify redundant non-terminals with same names, and having exactly same expansion.

Essentially, summarize loop items by deriving regular expressions (upto and not
including the method tokens). Then use this expression to identify redundant
non-terminals.

- Readable - Simplifying: Simply replace loops and ifs with regular expression
  -- specifically, do not use active learning. Remove generalize, and do the
  regex transformation after merging to grammar.


IMPORTANT: It fails to match up whiles from other inputs. So, all input files
need to be evaluated in the same execution, or dump the names used to a pickle
and reload at the start. This will likely cause exploding requests to
can_it_be_replaced. Use sampling if it happens. (Look for text sampling in generalize).

IMPORTANT: A single if condition should be an optional.  Currently, it is
ignored and inserted as is. Figure out why this happens.

IMPORTANT: Do the recursion merge on the whiles and others before converting
them to regex
