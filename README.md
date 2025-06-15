# 📊 Visualización de modelos de aprendizaje automático en Grafana

## 💡 Descripción de la solución
Este proyecto tiene como objetivo visualizar modelos de aprendizaje automático en Grafana, aprovechando el poder de extensiones como **Business Charts** para crear paneles interactivos. Se han desarrollado visualizaciones para representar los siguientes tipos de modelos:

- Agrupamiento K-medias - K-medoides
- Agrupamiento jerárquico
- Regresión lineal
- Regresión logística
- Correlación Pearson - Spearman
- Árboles de decisión
- Reglas de asociación

Los modelos son entrenados en Python, se almacenan en una base de datos relacional PostgreSQL, y luego son obtenidos desde Grafana mediante consultas SQL para su visualización. La interacción con el usuario se realiza mediante un sistema de gestión de tareas, que permite crear y eliminar modelos, así como administrar las fuentes de datos utilizadas para el entrenamiento.

## 🛠️ Tecnologías utilizadas
- **Python**: para la ejecución de los algoritmos y el procesamiento.
- **PostgreSQL**: para almacenar fuentes de datos y modelos.
- **Grafana + Business Charts + Business Text**: para visualizar los modelos.

## 📦 Instalación
```bash
git clone https://github.com/KDC-Grafana/grafana-ml-visualization.git
cd grafana-ml-visualization
python -m venv venv
source venv/bin/activate  # o .\venv\Scripts\activate en Windows
pip install -r requirements.txt
```

## ⚙️ Configuración 
El archivo `conf.ini` se encuentra en la carpeta `config/` y contiene los parámetros necesarios para conectar con la base de datos y controlar algunas funcionalidades del sistema.

### Estructura del archivo
```ini
[database]
dbname = grafana_ml_models       # Nombre de la base de datos en PostgreSQL
user = postgres                  # Usuario con permisos para acceder a la base de datos
password = postgres              # Contraseña del usuario especificado
host = localhost                 # Dirección del servidor de base de datos (localhost si es local)
port = 5432                      # Puerto de conexión de PostgreSQL (5432 por defecto)

[scheduler]
interval_minutes = 1            # Intervalo en minutos para revisar y ejecutar tareas pendientes

[features]
task_notifications = true       # Habilita notificaciones para cada tarea
general_notifications = false   # Habilita notificaciones generales por ejecución
generate_summary = true         # Habilita la creación de un resumen por ejecución con IDs y posibles errores detectados
```

## ▶️ Ejecución

### Linux
**Comandos disponibles:**
```bash
python main_linux.py create
```
Programa la ejecución automática del sistema cada N minutos (según el valor en `config/conf.ini` > `[scheduler] interval_minutes`).
```bash
python main_linux.py delete
```
Elimina la programación automática.

📌 Una vez creado, el cron ejecuta el programa de forma recurrente, incluso si la computadora se reinicia.

### Windows
Primeramente, se debe ejecutar el archivo `main_windows.py`.

Al hacerlo, se mostrará una ventana emergente con el mensaje:
> ¿Desea ejecutar el servicio GrafanaML?

- ✅ Si haces clic en **"Sí"**, el servicio se inicia y comienza a procesar tareas automáticamente.
- ❌ Si haces clic en **"No"**, el programa se cierra sin ejecutar ningún proceso.

📌 Una vez iniciado el servicio por primera vez, desde el entorno no será necesario volver a entrar al IDE. Cada vez que se inicie el sistema operativo aparecerá la ventana emergente con el mensaje.

Para detener el programa, presionar la combinación:
```
Ctrl + Shift + Q
```
Al hacerlo, el sistema mostrará una ventana emergente:
> ¿Desea detener el servicio GrafanaML?

- ✅ Si haces clic en **"Sí"**, el servicio se detiene de forma segura y se cierra completamente.
- ❌ Si haces clic en **"No"**, el servicio continuará ejecutándose.