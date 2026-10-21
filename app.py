"""Interfaz educativa Streamlit para el asistente HITL de Recursos Humanos."""

import streamlit as st

from hitl_rrhh.agent import HRHITLAgent
from hitl_rrhh.settings import get_settings
from hitl_rrhh.store import CaseStore

st.set_page_config(page_title="HITL RR. HH.", page_icon="🧭", layout="wide")
settings = get_settings()
store = CaseStore(settings)
agent = HRHITLAgent(settings, store)

st.title("Asistente de Recursos Humanos · HITL")
st.caption("Prototipo académico · motor de política + skill modular + Hugging Face opcional + revisión humana")

with st.sidebar:
    st.subheader("Estado del entorno")
    st.write("Hugging Face:", "Token configurado" if settings.hf_token else "Modo local (sin token)")
    st.write("Modelo:", settings.hf_model_id)
    st.write("Vencimiento de revisión:", f"{settings.review_ttl_hours} horas")
    st.warning(
        "Usá únicamente datos ficticios. No ingreses nombres reales, DNI, salarios, evaluaciones, "
        "información médica ni legajos. Esta demo no tiene autenticación ni autorización de producción."
    )

assistant_tab, review_tab, audit_tab = st.tabs(["Asistente", "Cola de revisión humana", "Auditoría"])

with assistant_tab:
    st.markdown(
        "El asistente responde consultas informativas cubiertas por fuentes de demo, ayuda a redactar "
        "borradores y deriva cambios o decisiones laborales sensibles a revisión humana."
    )
    with st.form("hr_request_form", clear_on_submit=False):
        request_text = st.text_area(
            "Consulta (usar un caso ficticio)",
            placeholder="Ej.: ¿Cuál es el horario de atención de RR. HH.?",
            height=120,
        )
        consent = st.checkbox(
            "Confirmo que el texto es ficticio/anonimizado y autorizo enviarlo al proveedor Hugging Face si el token está configurado.",
            value=False,
        )
        submitted = st.form_submit_button("Evaluar consulta", type="primary")
    if submitted:
        result = agent.handle(request_text, consent_to_hf=consent)
        if result.decision in {"DERIVAR_A_RRHH", "REQUIERE_APROBACION", "DECISION_EXCLUSIVAMENTE_HUMANA"}:
            st.info(f"Estado: {result.decision}")
        else:
            st.success(f"Estado: {result.decision}")
        st.markdown(result.message)
        if result.source_title:
            st.caption(f"Referencia utilizada: {result.source_title}")
        if result.used_huggingface:
            st.caption("Borrador generado mediante Hugging Face Inference Providers. No se ejecutó ninguna acción externa.")
        if result.case_id:
            st.code(result.case_id, language=None)
            st.caption("ID del caso. Abrí la pestaña Cola de revisión humana para resolverlo.")

with review_tab:
    st.subheader("Casos pendientes")
    st.caption("Resolver un caso no modifica sistemas externos. La opción de aprobación significa únicamente habilitar una gestión manual posterior.")
    cases = store.list_cases()
    if not cases:
        st.info("No hay casos pendientes.")
    for case in cases:
        with st.expander(f"{case['category']} · {case['case_id'][:8]} · {case['decision']}"):
            st.write("**Solicitud anonimizada:**", case["request_redacted"])
            st.write("**Motivo de revisión:**", case["reason"])
            st.write("**Evidencia disponible:**", case["evidence"])
            st.write("**Propuesta para revisión:**", case["proposal"])
            st.write("**Consecuencias potenciales:**", case["consequences"])
            st.write("**Creado:**", case["created_at"])
            st.write("**Vence:**", case["expires_at"])
            with st.form(f"review_{case['case_id']}"):
                reviewer = st.text_input("Nombre/identificador del revisor", key=f"reviewer_{case['case_id']}")
                resolution = st.selectbox(
                    "Decisión humana",
                    ["APROBAR_PARA_GESTION_MANUAL", "RECHAZAR", "CORREGIR", "PEDIR_INFORMACION"],
                    format_func=lambda x: {
                        "APROBAR_PARA_GESTION_MANUAL": "Aprobar para gestión manual (sin ejecutar) ",
                        "RECHAZAR": "Rechazar",
                        "CORREGIR": "Corregir y solicitar nueva revisión",
                        "PEDIR_INFORMACION": "Pedir información adicional",
                    }[x],
                    key=f"resolution_{case['case_id']}",
                )
                notes = st.text_area("Motivo / corrección / información faltante", key=f"notes_{case['case_id']}")
                resolve = st.form_submit_button("Registrar decisión")
            if resolve:
                try:
                    ok = store.resolve_case(case["case_id"], reviewer, resolution, notes)
                    if ok:
                        st.success("Decisión registrada. No se ejecutó ninguna acción externa.")
                        st.rerun()
                    else:
                        st.error("El caso ya fue resuelto o venció. Actualizá la cola y revisá su estado.")
                except ValueError as exc:
                    st.error(str(exc))
    st.subheader("Historial reciente")
    history = store.list_cases(include_resolved=True)[:20]
    if history:
        st.dataframe(
            [
                {"ID": c["case_id"][:8], "Creado": c["created_at"], "Categoría": c["category"], "Estado": c["status"], "Revisor": c["reviewer"] or "—"}
                for c in history
            ],
            use_container_width=True,
            hide_index=True,
        )

with audit_tab:
    st.subheader("Eventos de auditoría")
    st.caption("Se registran eventos y decisiones, no el texto original completo del pedido.")
    events = store.audit_events(100)
    if events:
        st.dataframe(
            [
                {"Fecha UTC": e["created_at"], "Categoría": e["category"], "Decisión": e["decision"], "Estado": e["status"], "Revisor": e["reviewer"] or "—", "Detalle": e["detail"]}
                for e in events
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Todavía no hay eventos de auditoría.")

st.divider()
st.caption("Uso educativo. No reemplaza asesoría legal, políticas oficiales de RR. HH., controles de acceso, DLP ni un sistema de gestión de personal.")
