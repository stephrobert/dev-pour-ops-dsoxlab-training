# The takeover

## Situation

Julien, who wrote `certcheck.sh`, has left the team, and you are taking the
tool over. The script runs every night from the operations server's cron. It
always exits 0, and for weeks it counted a certificate that could not be
found as expiring "in 0 days": nobody noticed. The team wrote down what it
expects from the tool in `CONTRAT.md`.

On the same day, Inès asks you to review her pull request #57 on the Python
variant the team had been maintaining on the side: her tests pass, and she
would like to merge it before the move to the internal forge.

## Goal

Deliver a tool anyone on the team can take over after you: compliant with
the contract, covered by a test suite that does not depend on its
implementation, published under a tagged version that installs in one
command, and accompanied by your review of PR #57. The language is yours,
and you explain why in `CHOIX.md`.

There is no lesson and no hint in this exam: it measures what you already
know how to do. The mission is in `dsoxlab challenge`.
