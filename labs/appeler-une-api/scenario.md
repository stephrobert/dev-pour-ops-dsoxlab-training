# A publication that holds up

## Situation

certcheck honours its contract, except on one point: publishing to the
forge. A colleague wrote it on a Friday, tried it once on a test forge and
shipped it. Read the `requete()` function and the end of `publier()` in
`certcheck.py`: the token is glued to the URL (`?access_token=`), `urlopen`
is called without a timeout, the first 503 error aborts, and every run opens
a new ticket.

Run every night by cron, this tool would open one ticket per night, write
the token to the logs on every error, and hang forever the day the forge
stops answering.

## Goal

`bin/certcheck --publish` honours the "Publication sur la forge" section of
`CONTRAT.md`:

- the token travels in the `Authorization: token <token>` header, never in
  a URL nor on an output;
- before opening, the tool looks for an open ticket whose title is
  **exactly** `certcheck : certificats à renouveler`, across **every** page
  of the list;
- a 429 or 5xx response is retried, three attempts in total, with a pause
  in between, before giving up with code 3;
- every request has a timeout: a forge that does not answer makes the tool
  exit with code 3, instead of waiting forever.

The rest of the tool (reading, decision, outputs, codes) already complies:
leave it alone.

## Hints

- `urllib.request.Request(url, headers={"Authorization": f"token {token}"})`
  puts the token in the header; `urlopen(request, timeout=5)` bounds the
  wait for the connection and for each read.
- `urllib.error.HTTPError` carries the HTTP code in `exc.code`; an expired
  timeout raises `TimeoutError` (or `URLError` while connecting).
- The ticket list: `GET /api/v1/repos/{repo}/issues?state=open&type=issues&limit=50&page=N`.
  The forge returns 30 tickets per page by default and 50 at most; an
  incomplete (or empty) page is the last one. The `Link: rel="next"` header
  also gives the next page.
- `--verbose` writes the log to standard error: make sure it never contains
  the token.
