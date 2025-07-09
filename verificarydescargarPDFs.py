import requests
import base64
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import sys

def obtener_ruta_base():
    try:
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))
    except Exception as e:
        escribir_log(f"Error al obtener la ruta base: {e}")
        return "."

def escribir_log(mensaje):
    try:
        hoy = datetime.now().strftime("%Y%m%d")
        if not os.path.exists(CARPETA_LOGS):
            os.makedirs(CARPETA_LOGS)

        archivo_log = os.path.join(CARPETA_LOGS, f"log_{hoy}.txt")
        with open(archivo_log, 'a', encoding="utf-8") as log_file:
            hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{hora_actual} - {mensaje}\n")
    except Exception:
        pass  # Evita errores si no se puede escribir en el log

def cargar_config():
    try:
        ruta_config = os.path.join(obtener_ruta_base(), 'config.json')
        if not os.path.exists(ruta_config):
            raise FileNotFoundError(f"No se encontró el archivo de configuración: {ruta_config}")
        with open(ruta_config, 'r', encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        escribir_log(f"Error al cargar configuración: {e}")
        return {}

config = cargar_config()
BASE_URL = config.get('BASE_URL', '')
BASE_URL_LISTADOS = config.get('BASE_URL_LISTADOS', '')
USER = config.get('USER', '')
PASSWORD = config.get('PASSWORD', '')
RUT_EMPRESA = config.get('RUT_EMPRESA', '')
CODIGO_COMERCIO = config.get('CODIGO_COMERCIO', '')
CODIGO_TERMINAL = config.get('CODIGO_TERMINAL', '')
PAGE_SIZE = config.get('PAGE_SIZE', 100)
TIPO_CFE = config.get('TIPO_CFE', '')
CARPETA_INSTALACION = config.get('CARPETA_INSTALACION', '.')
CARPETA_LOCAL = config.get('CARPETA_LOCAL', './data')
CARPETA_DESCARGADOS = config.get('CARPETA_DESCARGADOS', './descargados')
CARPETA_LOGS = config.get('CARPETA_LOGS', './logs')

def obtener_autorizacion():
    try:
        credentials = f"{USER}:{PASSWORD}"
        auth_info = base64.b64encode(credentials.encode('ascii')).decode('ascii')
        return {
            "Authorization": f"Basic {auth_info}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    except Exception as e:
        escribir_log(f"Error al obtener autorización: {e}")
        return {}

def obtener_listado_hoy():
    try:
        hoy = datetime.now().strftime("%Y%m%d")
        url = f"{BASE_URL_LISTADOS}/ObtenerCfeEmitidosInicial"
        payload = {
            "rut": RUT_EMPRESA,
            "codigoComercio": CODIGO_COMERCIO,
            "codigoTerminal": CODIGO_TERMINAL,
            "fechaDesde": hoy,
            "fechaHasta": hoy,
            "tipoCfe": TIPO_CFE,
            "pageSize": PAGE_SIZE
        }

        response = requests.post(url, headers=obtener_autorizacion(), data=json.dumps(payload), timeout=100)

        if response.status_code == 200:
            respuesta_json = response.json()
            try:
                with open(os.path.join(CARPETA_LOGS, f"respuesta_API_{hoy}.json"), "w", encoding="utf-8") as f:
                    json.dump(respuesta_json, f, indent=4, ensure_ascii=False)
            except Exception as e:
                escribir_log(f"Error al guardar respuesta JSON: {e}")
            return respuesta_json.get("CfeEmitidos", [])
        else:
            escribir_log(f"Respuesta con código inesperado: {response.status_code}")
    except Exception as e:
        escribir_log(f"Error al obtener listado de hoy: {e}")
    return []

def obtener_pdfs_locales():
    try:
        hoy = datetime.now().strftime("%Y%m%d")
        return [f for f in os.listdir(CARPETA_LOCAL) if f.endswith(".pdf") and hoy in f]
    except Exception as e:
        escribir_log(f"Error al obtener PDFs locales: {e}")
        return []

def obtener_archivos_descargados():
    try:
        hoy = datetime.now().strftime("%Y%m%d")
        archivo_registro = os.path.join(CARPETA_DESCARGADOS, f"archivos_descargados_{hoy}.txt")
        if os.path.exists(archivo_registro):
            with open(archivo_registro, 'r', encoding='utf-8') as f:
                return set(f.read().splitlines())
    except Exception as e:
        escribir_log(f"Error al leer archivos descargados: {e}")
    return set()

def registrar_archivo_descargado(nombre_pdf):
    try:
        hoy = datetime.now().strftime("%Y%m%d")
        archivo_registro = os.path.join(CARPETA_DESCARGADOS, f"archivos_descargados_{hoy}.txt")
        with open(archivo_registro, 'a', encoding='utf-8') as f:
            f.write(nombre_pdf + '\n')
    except Exception as e:
        escribir_log(f"Error al registrar archivo descargado {nombre_pdf}: {e}")

def descargar_pdf(tipoCfe, serie, nro):
    try:
        url = f"{BASE_URL}/ObtenerPdf"
        payload = {"rut": RUT_EMPRESA, "tipoCfe": tipoCfe, "serieCfe": serie, "numeroCfe": nro}
        headers_aux = obtener_autorizacion()
        headers_aux["Accept"] = "text/xml"

        response = requests.post(url, headers=headers_aux, data=json.dumps(payload), timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            contenido_base64 = root.text
            return f"{tipoCfe}{serie}{nro}.pdf", contenido_base64
        else:
            escribir_log(f"Error HTTP al obtener PDF {tipoCfe}-{serie}-{nro}: {response.status_code}")
    except Exception as e:
        escribir_log(f"Error al descargar PDF {tipoCfe}-{serie}-{nro}: {e}")
    return None

def verificar_y_descargar():
    try:
        if not os.path.exists(CARPETA_LOCAL):
            os.makedirs(CARPETA_LOCAL)

        archivos_descargados = obtener_archivos_descargados()
        pdfs_nube = obtener_listado_hoy()
        pdfs_locales = obtener_pdfs_locales()

        escribir_log("Inicia el proceso...")

        for pdf in pdfs_locales:
            escribir_log(f"Archivo local encontrado: {pdf}")

        for cfe in pdfs_nube:
            nombre_pdf = f"{cfe['TipoCfe']}{cfe['Serie']}{cfe['Numero']}.pdf"
            if nombre_pdf not in archivos_descargados:
                escribir_log(f"Archivo no registrado: {nombre_pdf}. Iniciando descarga.")
                resultado = descargar_pdf(cfe['TipoCfe'], cfe['Serie'], cfe['Numero'])
                if resultado:
                    ruta_destino = os.path.join(CARPETA_LOCAL, resultado[0])
                    try:
                        with open(ruta_destino, "wb") as f:
                            f.write(base64.b64decode(resultado[1]))
                        escribir_log(f"Archivo guardado: {resultado[0]}")
                        registrar_archivo_descargado(nombre_pdf)
                    except PermissionError:
                        escribir_log(f"Permiso denegado al guardar el archivo: {ruta_destino}")
                    except Exception as e:
                        escribir_log(f"Error al guardar {resultado[0]}: {e}")
            else:
                escribir_log(f"Archivo ya registrado: {nombre_pdf}. No se descarga.")
        escribir_log("Finaliza el proceso.")
    except Exception as e:
        escribir_log(f"Error general en verificar_y_descargar: {e}")

if __name__ == "__main__":
    try:
        verificar_y_descargar()
    except Exception as e:
        escribir_log(f"Error no controlado en main: {e}")
