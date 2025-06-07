from typing import Dict

import numpy as np
import pandas as pd

from src.da.entities.association_rule_entity import AssociationRule
from src.da.entities.decision_tree_entity import DecisionTreeNode
from src.da.entities.index_entity import Index
from src.da.models.association_rules_model import AssociationRulesModel
from src.da.models.decision_tree_model import DecisionTreeModel
from src.da.repositories.manager_repository import ManagerRepository


class Controller:
    def __init__(self):
        self.manager_repo = ManagerRepository()
        self.modelo_arbol = DecisionTreeModel()
        self.modelo_reglas = AssociationRulesModel()

    def get_parent_id(self, nodo_id, nodos):
        """Determina el ID del nodo padre de un nodo dado."""
        for i, nodo in enumerate(nodos):
            if nodo['left_child'] == nodo_id or nodo['right_child'] == nodo_id:
                return i  # Devuelve el índice del nodo actual como el padre
        return None  # Devuelve None si no tiene padre (caso raíz)
    
    def save_model_tree(self, id_source: int, parameters: Dict) -> int:
        """Guardar el modelo en ModelIndex"""
        model_tree = self.manager_repo.get_index_repository().create(Index(id_source=id_source, algorithm="arbol_decision", parameters=parameters))
        return model_tree.id

    def train_and_store_tree(self, X, y, id_source, feature_names, class_names, max_depth=None, class_weight=None, parameters=None):
        """Entrenar el modelo de árbol de decisión."""
        # ===== Validación de X =====
        # Convertir X a DataFrame si es un numpy array
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X, columns=feature_names)

        # Verificar si hay columnas categóricas (tipo 'object')
        categorical_cols = X.select_dtypes(include=['object']).columns
        if not categorical_cols.empty:
            raise ValueError(
                f"El modelo no soporta características categóricas directamente. "
                f"Columnas categóricas detectadas: {list(categorical_cols)}. "
                f"Por favor, aplique OneHotEncoder o OrdinalEncoder manualmente."
            )

        # ===== Validación de y =====
        # Convertir y a Series si es numpy array
        if isinstance(y, np.ndarray):
            y = pd.Series(y)
    
        # Caso 1: y es string (categórico)
        if pd.api.types.is_string_dtype(y) or pd.api.types.is_object_dtype(y):
            unique_classes = y.unique()
            # Solo verifica que haya al menos una clase
            if len(unique_classes) < 1:
                raise ValueError(
                    f"El target categórico no contiene clases válidas."
                    f"Valores encontrados: {y.unique()}"
                )
    
        # Caso 2: y es numérico binario 
        elif pd.api.types.is_numeric_dtype(y):
            unique_values = set(y.unique())
            valid_binary = {0, 1}
        
            if not unique_values.issubset(valid_binary):
                raise ValueError(
                    f"El target numérico debe ser binario (0 y 1)."
                    f"Valores encontrados: {unique_values}"
                )
    
        # Caso 3: Tipo no soportado
        else:
            raise ValueError(
                f"Tipo de target no soportado."
                f"Se esperaba string o numérico binario. Tipo recibido: {type(y)}"
            )

        # Entrenar el modelo de árbol de decisión
        self.modelo_arbol.train(X, y, feature_names, max_depth=max_depth, class_weight=class_weight)
        nodos, valores = self.modelo_arbol.get_nodes()

        # Mostrar precisión después de entrenar
        precision = self.modelo_arbol.get_precision()
        print(f"Precisión del modelo de árbol de decisión: {precision:.2f}")

        # Mapear características y valores de predicción a sus IDs en la base de datos
        caracteristica_ids = {nombre: self.manager_repo.get_decision_tree_repository().get_feature_id(id_source, nombre) for nombre in feature_names}
        prediccion_ids = {clase: self.manager_repo.get_decision_tree_repository().get_prediction_value_id(id_source, clase) for clase in class_names}

        # Primera etapa: Inserción inicial de nodos
        nodo_id_map = {}
        # Insertar cada nodo del árbol de decisión
        for nodo_id, nodo in enumerate(nodos):
           # Obtener el índice de la característica si es un nodo de decisión
           caracteristica_index = nodo['feature']

           # Asegurarse de que el índice está dentro de los límites
           caracteristica = feature_names[caracteristica_index] if 0 <= caracteristica_index < len(feature_names) else None
           caracteristica_id = caracteristica_ids.get(caracteristica) if caracteristica else None

           # Establecer umbral
           umbral = nodo['threshold'] if caracteristica_id is not None else None
           es_hoja = nodo['left_child'] == -1 and nodo['right_child'] == -1

           # Obtener el ID del valor de predicción si es hoja
           valor_prediccion_id = None
           if es_hoja:
               valor_prediccion = class_names[valores[nodo_id].argmax()]
               valor_prediccion_id = prediccion_ids.get(valor_prediccion)
        
           # Insertar el nodo en la tabla arbol_decision con IDs de características y predicción
           nodo_db_id = self.manager_repo.get_decision_tree_repository().create(DecisionTreeNode(id_model= None, parent_node= None, feature= caracteristica_id, 
                                                                                                 threshold= umbral, left_node= None, right_node= None,
                                                                                                 is_leaf= es_hoja, prediction_value= valor_prediccion_id))     
           nodo_id_map[nodo_id] = nodo_db_id

        # Segunda etapa: Actualización de relaciones padre-hijo
        for nodo_id, nodo in enumerate(nodos):
           # Obtener el ID del nodo padre
           nodo_padre_id = nodo_id_map.get(self.get_parent_id(nodo_id, nodos))
           # Actualizar los indices de los nodos izquierdo y derecho
           nodo_izquierdo_id = nodo_id_map.get(nodo['left_child']) if nodo['left_child'] != -1 else None
           nodo_derecho_id = nodo_id_map.get(nodo['right_child']) if nodo['right_child'] != -1 else None

           self.manager_repo.get_decision_tree_repository().update_node_relations(
               nodo_id_map[nodo_id], nodo_padre_id, nodo_izquierdo_id, nodo_derecho_id
            )
        
        # Tercera etapa: Crear el modelo en Index
        modelo_id = self.save_model_tree(id_source, parameters)

        # Cuarta etapa: Actualizar los nodos para asignarles modelo_id 
        for nodo_db_id in nodo_id_map.values():
            self.manager_repo.get_decision_tree_repository().update_id_model(nodo_db_id, modelo_id)

        return modelo_id

    
    def save_model_rule(self, id_source: int, parameters: Dict) -> int:
        """Guardar el modelo en ModelIndex"""
        model_rule = self.manager_repo.get_index_repository().create(Index(id_source=id_source, algorithm="reglas_asociacion", parameters=parameters))
        return model_rule.id

    def train_and_store_rules(self, id_source, datos, min_support= None, min_confidence= None, parameters=None):
        """Entrenar y almacenar solo el modelo de reglas de asociación."""
        datos_bool = datos.astype(bool)
        self.modelo_reglas.train(datos_bool, min_support=min_support, min_confidence=min_confidence)
        reglas = self.modelo_reglas.get_rules()

        # Guardar modelo y obtener modelo_id 
        modelo_id = self.save_model_rule(id_source=id_source, parameters=parameters)

        # Insertar reglas en la base de datos
        for _, regla in reglas.iterrows():
            antecedente = ', '.join(list(regla['antecedents']))
            consecuente = ', '.join(list(regla['consequents']))
            soporte = regla['support']
            confianza = regla['confidence']
            lift = regla['lift']

            # Insertar en la tabla
            self.manager_repo.get_association_rule_repository().create(AssociationRule(id_model = modelo_id, antecedent = antecedente, consequent = consecuente,
                                                                                           support = soporte, confidence = confianza, lift = lift))
        
        # Mostrar confianza promedio después de entrenar
        average_confidence = self.modelo_reglas.get_average_confidence()
        print(f"Confianza promedio del modelo de reglas de asociación: {average_confidence:.2f}")

        return modelo_id