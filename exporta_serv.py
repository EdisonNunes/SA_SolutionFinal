import streamlit as st
import pandas as pd
from crud import supabase


def listar_servicos_export():
    query = supabase.table("servicos").select("id_servico, codigo, descricao, tipo, valor")
    query = query.order("codigo", desc=False)
    response = query.execute()
    return response.data

def listar_todos_servicos_export():
    query = supabase.table("servicos").select("*").order("codigo", desc=False)
    response = query.execute()
    # print(response.data)
    return response.data


st.info("### Exportar servicos", icon=":material/file_export:")

# servicos = listar_servicos_export(filtro_empresa=st.session_state.get("busca_codigo", ""))
servicos = listar_servicos_export()
df = pd.DataFrame(servicos) if servicos else pd.DataFrame()

if not df.empty:
    df["Selecionar"] = False
    resultado = st.data_editor(
        df,
        # use_container_width=True,
        hide_index=True,
        column_order=["Selecionar", "codigo", "descricao"],
        num_rows="dynamic",
    )
else:
    st.warning("Nenhum servico encontrado.")
    resultado = None

if not df.empty:
    # 🔽 Exportação
    with st.expander("⬇️ Exportar Registros", expanded=False):
        if resultado is not None:
            selecionados = resultado[resultado["Selecionar"] == True]

            if len(selecionados) == 1:
                nome_empresa = selecionados.iloc[0]["codigo"]
                st.warning(f'Deseja exportar o servico: **{nome_empresa}** ?')
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar Exportação"):
                        id_sel = selecionados.iloc[0]["id_servico"]
                        servico_completo = next((c for c in listar_todos_servicos_export() if c["id_servico"] == id_sel), None)
                        if servico_completo:
                            df_sel = pd.DataFrame([servico_completo])
                            csv_bytes = ('\ufeff' + df_sel.to_csv(index=False, sep=';')).encode("utf-8")
                            st.download_button(
                                "📁 Baixar CSV (1 servico completo)",
                                data=csv_bytes,
                                file_name=f"{servico_completo['codigo']}.csv",
                                mime="text/csv",
                            )
            elif len(selecionados) == 0:
                if st.button("✅ Exportar Todos"):
                    servicos_todos = listar_todos_servicos_export()
                    df_all = pd.DataFrame(servicos_todos)
                    csv_bytes = ('\ufeff' + df_all.to_csv(index=False, sep=';')).encode("utf-8")
                    st.download_button(
                        "📁 Baixar CSV (todos)",
                        data=csv_bytes,
                        file_name="servicos.csv",
                        mime="text/csv",
                    )
            else:
                st.error("Selecione apenas 1 item para exportar individualmente.")
        else:
            st.info("Nenhuma tabela carregada para exportação.")
