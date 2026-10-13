"""certcheck : signale les certificats TLS d'un parc qui arrivent à expiration."""

from importlib.metadata import version

# Une seule source pour la version : pyproject.toml. Le paquet installé la
# porte dans ses métadonnées, et l'outil la lit là, jamais en dur ici.
__version__ = version("certcheck")
