# Challenge: certcheck publishes its ticket without fragility

5 tasks, 100 points, 45 minutes.

Every check runs `bin/certcheck --publish` against a fake forge and counts
the requests it receives. The contract is in `CONTRAT.md`, section
"Publication sur la forge".

### Task 1: the token stays in the header (20 pts)

Every request carries `Authorization: token <token>`; the token appears in
no URL, neither on standard output nor on standard error, even with
`--verbose` and even when the forge is down.

### Task 2: one ticket across two runs (20 pts)

Two runs in a row open a single ticket, with the exact title
`certcheck : certificats à renouveler`, whose body names every host to
renew. A ticket that merely quotes that title does not count.

### Task 3: the search goes through every page (20 pts)

With more than a hundred open tickets and certcheck's one beyond the first
page, the tool finds it and opens nothing.

### Task 4: transient failures are retried (20 pts)

Two 503 responses, then a healthy forge: the tool succeeds, one ticket, the
check's exit code. A forge that stays down: code 3, a message on standard
error, and a handful of requests, not a flood.

### Task 5: a timeout on every request (20 pts)

A forge that accepts the connection and never answers: the tool gives control
back on its own in less than 60 seconds, with code 3 and a message.
