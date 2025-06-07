-- Algoritmos 
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'algorithm') THEN
        CREATE TYPE algorithm AS ENUM (
            'a_kmedias',
            'a_kmedoides',
            'a_jerarquico',
            'c_pearson',
            'c_spearman',
            'r_lineal',
            'r_logistica',
            'arbol_decision',
            'reglas_asociacion'
        );
    END IF;
END $$;

-- Estados
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'state') THEN
        CREATE TYPE state AS ENUM (
            'listo',
            'pendiente',
            'en_ejecucion',
            'ejecucion_fallida',
            'eliminado'
        );
    END IF;
END $$;

-- Tabla principal para fuentes de modelos ML
CREATE TABLE IF NOT EXISTS grafana_ml_model_source (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source VARCHAR(255) NOT NULL,
    description TEXT,
    creator VARCHAR(255) 
);

-- Índice de modelos ML
CREATE TABLE IF NOT EXISTS grafana_ml_model_index (
    id SERIAL PRIMARY KEY,
    id_source INTEGER NOT NULL REFERENCES grafana_ml_model_source(id),
    algorithm algorithm NOT NULL,
    parameters TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Características de los modelos
CREATE TABLE IF NOT EXISTS grafana_ml_model_feature (
    id_source INTEGER NOT NULL REFERENCES grafana_ml_model_source(id),
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    is_target BOOLEAN NOT NULL
);

-- Puntos de datos para los modelos
CREATE TABLE IF NOT EXISTS grafana_ml_model_point (
    id_source INTEGER NOT NULL REFERENCES grafana_ml_model_source(id),
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Valores de los puntos de datos
CREATE TABLE IF NOT EXISTS grafana_ml_model_point_value (
    id_source INTEGER NOT NULL REFERENCES grafana_ml_model_source(id),
    id_point INTEGER NOT NULL REFERENCES grafana_ml_model_point(id),
    id_feature INTEGER NOT NULL REFERENCES grafana_ml_model_feature(id),
    numeric_value DOUBLE PRECISION,
    string_value VARCHAR(255),
    PRIMARY KEY (id_source, id_point, id_feature)
);

-- Valores de predicción para modelos de clasificación
CREATE TABLE IF NOT EXISTS grafana_ml_model_prediction_values (
    id_source INTEGER NOT NULL REFERENCES grafana_ml_model_source(id),
    id_prediction SERIAL PRIMARY KEY,
    class_name VARCHAR(255) NOT NULL
);

-- Clusters de modelos de clustering
CREATE TABLE IF NOT EXISTS grafana_ml_model_clustering_cluster (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id SERIAL PRIMARY KEY,
    number INTEGER NOT NULL,
    inertia DOUBLE PRECISION,
    silhouette_coefficient DOUBLE PRECISION
);

-- Centroides de clusters para K-Means
CREATE TABLE IF NOT EXISTS grafana_ml_model_kmeans_centroid (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id_cluster INTEGER NOT NULL,
    id_feature INTEGER NOT NULL REFERENCES grafana_ml_model_feature(id),
    value DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (id_model, id_cluster, id_feature)
);

-- Asignación de puntos a clusters en K-Means
CREATE TABLE IF NOT EXISTS grafana_ml_model_kmeans_point (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id SERIAL PRIMARY KEY,
    id_point INTEGER NOT NULL REFERENCES grafana_ml_model_point(id),
    id_cluster INTEGER NOT NULL REFERENCES grafana_ml_model_clustering_cluster(id)
);

-- Asignación de puntos a clusters en K-Medoids
CREATE TABLE IF NOT EXISTS grafana_ml_model_kmedoids_point (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id SERIAL PRIMARY KEY,
    id_point INTEGER NOT NULL REFERENCES grafana_ml_model_point(id),
    id_cluster INTEGER NOT NULL REFERENCES grafana_ml_model_clustering_cluster(id),
    is_medoid BOOLEAN NOT NULL
);

-- Métricas de clustering
CREATE TABLE IF NOT EXISTS grafana_ml_model_clustering_metrics (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id SERIAL PRIMARY KEY,
    inertia DOUBLE PRECISION,
    silhouette_coefficient DOUBLE PRECISION,
    davies_bouldin_index DOUBLE PRECISION
);

-- Modelos de clustering jerárquico
CREATE TABLE IF NOT EXISTS grafana_ml_model_clustering_hierarchical (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id SERIAL PRIMARY KEY,
    id_parent INTEGER REFERENCES grafana_ml_model_clustering_hierarchical(id),
    id_point INTEGER REFERENCES grafana_ml_model_point(id),
    name VARCHAR(255) NOT NULL,
    height DOUBLE PRECISION NOT NULL
);

-- Correlaciones entre características
CREATE TABLE IF NOT EXISTS grafana_ml_model_correlation (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id SERIAL PRIMARY KEY,
    id_feature1 INTEGER NOT NULL REFERENCES grafana_ml_model_feature(id),
    id_feature2 INTEGER NOT NULL REFERENCES grafana_ml_model_feature(id),
    value DOUBLE PRECISION NOT NULL
);

-- Modelos de regresión
CREATE TABLE IF NOT EXISTS grafana_ml_model_regression (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id SERIAL PRIMARY KEY,
    id_feature INTEGER REFERENCES grafana_ml_model_feature(id),
    coeff DOUBLE PRECISION NOT NULL,
    std_err DOUBLE PRECISION NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    p_value DOUBLE PRECISION NOT NULL
);

-- Modelos de árboles de decisión
CREATE TABLE IF NOT EXISTS grafana_ml_model_decision_tree (
    id_model INTEGER REFERENCES grafana_ml_model_index(id),
    id_node SERIAL PRIMARY KEY,
    parent_node INTEGER REFERENCES grafana_ml_model_decision_tree(id_node),
    feature INTEGER REFERENCES grafana_ml_model_feature(id),
    threshold DOUBLE PRECISION,
    left_node INTEGER REFERENCES grafana_ml_model_decision_tree(id_node),
    right_node INTEGER REFERENCES grafana_ml_model_decision_tree(id_node),
    is_leaf BOOLEAN NOT NULL,
    prediction_value INTEGER REFERENCES grafana_ml_model_prediction_values(id_prediction)
);

-- Reglas de asociación
CREATE TABLE IF NOT EXISTS grafana_ml_model_association_rules (
    id_model INTEGER NOT NULL REFERENCES grafana_ml_model_index(id),
    id SERIAL PRIMARY KEY,
    antecedent VARCHAR(255) NOT NULL,
    consequent VARCHAR(255) NOT NULL,
    support DOUBLE PRECISION NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    lift DOUBLE PRECISION NOT NULL
);

-- Tareas de creación de modelos
CREATE TABLE IF NOT EXISTS grafana_ml_model_task_create (
    id SERIAL PRIMARY KEY,
    id_source INTEGER NOT NULL,
    algorithm algorithm NOT NULL,
    parameters JSON DEFAULT '{}',
    state state NOT NULL DEFAULT 'pendiente',
    id_model INTEGER
);

-- Trigger para prevenir inserción manual de id_model
CREATE OR REPLACE FUNCTION prevent_insert_id_model()
RETURNS trigger AS $$
BEGIN
    IF NEW.id_model IS NOT NULL THEN
        RAISE EXCEPTION 'El campo id_model no puede establecerse manualmente al insertar. Será asignado automáticamente.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_insert_id_model ON grafana_ml_model_task_create;

CREATE TRIGGER trg_prevent_insert_id_model
BEFORE INSERT ON grafana_ml_model_task_create
FOR EACH ROW
EXECUTE FUNCTION prevent_insert_id_model();

-- Tareas de creación de fuentes
CREATE TABLE IF NOT EXISTS grafana_ml_model_source_create (
    id SERIAL PRIMARY KEY,
    description TEXT,
    name VARCHAR(255) NOT NULL,
    creator VARCHAR(255),
    source VARCHAR(255) NOT NULL,
    target VARCHAR(255),
    state state NOT NULL DEFAULT 'pendiente',
    id_source INTEGER
);

-- Trigger para prevenir inserción manual de id_source
CREATE OR REPLACE FUNCTION prevent_insert_id_source()
RETURNS trigger AS $$
BEGIN
    IF NEW.id_source IS NOT NULL THEN
        RAISE EXCEPTION 'El campo id_source no puede establecerse manualmente al insertar. Será asignado automáticamente.';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_prevent_insert_id_source ON grafana_ml_model_source_create;

CREATE TRIGGER trg_prevent_insert_id_source
BEFORE INSERT ON grafana_ml_model_source_create
FOR EACH ROW
EXECUTE FUNCTION prevent_insert_id_source();

-- Tareas de eliminación de modelos
CREATE TABLE IF NOT EXISTS grafana_ml_model_task_delete (
    id SERIAL PRIMARY KEY,
    id_model INTEGER NOT NULL,
    state state NOT NULL DEFAULT 'pendiente',
    date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Tareas de eliminación de fuentes
CREATE TABLE IF NOT EXISTS grafana_ml_model_source_delete (
    id SERIAL PRIMARY KEY,
    id_source INTEGER NOT NULL,
    state state NOT NULL DEFAULT 'pendiente',
    date DATE NOT NULL DEFAULT CURRENT_DATE
);
