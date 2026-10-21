# Instrucciones para agentes de desarrollo

Antes de modificar este repositorio, leer `agent.md` y `skills/rrhh-supervision/SKILL.md`.

## Arquitectura
- `policy.py` es la fuente de verdad de las decisiones HITL; no delegar esos permisos al LLM.
- `agent.py` orquesta política, skill/KB, proveedor y persistencia.
- `huggingface_client.py` solo redacta texto; no contiene funciones de ejecución de acciones.
- `store.py` es persistencia local para demo, no una base multiusuario de producción.
- `app.py` es la interfaz educativa Streamlit.

## Reglas de cambio
- No añadir herramientas que modifiquen datos de empleados ni integraciones de escritura sin una nueva revisión de riesgo, autorización por rol, aprobación explícita, revalidación y pruebas.
- No agregar puntuación, ranking o filtrado automatizado de candidatos.
- Mantener secretos fuera del repositorio. Nunca imprimir ni registrar `HF_TOKEN`.
- Toda fuente de políticas debe indicar origen, propietario, fecha de vigencia y estado de aprobación antes de usarse en producción.
- Nuevas reglas de clasificación requieren pruebas en `tests/` que cubran falsos positivos y negativos conocidos.
- Ejecutar `pytest` y `ruff check .` antes de proponer cambios.
