"""Les deux erreurs que l'interface traduit en codes de sortie."""


class ErreurUsage(Exception):
    """Entrée ou configuration inexploitable : code de sortie 2."""


class ErreurPublication(Exception):
    """La forge a refusé ou n'a pas répondu : code de sortie 3."""
