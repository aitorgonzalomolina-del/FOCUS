# Proyecto: Catálogo de Perfumes y Cosméticos

## Qué es este proyecto
Extracción automática del catálogo de productos desde el PDF `PERFUMES Y COSMÉTICOS 01-03-2026.pdf`.
Se generó una carpeta por producto dentro de `catalogo/`, cada una con:
- `info.json` → nombre, cantidad, precio, descripción
- `imagen.jpeg` → foto del producto (si existía en el PDF)

## Estado actual
- **286 productos** extraídos y organizados en `catalogo/`
- **268 imágenes** guardadas
- **20 productos sin imagen** (FOLIE PURE aparece en tabla sin fotos; algunos ANWAR tampoco tenían miniatura en el PDF)

## Estructura de carpetas
```
catalogo/
  BODY_CREAM_AFEER_AL_NOBLE_WAZEER/
    info.json
    imagen.jpeg
  PERFUME_LATTAFA_YARA_EDP/
    info.json
    imagen.jpeg
  ... (286 carpetas en total)
```

## Ejemplo de info.json
```json
{
  "nombre": "AMBIENTADOR LATTAFA AMEERAT AL ARAB AIR FRESHENER",
  "cantidad": "300ML",
  "precio": 4.25,
  "descripcion": "AMBIENTADOR LATTAFA AMEERAT AL ARAB AIR FRESHENER 300ML"
}
```

## Marcas incluidas
AFEER, AFNAN, AL HARAMAIN, AL WATANIAH, ANWAR, ARMAF, FOLIE PURE,
FRENCH AVENUE, KARSEELL, LATTAFA, MAISON ALHAMBRA, ORIENTICA,
RASASI, RAYHAAN, VICTORIA'S SECRET, XERJOFF, ZIMAYA

## Scripts en la carpeta
- `extraer_imagenes.py` → lee el PDF y guarda imágenes en cada carpeta de `catalogo/`
- `generar_catalogo.py` → recrea todas las carpetas y `info.json` desde datos hardcodeados (no necesita el PDF)
- `extraer_catalogo.py` → versión combinada (texto + imágenes desde el PDF)

## Dependencia
```bash
pip install PyMuPDF
```

## Si querés volver a generar todo desde cero
```bash
python generar_catalogo.py   # crea carpetas + info.json
python extraer_imagenes.py   # agrega las imágenes del PDF
```

## Agentes instalados (sesión 2026-03-18)

### Agente 1: Web Search (DuckDuckGo) — LISTO
- Script: `web_search_agent.py`
- Dependencia: `pip install ddgs`
- Uso:
  ```bash
  python web_search_agent.py "perfumes arabes Argentina"
  python web_search_agent.py "tendencias 2025" --modo noticias
  python web_search_agent.py "consulta" --resultados 10 --guardar
  ```
- Los resultados guardados van a `busquedas/<timestamp>.json`

### Agentes pendientes (necesitan credenciales)
| Agente | Credencial necesaria |
|--------|---------------------|
| Email SMTP | host SMTP, usuario, contraseña |
| Google Sheets | Credenciales Google (OAuth JSON) |
| Google Calendar | Credenciales Google (OAuth JSON) |
| Trello | API key + token |
| Buffer | Access token |
| Zapier | Webhook URL |
| DALL-E 3 | OpenAI API key |
| Dialogflow | Google Cloud service account |

## Contenido para RRSS (sesión 2026-03-18)

Se generó un prompt para Leonardo.ai para video/reel del producto:
**PERFUME AL HARAMAIN AMBER OUD GOLD 999.9 DUBAI EDITION EDP 100ML — $39.95**

Prompt generado (en inglés, modelo Motion 2.0, 9:16, 6s):
- Botella dorada sobre mármol negro
- Humo dorado y partículas de oud
- Cámara orbitando la botella
- Estética árabe de lujo

Caption sugerido:
"Lujo árabe en cada gota. Al Haramain Amber Oud Gold — Dubai Edition. Solo en FOCUS."

## Próximos pasos posibles
- Continuar instalando agentes (empezar por Email SMTP — solo necesita usuario/pass de Gmail)
- Generar más prompts de video/imagen para otros productos del catálogo
- Agregar campo `marca` al info.json de cada producto
- Exportar todo a un CSV o base de datos
- Crear una interfaz web para navegar el catálogo
