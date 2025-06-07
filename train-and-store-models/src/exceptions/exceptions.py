class NotEnoughVariablesException(Exception):
    """Excepción para cuando no hay suficientes variables para ejecutar el algoritmo."""
    pass

class NoTargetException(Exception):
    """Excepción cuando no se encuentra una variable objetivo (target)."""
    pass

class SourceNotFoundException(Exception):
    """Excepción cuando no se encuentra la fuente de datos."""
    pass

