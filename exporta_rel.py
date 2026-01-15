import streamlit as st
import pandas as pd
from crud import listar_registros, listar_todos_registros

st.info("### Exportar Relatórios", icon=":material/csv:")

registros = listar_registros(filtro_relatorio=st.session_state.get("ger_busca_relatorio", ""))
df = pd.DataFrame(registros) if registros else pd.DataFrame()

if not df.empty:
    df["Selecionar"] = False
    resultado = st.data_editor(
        df,
        # use_container_width=True,
        hide_index=True,
        column_order=["Selecionar", "relatorio", "cliente"],
        column_config={
            "relatorio": st.column_config.TextColumn("Relatório"),
            "cliente": st.column_config.TextColumn("Empresa"),
        },
        num_rows="dynamic",
    )
else:
    st.warning("Nenhum registro encontrado.")
    resultado = None

if not df.empty:
    # 🔽 Exportação
    with st.expander("⬇️ Exportar Registros", expanded=False):
        # if 'confirmar_exportar' not in st.session_state:
        #     st.session_state.confirmar_exportar = False

        if resultado is not None:
            selecionados = resultado[resultado["Selecionar"] == True]

            if len(selecionados) == 1:
                nome_relatorio = selecionados.iloc[0]["relatorio"]
                st.warning(f'Deseja exportar o relatório: **{nome_relatorio}** ?')
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar Exportação"):
                        id_sel = selecionados.iloc[0]["id"]
                        registro_completo = next((r for r in listar_todos_registros() if r["id"] == id_sel), None)
                        if registro_completo:
                            df_sel = pd.DataFrame([registro_completo])
                            csv_bytes = ('\ufeff' + df_sel.to_csv(index=False, sep=';')).encode("utf-8")
                            st.download_button(
                                "📁 Baixar CSV (1 item completo)",
                                data=csv_bytes,
                                file_name=f"{registro_completo['relatorio']}.csv",
                                mime="text/csv",
                            )
            elif len(selecionados) == 0:
                if st.button("✅ Exportar Todos"):
                    registros_todos = listar_todos_registros()
                    df_all = pd.DataFrame(registros_todos)
                    csv_bytes = ('\ufeff' + df_all.to_csv(index=False, sep=';')).encode("utf-8")
                    st.download_button(
                        "📁 Baixar CSV (todos)",
                        data=csv_bytes,
                        file_name="planilha_completa.csv",
                        mime="text/csv",
                    )
            else:
                st.error("Selecione apenas 1 item para exportar individualmente.")
        else:
            st.info("Nenhuma tabela carregada para exportação.")
