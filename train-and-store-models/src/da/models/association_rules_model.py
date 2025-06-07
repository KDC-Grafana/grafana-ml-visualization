from mlxtend.frequent_patterns import apriori, association_rules


class AssociationRulesModel:
    def __init__(self):
        self.reglas = None
        self.average_confidence = None

    def train(self, datos, min_support= None, min_confidence= None):
        """
        Entrena el modelo de reglas de asociación y aplica filtros opcionales.
    
        Parámetros:
           datos (DataFrame): Datos transaccionales.
           min_support (float): Soporte mínimo para el algoritmo Apriori.
           min_confidence (float): Confianza mínima para generar reglas.
           filtro_support (float, opcional): Valor mínimo de soporte para filtrar reglas.
           filtro_lift (float, opcional): Valor mínimo de lift para filtrar reglas.
        """

        # Generar los ítems frecuentes
        itemsets_frecuentes = apriori(datos, min_support=min_support, use_colnames=True)

        # Generar las reglas usando la confianza como métrica principal
        reglas = association_rules(itemsets_frecuentes, metric="confidence", min_threshold=min_confidence)

        # Verificar que las reglas cumplen el filtro de confianza
        reglas = reglas[reglas['confidence'] >= min_confidence]

        # Almacenar las reglas finales
        self.reglas = reglas

        # Calcular el promedio de la confianza del conjunto de reglas
        self.average_confidence = self.reglas['confidence'].mean() if not self.reglas.empty else 0.0

    def get_rules(self):
        """Obtener reglas con soporte, confianza y lift."""
        if self.reglas is not None:
            return self.reglas[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
        else:
            raise Exception("El modelo no está entrenado")
        
    def get_average_confidence(self):
        """Obtener el promedio de confianza de las reglas generadas."""
        if self.average_confidence is not None:
            return self.average_confidence
        else:
            raise Exception("El modelo no está entrenado o no tiene reglas generadas.")