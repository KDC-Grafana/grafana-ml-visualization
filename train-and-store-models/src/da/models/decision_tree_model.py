from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier


class DecisionTreeModel:
    def __init__(self):
        self.modelo = None
        self.feature_names = []  # Atributo para almacenar los nombres de las características
        self.class_names = []    # Atributo para almacenar los nombres de las clases
        self.precision = None    # Atributo para almacenar la precisión del modelo

    def train(self, X, y, feature_names, max_depth=None, class_weight=None):
        """
        Entrena el modelo de árbol de decisión y aplica filtros opcionales.
    
        Parámetros:
           X (DataFrame): Conjunto de características.
           y (Series): Variable objetivo.
           feature_names (list): Lista de nombres de características.
           max_depth (int, opcional): Profundidad máxima del árbol.
           class_weight (dict or str, opcional): Pesos de clases, ej. 'balanced'.
        """
        
        # Inicializar el clasificador de árbol de decisión
        self.modelo = DecisionTreeClassifier(max_depth=max_depth, class_weight=class_weight)

        # Entrenar el modelo con los datos de entrada
        self.modelo.fit(X, y)

        # Almacenar los nombres de las características y las clases
        self.feature_names = feature_names  # Ahora almacenamos los nombres pasados como argumento
        self.class_names = [str(cls) for cls in set(y)]  # Convertir las clases a string

        # Calcular precisión en los datos de entrenamiento
        y_pred = self.modelo.predict(X)
        self.precision = accuracy_score(y, y_pred)

    def get_nodes(self):
        """Obtener la estructura del árbol (nodos, umbrales, etc.)."""
        if self.modelo:
            return self.modelo.tree_.__getstate__()['nodes'], self.modelo.tree_.value
        else:
            raise Exception("El modelo no está entrenado")

    def get_precision(self):
        """Devuelve la precisión calculada del modelo."""
        if self.precision is not None:
            return self.precision
        else:
            raise Exception("El modelo no ha sido entrenado, no se puede calcular precisión.")