# The takeover

## Situation

Julien, who wrote `certcheck.sh`, has left the team, and you are taking the
tool over. The script runs every night from the operations server's cron. It
always exits 0, and for weeks it counted a certificate that could not be
found as expiring "in 0 days": nobody noticed. The team wrote down what it
expects from the tool in `CONTRAT.md`, and decided to replace it with a
Python project.

On the same day, Inès asks you to review her pull request #57 on the Python
variant the team had been maintaining on the side: her tests pass, and she
would like to merge it before the move to the internal forge.

## Goal

Deliver a tool anyone on the team can take over after you: a Python project
compliant with the contract, covered by pytest tests that catch the
inherited bug, installable in one command, shipped under a version recorded
in the CHANGELOG and tagged in Git, and accompanied by your review of PR
#57.

There is no lesson and no hint in this exam: it measures what you already
know how to do. The mission is in `dsoxlab challenge`.
