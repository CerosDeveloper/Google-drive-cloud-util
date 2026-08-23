# Google Drive Backup Utility

Aplicación de escritorio hecha en **Python + PySide6 (Qt)** para respaldar carpetas locales a Google Drive de forma automática, con interfaz gráfica, subida/descarga en paralelo, y limpieza automática de archivos y carpetas eliminados.

---

## Características

- **Interfaz gráfica de escritorio** hecha con PySide6/Qt Designer, sin necesidad de usar la línea de comandos.
- **Selección de carpetas a respaldar y carpetas a excluir**, gestionadas desde la interfaz y guardadas en `backup_info.json`.
- **Subida incremental**: solo sube archivos nuevos o modificados desde el último backup (comparando fechas de modificación), en vez de resubir todo cada vez.
- **Detección y borrado de archivos eliminados**: si borraste un archivo localmente, la próxima vez que corras el backup se elimina también de Google Drive.
- **Limpieza automática de carpetas vacías** en Drive tras un borrado, sin recorrer todo el árbol de carpetas (solo revisa las carpetas afectadas).
- **Subida y descarga en paralelo** usando múltiples hilos, pensado para trabajar con backups de decenas de miles de archivos sin que la operación tome horas.
- **Descarga completa del backup** desde Google Drive hacia una carpeta local, con indexado del árbol de carpetas también en paralelo.
- **Eliminación completa del backup en la nube**, con diálogo de confirmación para evitar borrados accidentales.
- **Progreso visual en tiempo real**: ventana emergente con barra de carga y el detalle de la carpeta/archivo que se está procesando en cada momento.
- **Renovación automática de sesión**: si el token de Google expira o es revocado, la app vuelve a pedir el login.
- **Portable y propio**: la app compilada (`.exe`) no trae credenciales propias; cada usuario conecta su propia cuenta de Google Drive.

---

## Sobre el uso de IA en este proyecto

Este proyecto fue desarrollado con la asistencia de modelos de lenguaje de IA como herramienta de apoyo durante el desarrollo, concretamente **Claude (Anthropic)** y **ChatGPT (OpenAI)**. usados para:

- Depurar problemas específicos de layouts y comportamiento de Qt/PySide6.
- Resolver manejo de errores de autenticación con la API de Google.
- Optimizar el rendimiento de las operaciones de subida/descarga (paralelismo con hilos).
- Redactar y estructurar este mismo README.

La arquitectura general, las decisiones de diseño y el código base del proyecto son de mi autoría; la IA se usó como herramienta de consulta y depuración puntual, no para generar el proyecto de punta a punta sin supervisión. Se documenta esto por transparencia.

---

## ¿Ya existe algo así?

Antes de este proyecto busqué si había herramientas similares, hay varias alternativas ya existentes, cada una con un enfoque distinto:

