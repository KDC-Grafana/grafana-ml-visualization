import pandas as pd
from psycopg2 import errors
from psycopg2.sql import SQL, Identifier, Literal

from ...database.database_connection import DatabaseConnection


class TableLoader:
    
    def load_dataframe(self, source: str, target_column: str, limit: int = 45000) -> pd.DataFrame:
        """Carga hasta `limit` filas desde una tabla especificada con 'esquema.tabla'.
        Convierte columnas booleanas a 0/1 y mantiene solo columnas numéricas,
        excepto la variable objetivo (si se especifica), que puede ser categórica o numérica.
        """

        if '.' not in source or source.count('.') != 1:
            raise ValueError("Debe indicarse el nombre como 'esquema.tabla'")

        schema, table = source.split('.')

        query = SQL("SELECT * FROM {}.{} LIMIT {}").format(
            Identifier(schema),
            Identifier(table),
            Literal(limit)
        )

        try:
            db = DatabaseConnection()
            with db.connection.cursor() as cursor:
                cursor.execute(query)
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=columns)

                # Convertir booleanos a 0/1
                bool_cols = df.select_dtypes(include=['bool']).columns
                df[bool_cols] = df[bool_cols].astype(int)

                # Seleccionar columnas numéricas
                df_numeric = df.select_dtypes(include=['number'])

                # Si se indica variable objetivo y existe, se añade (aunque no sea numérica)
                if target_column:
                    if target_column not in df.columns:
                        raise ValueError(f"La columna objetivo '{target_column}' no existe en la tabla.")
                    if target_column not in df_numeric.columns:
                        df_numeric[target_column] = df[target_column]

                return df_numeric.dropna()

        except errors.UndefinedTable:
            raise RuntimeError(f"La tabla '{schema}.{table}' no existe.")
        except Exception as e:
            raise RuntimeError(f"No se pudo leer la tabla {schema}.{table}: {e}")