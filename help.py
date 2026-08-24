HELP_HTML = """
<h2>Cómo conectar tu cuenta de Google Drive</h2>

<h3>¿Por qué tengo que crear mi propio proyecto en Google Cloud?</h3>

<p>Puede parecer un paso tedioso, pero tiene una razón concreta: esta
aplicación corre completamente en tu propio computador y se comunica
directamente con Google Drive, sin utilizar un servidor externo para
almacenar o procesar tus archivos.</p>

<p>Para conectarse a Google Drive mediante OAuth, la aplicación necesita
identificarse ante los servidores de Google. Para las aplicaciones de
escritorio, Google requiere crear un cliente OAuth 2.0 en un proyecto de
Google Cloud y descargar sus credenciales como 'credentials.json'.</p>

<p>Este archivo no contiene tus credenciales de Google ni da acceso directo
a tu Drive. Durante el primer inicio de sesión, Google te muestra qué
permisos solicita la aplicación y, una vez que autorizas el acceso, se
genera el token que la aplicación utiliza para realizar las operaciones
permitidas.</p>

<p>Por eso debes crear o proporcionar las credenciales de OAuth para esta
aplicación. Es un proceso que se realiza una sola vez.</p>

<h3>1. Crear un proyecto en Google Cloud Console</h3>
<ol>
<li>Ve a <a href="https://console.cloud.google.com/">Google Cloud Console</a>.</li>
<li>Inicia sesión con la cuenta de Google que quieras usar para el backup.</li>
<li>En la parte superior, haz clic en el selector de proyectos → <b>Nuevo Proyecto</b>.</li>
<li>Dale un nombre (por ejemplo, <i>Drive Backup Utility</i>) y créalo.</li>
</ol>

<h3>2. Habilitar la API de Google Drive</h3>
<ol>
<li>Con el proyecto recién creado seleccionado, ve directamente a
<a href="https://console.cloud.google.com/apis/library/drive.googleapis.com">Habilitar Google Drive API</a>.</li>
<li>Haz clic en <b>Habilitar</b> (Enable).</li>
</ol>

<h3>3. Configurar la pantalla de consentimiento OAuth</h3>
<ol>
<li>Ve a <a href="https://console.cloud.google.com/auth/overview">Menú ☰ → Google Auth Platform → Overview</a>.</li>
<li>Si aparece el mensaje de que la plataforma no está configurada, haz clic en <b>Comenzar / Get Started</b>.</li>
<li>En <b>App Information</b>, ingresa un nombre para la app (por ejemplo, <i>Drive Backup Utility</i>) y un correo de soporte.</li>
<li>Avanza y, en <b>Audience</b>, selecciona <b>External</b> (a menos que uses una cuenta de Google Workspace/organización).</li>
<li>Completa el correo de contacto y acepta la política de datos (Google API Services User Data Policy).</li>
<li>Haz clic en <b>Crear/Create</b>. No es necesario agregar scopes manualmente en este paso.</li>
</ol>

<p><i>Nota: como la app queda en modo de prueba ("Testing"), Google puede
advertirte que la app "no está verificada" al iniciar sesión. Esto es
normal para uso personal — haz clic en <b>Avanzado → Ir a [nombre de tu
app] (no seguro)</b> para continuar. Es tu propio proyecto, con tus propias
credenciales, así que es seguro.</i></p>

<h4>Agregar usuarios de prueba (importante)</h4>
<p>Mientras tu app esté en modo "Testing" (que es el estado por defecto y
en el que se queda a menos que la envíes a verificación de Google, algo
innecesario para uso personal), <b>solo las cuentas de Google que agregues
explícitamente como usuarios de prueba podrán iniciar sesión</b> —
cualquier otra cuenta, aunque sea tuya, va a recibir un error de acceso
denegado al intentar autorizar la app.</p>

<p>Para agregar las cuentas que necesitas que funcionen:</p>
<ol>
<li>Ve a <a href="https://console.cloud.google.com/auth/audience">Menú ☰ → Google Auth Platform → Audience</a>.</li>
<li>Baja hasta la sección <b>Test users</b>.</li>
<li>Haz clic en <b>Add users</b>.</li>
<li>Ingresa el correo (o correos) de Gmail de cada cuenta que vaya a usar la aplicación.</li>
<li>Guarda los cambios.</li>
</ol>

<h3>4. Crear las credenciales (OAuth Client ID)</h3>
<ol>
<li>Ve a <a href="https://console.cloud.google.com/auth/clients">Menú ☰ → Google Auth Platform → Clients</a>.</li>
<li>Haz clic en <b>Crear Cliente / Create Client</b>.</li>
<li>En <b>Application type</b>, elige <b>Desktop app</b>.</li>
<li>Dale un nombre (el que quieras, solo es para identificarlo en la consola).</li>
<li>Haz clic en <b>Crear/Create</b>.</li>
<li>Descarga el archivo JSON generado (botón de descarga junto al cliente recién creado).</li>
</ol>

<h3>5. Colocar las credenciales junto al ejecutable</h3>
<ol>
<li>Renombra el archivo descargado a <code>credentials.json</code> exactamente (todo en minúsculas).</li>
<li>Copia ese archivo a la <b>misma carpeta donde está el .exe</b> de la aplicación.</li>
<li>Abre la aplicación. La primera vez que uses una función que necesite conexión a Drive
(subir, descargar, o <b>Options → Connect Google account</b>), se abrirá tu navegador
pidiéndote iniciar sesión y autorizar el acceso.</li>
<li>Una vez autorizado, se genera automáticamente un <code>token.json</code> junto al .exe
— no necesitas volver a autenticarte salvo que el token expire o lo revoques manualmente
desde tu cuenta de Google.</li>
</ol>

<p>Con esto, la aplicación queda lista para usar tu cuenta de Google Drive.</p>
"""