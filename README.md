# 📥 Descargador de CFE en PDF desde WebService UCFE

Este script automatiza la consulta y descarga de **Comprobantes Fiscales Electrónicos (CFE)** emitidos por una empresa mediante un **WebService**. El objetivo principal es mantener una copia local de los comprobantes generados diariamente, evitando duplicados y registrando cada acción en archivos de log.

---

## 🚀 Funcionalidades

- Consulta automática de CFEs emitidos en el día.
- Comparación con archivos ya descargados.
- Descarga individual de los PDFs faltantes.
- Registro de descargas exitosas.
- Manejo robusto de errores (con registro en log, sin mostrar excepciones al usuario).

---

## 🗂️ Estructura esperada del proyecto

```
verificarYdescargarPDFs/
├── verificarYdescargarPDFs.py
├── config.json
├── /data                   ← PDFs descargados
├── /descargados            ← Archivos de control de descarga
└── /logs                   ← Archivos de log y respuestas de la API
```

---

## ⚙️ Archivo `config.json`

El script requiere un archivo `config.json` con los siguientes datos de configuración:

```json
{
  "BASE_URL": "https://...",
  "BASE_URL_LISTADOS": "https://...",
  "USER": "usuario_ws",
  "PASSWORD": "clave_ws",
  "RUT_EMPRESA": "123456780012",
  "CODIGO_COMERCIO": "Ejemplo123",
  "CODIGO_TERMINAL": "ABC-001",
  "PAGE_SIZE": 100,
  "TIPO_CFE": "111",
  "CARPETA_INSTALACION": ".",
  "CARPETA_LOCAL": "./data",
  "CARPETA_DESCARGADOS": "./descargados",
  "CARPETA_LOGS": "./logs"
}
```

> ✅ Asegurate de que las carpetas definidas existan o que el script tenga permisos para crearlas.

---

## 🧰 Requisitos

- Python 3.7+
- Paquetes incluidos en la biblioteca estándar:
  - `requests`
  - `base64`
  - `json`
  - `os`, `sys`
  - `datetime`
  - `xml.etree.ElementTree`

---

## 🛠️ Compilación a `.exe` (opcional)

Para ejecutar el script en una PC sin Python instalado:

1. Instalar [PyInstaller](https://pyinstaller.org/):
   ```
   pip install pyinstaller
   ```

2. Generar el ejecutable:
   ```
   pyinstaller --onefile --noconsole verificarYdescargarPDFs.py
   ```

3. El `.exe` se ubicará en la carpeta `/dist/`.

---

## 🛡️ Tolerancia a errores

- Todos los errores se registran en los logs (`/logs/log_YYYYMMDD.txt`).
- No se muestran excepciones al usuario.
- Si un archivo no puede ser descargado o guardado, el proceso continúa con el siguiente.

---

## 📄 Licencia

Este proyecto puede ser adaptado y reutilizado libremente para fines internos o automatización con WebServices. Se recomienda validar las credenciales, estructuras y endpoints según el entorno (producción o test).

---

## 👤 Autor

Ignacio Amaral  
📧 iamaral598@gmail.com  
🔗 [linkedin.com/in/ignacio-amaral](https://linkedin.com/in/ignacio-amaral) 