- **[dunkmann00/Drive-Backup](https://github.com/dunkmann00/Drive-Backup)** — probablemente la más similar: respalda Google Drive localmente, con binarios precompilados y opción de usar credenciales propias (pero todo desde el cmd).
- **[Teidesat/GDrive-Backup](https://github.com/Teidesat/GDrive-Backup)** — mantiene una copia local de Drive con historial de revisiones para archivos modificados/eliminados.
- **[saurabh9651/sync_with_google_drive_api](https://github.com/saurabh9651/sync_with_google_drive_api)** — script simple para subir una carpeta local a una carpeta específica de Drive.
- **[vikynandha-zz/google-drive-backup](https://github.com/vikynandha-zz/google-drive-backup)** — script de sincronización con opciones de línea de comandos.
- **[bachvtuan/Backup-To-Google-Drive](https://github.com/bachvtuan/Backup-To-Google-Drive)** — enfocado en backups automatizados de bases de datos vía cron/crontab.

Ninguna de estas es una copia 1:1 de este proyecto (la combinación de GUI en Qt, selección visual de carpetas incluidas/excluidas, paralelismo pensado para decenas de miles de archivos, y limpieza dirigida de carpetas vacías no la vi replicada exactamente en ninguna), pero vale la pena revisarlas si buscas alternativas ya maduras o con más tiempo de desarrollo encima.

---

## Cómo usar la aplicación (usuarios)

### 1. Crear un proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/).
2. Inicia sesión con la cuenta de Google que quieras usar para el backup.
3. En la parte superior, haz clic en el selector de proyectos → **Nuevo Proyecto**.
4. Dale un nombre (por ejemplo, `Drive Backup Utility`) y créalo.

### 2. Habilitar la API de Google Drive

1. Con el proyecto recién creado seleccionado, ve directamente a: [Habilitar Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com).
2. Haz clic en **Habilitar** (Enable).

### 3. Configurar la pantalla de consentimiento OAuth

1. Ve a **Menú ☰ → Google Auth Platform → Overview** (o [ve directo aquí](https://console.cloud.google.com/auth/overview)).
2. Si aparece el mensaje de que la plataforma no está configurada, haz clic en **Comenzar / Get Started**.
3. En **App Information**, ingresa un nombre para la app (por ejemplo, `Drive Backup Utility`) y un correo de soporte.
4. Avanza y, en **Audience**, selecciona **External** (a menos que uses una cuenta de Google Workspace/organización).
5. Completa el correo de contacto y acepta la política de datos (**Google API Services User Data Policy**).
6. Haz clic en **Crear/Create**. No es necesario agregar scopes manualmente en este paso.

> **Nota:** como la app queda en modo de prueba ("Testing"), Google puede advertirte que la app "no está verificada" al iniciar sesión. Esto es normal para uso personal — haz clic en **Avanzado → Ir a [nombre de tu app] (no seguro)** para continuar. Es tu propio proyecto, con tus propias credenciales, así que es seguro.

### 4. Crear las credenciales (OAuth Client ID)

1. Ve a **Menú ☰ → Google Auth Platform → Clients** (o [ve directo aquí](https://console.cloud.google.com/auth/clients)).
2. Haz clic en **Crear Cliente / Create Client**.
3. En **Application type**, elige **Desktop app**.
4. Dale un nombre (el que quieras, solo es para identificarlo en la consola).
5. Haz clic en **Crear/Create**.
6. Descarga el archivo JSON generado (botón de descarga junto al cliente recién creado).

### 5. Colocar las credenciales junto al ejecutable

1. Renombra el archivo descargado a **`credentials.json`** exactamente (todo en minúsculas).
2. Copia ese archivo a la **misma carpeta donde está el `.exe`** de la aplicación.
3. Abre la aplicación. La primera vez que uses una función que necesite conexión a Drive (subir, descargar, o **Options → Connect Google account**), se abrirá tu navegador pidiéndote iniciar sesión y autorizar el acceso.
4. Una vez autorizado, se genera automáticamente un `token.json` junto al `.exe` — no necesitas volver a autenticarte salvo que el token expire o lo revoques manualmente desde tu cuenta de Google.

Con esto, la aplicación queda lista para usar tu cuenta de Google Drive.

---

## Compilar la aplicación desde el código fuente

Si prefieres no confiar en el `.exe` de la sección de *Releases* y compilarlo tú mismo desde el código, sigue estos pasos.

### 1. Requisitos previos

- [Python 3.11 o superior](https://www.python.org/downloads/) instalado (marca la opción "Add to PATH" durante la instalación en Windows).
- Git (opcional, para clonar el repositorio) o descargar el código como ZIP directamente desde GitHub.

### 2. Descargar el código

```bash
git clone <URL-de-este-repositorio>
cd <carpeta-del-proyecto>
```

O bien, descarga el repositorio como ZIP desde GitHub (**Code → Download ZIP**) y descomprímelo.

### 3. Instalar las dependencias

Se recomienda usar un entorno virtual, aunque no es obligatorio:

```bash
python -m venv venv
venv\Scripts\activate        # en Windows
# source venv/bin/activate   # en macOS/Linux

pip install -r requirements.txt
```

Si el proyecto no incluye `requirements.txt`, instala manualmente:

```bash
pip install PySide6 google-api-python-client google-auth-httplib2 google-auth-oauthlib pyinstaller
```

### 4. Probar que funciona desde el código fuente

Antes de compilar, verifica que la app corre correctamente:

```bash
python main.py
```

Sigue la sección **"Cómo usar la aplicación"** de más arriba para generar tu propio `credentials.json` y colócalo en la carpeta del proyecto (junto a `main.py`) para poder probar la conexión a Drive.

### 5. Compilar el ejecutable

Desde la carpeta del proyecto, con el entorno virtual activado:

```bash
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." main.py
```

> En macOS/Linux, reemplaza el `;` del `--add-data` por `:` (ej. `"icon.ico:."`).

Esto genera el ejecutable dentro de la carpeta `dist/`.

De esta forma, compilas la app tú mismo desde el código fuente público, sin depender de ningún binario que no hayas generado con tus propias manos — y usando siempre tus propias credenciales de Google, nunca compartidas con nadie más.

---

## Estructura de archivos relevante (junto al `.exe` o al `main.py`)

| Archivo | Descripción | ¿Se incluye en el repo? |
|---|---|---|
| `credentials.json` | Credenciales OAuth de tu propio proyecto de Google Cloud. Cada usuario genera el suyo. | No |
| `token.json` | Token de sesión generado automáticamente tras el primer login. | No |
| `backup_info.json` | Carpetas incluidas/excluidas y datos internos de carpetas de Drive. Se genera/edita desde la app. | No |
| `backup_data.json` | Historial de archivos ya respaldados, usado para detectar cambios. Se genera automáticamente. | No |
| `icon.ico` | Ícono de la aplicación. | Sí |
