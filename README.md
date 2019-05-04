# pymimid

Infering grammar

Loops: add an iteration index per loop, and update all if conditions and inner loops with it. At the end of derivation, during grammar inference, identify redundant non-terminals with same names, and having exactly same expansion.

Essentially, summarize loop items by deriving regular expressions (upto and not
including the method tokens). Then use this expression to identify redundant
non-terminals.

- Readable - Simplifying: Simply replace loops and ifs with regular expression
- Todo: Check if for loops need to be scoped
