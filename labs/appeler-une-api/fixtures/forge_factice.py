#!/usr/bin/env python3
"""Une forge factice, pour essayer --publish sans vraie forge.

Elle répond comme l'API des tickets de Forgejo, sur une seule route :

    GET  /api/v1/repos/exploitation/certificats/issues   la liste des tickets ouverts
    POST /api/v1/repos/exploitation/certificats/issues   ouvre un ticket

Elle exige l'en-tête `Authorization: token jeton-de-demo` et répond 401 sans
lui. Avec --panne, elle répond 503 à tout. Chaque requête reçue est affichée
dans ce terminal : lancez-la dans un premier terminal, certcheck dans un
second.

    python3 forge_factice.py            # puis, dans un autre terminal :
    export FORGE_URL=http://127.0.0.1:8099 FORGE_TOKEN=jeton-de-demo
    export FORGE_REPO=exploitation/certificats
    CERTCHECK_NOW=2026-06-01 bin/certcheck --publish; echo "code : $?"
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

JETON = "jeton-de-demo"
ROUTE = "/api/v1/repos/exploitation/certificats/issues"
tickets: list[dict] = []


class Forge(BaseHTTPRequestHandler):
    panne = False

    def _repondre(self, code: int, corps: object) -> None:
        charge = json.dumps(corps, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(charge)))
        self.end_headers()
        self.wfile.write(charge)

    def _verifier(self) -> bool:
        auth = self.headers.get("Authorization", "")
        print(f"{self.command} {self.path}  (Authorization : {'présent' if auth else 'absent'},"
              f" User-Agent : {self.headers.get('User-Agent', '?')})", flush=True)
        if self.panne:
            self._repondre(503, {"message": "service indisponible"})
            return False
        if self.path.split("?")[0].rstrip("/") != ROUTE:
            self._repondre(404, {"message": f"route inconnue : {self.path}"})
            return False
        if auth not in (f"token {JETON}", f"Bearer {JETON}"):
            self._repondre(401, {"message": "jeton absent ou invalide"})
            return False
        return True

    def do_GET(self) -> None:
        if self._verifier():
            self._repondre(200, [t for t in tickets if t["state"] == "open"])

    def do_POST(self) -> None:
        longueur = int(self.headers.get("Content-Length") or 0)
        corps = json.loads(self.rfile.read(longueur) or b"{}")
        if self._verifier():
            ticket = {"number": len(tickets) + 1, "title": corps.get("title", ""),
                      "body": corps.get("body", ""), "state": "open"}
            tickets.append(ticket)
            print(f"  ticket n°{ticket['number']} ouvert : {ticket['title']}", flush=True)
            self._repondre(201, ticket)

    def log_message(self, *args: object) -> None:  # le print ci-dessus suffit
        return


def main() -> None:
    p = argparse.ArgumentParser(description="Forge factice pour le lab appeler-une-api.")
    p.add_argument("--port", type=int, default=8099)
    p.add_argument("--panne", action="store_true", help="répondre 503 à toutes les requêtes")
    args = p.parse_args()
    Forge.panne = args.panne
    print(f"forge factice sur http://127.0.0.1:{args.port} (Ctrl+C pour arrêter)", flush=True)
    HTTPServer(("127.0.0.1", args.port), Forge).serve_forever()


if __name__ == "__main__":
    main()
