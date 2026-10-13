# Challenge: certcheck opens its ticket with requests

5 tasks, 100 points, 30 minutes. Network access needed once (PyPI).

Each check runs `bin/certcheck --publish` against a fake forge and looks at
the requests it receives.

### Task 1: requests declared, token in the header (20 pts)

`pyproject.toml` declares `requests` at an exact version (`==`), and it is
the one calling the forge (User-Agent `python-requests/<that version>`).
Every request carries `Authorization: token <token>`; the token appears
neither in a URL nor on any output, even with `--verbose`.

### Task 2: a timeout (20 pts)

A forge that accepts the connection and never answers: the tool gives back
control on its own, with code 3 and a message on standard error.

### Task 3: an HTTP error gives code 3 (20 pts)

A rejected token (401) or a forge that is down (503): code 3, and a message
on standard error naming the HTTP code, without the token.

### Task 4: the ticket is created with the right title (20 pts)

Certificates are due: a single ticket is created, with the exact title
`certcheck : certificats à renouveler`, whose body names every host, and the
exit code stays the one of the check.

### Task 5: no duplicate (20 pts)

An open ticket already carries that title, on the first page of the list:
the tool reads the list, creates nothing, and keeps the check's exit code.
