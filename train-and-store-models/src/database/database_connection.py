import configparser
import logging
import os
from pathlib import Path

from psycopg2 import OperationalError, connect

logging.basicConfig(level=logging.INFO)

class DatabaseConnection:
    _instance = None
    _config_file = Path(__file__).resolve().parents[2] / "config" / "config.ini"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._config = self._load_config()
        self._connection = None
        self._initialize_database()

    @property
    def connection(self):
        if self._connection is None or self._connection.closed:
            self._connect()
        return self._connection


    def _load_config(self):
        config_path = self._config_file
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {self._config_file}")
        
        parser = configparser.ConfigParser()
        parser.read(config_path)

        if 'database' not in parser:
            raise ValueError("La sección [database] falta en el archivo de configuración")

        db_config = parser['database']
        required_keys = {'dbname', 'user', 'password', 'host'}

        if missing := required_keys - db_config.keys():
            raise ValueError(f"Faltan parámetros en la configuración: {missing}")

        config = {
            'dbname': db_config['dbname'],
            'user': db_config['user'],
            'password': db_config['password'],
            'host': db_config['host'],
            'port': db_config.getint('port', 5432),
        }

        return config

    def _connect(self):
        try:
            self._connection = connect(**self._config)
            logging.info("Conexión a la base de datos establecida")
        except OperationalError as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
            raise

    def _initialize_database(self):
        """Ejecuta el script SQL para crear las tablas si no existen"""
        schema_path = Path(__file__).parent / "init_database.sql"
        cursor = None

        try:
            # Verificamos si las tablas ya existen
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            existing_tables = {row[0] for row in cursor.fetchall()}

            # Lista de tablas 
            required_tables = ["grafana_ml_model_source", "grafana_ml_model_index", "grafana_ml_model_feature", "grafana_ml_model_point", "grafana_ml_model_point_value",
                                "grafana_ml_model_prediction_values", "grafana_ml_model_clustering_cluster", "grafana_ml_model_kmeans_centroid", "grafana_ml_model_kmeans_point",
                                "grafana_ml_model_kmedoids_point", "grafana_ml_model_clustering_metrics", "grafana_ml_model_clustering_hierarchical", "grafana_ml_model_correlation",
                                "grafana_ml_model_regression", "grafana_ml_model_decision_tree", "grafana_ml_model_association_rules", "grafana_ml_model_task_create",
                                "grafana_ml_model_source_create", "grafana_ml_model_task_delete", "grafana_ml_model_source_delete"]  

            # Si alguna de las tablas no existen, ejecutar el script
            if not all(table in existing_tables for table in required_tables):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    sql_script = f.read()

                cursor.execute(sql_script)
                self.connection.commit()

        except FileNotFoundError as e:
            raise FileNotFoundError(f"No se encontró el archivo schema.sql: {schema_path}") from e
        except Exception as e:
            self.connection.rollback()
            raise RuntimeError(f"Error al inicializar la base de datos: {str(e)}") from e
        finally:
            if cursor is not None:
                cursor.close()
    
    def close(self):
        if self._connection and not self._connection.closed:
            self._connection.close()
            logging.info("Conexión cerrada correctamente")
        self._connection = None
        self.__class__._instance = None