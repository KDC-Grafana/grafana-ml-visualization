import logging

from src.da.core.controller import Controller
from src.da.repositories.manager_repository import ManagerRepository


class DecisionTreeAlgorithm:
    def __init__(self):
        self.manager_repo = ManagerRepository()
        self.controlador = Controller()
        
    def execute(self, tarea):
        """Ejecuta el algoritmo de árbol de decisión"""
        try:
            # 1. Obtener datos del repositorio
            X, y, features, class_list = self.manager_repo.get_decision_tree_repository().get_data(tarea.id_source)
                
            # 2. Preparar caracteristicas y clases
            feature_names = [feature['name'] for feature in features]
            class_names = [cls['name'] for cls in class_list]
            
            # 3. Preparar los parámetros
            parameters = tarea.parameters
            max_depth = parameters.get("max_depth", None) 
            class_weight = parameters.get("class_weight", None) 

            ## Validar parámetros si no son "None"
            if max_depth is not None:
                if not isinstance(max_depth, int) or max_depth <= 0:
                    raise ValueError("'max_depth' debe ser un entero positivo")
            
            if class_weight is not None:
                if not (
                    class_weight == "balanced"
                    or isinstance(class_weight, dict)
                    or (isinstance(class_weight, list) and all(isinstance(d, dict) for d in class_weight))
                ):
                    raise ValueError(
                        "'class_weight' debe ser: 'balanced', un diccionario {clase: peso}, "
                        "o una lista de diccionarios para multi-output"
                    )

            # 4. Ejecutar entrenamiento y almacenamiento del arbol
            return self.controlador.train_and_store_tree(
                X=X, y=y, id_source=tarea.id_source,
                feature_names=feature_names, class_names=class_names,
                max_depth=max_depth, class_weight=class_weight,
                parameters=parameters
            )           
            
        except Exception as e:
            logging.error(f"Error en execute_algorithm_tree: {str(e)}")
            raise
    
    def delete(self, id_model: int):
        self.manager_repo.get_decision_tree_repository().delete_by_model(id_model)
        self.manager_repo.get_index_repository().delete(id_model)