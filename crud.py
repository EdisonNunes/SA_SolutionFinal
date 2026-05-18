"""
Módulo CRUD - Compatibilidade com código legado.

Este módulo mantém compatibilidade com o código existente
enquanto direciona para os novos serviços.

DEPRECATED: Use services/clientes.py e services/servicos.py
"""

import warnings
from typing import List, Dict, Any, Optional
from core import LoggerManager
from services import ClienteService, ServicoService

# Avisar sobre depreciação
warnings.warn(
    "crud.py está deprecated. Use services/clientes.py e services/servicos.py",
    DeprecationWarning,
    stacklevel=2
)

logger = LoggerManager.get_logger(__name__)

# Instâncias dos serviços
_cliente_service = None
_servico_service = None

def _get_cliente_service() -> ClienteService:
    """Obtém instância do ClienteService."""
    global _cliente_service
    if _cliente_service is None:
        _cliente_service = ClienteService()
    return _cliente_service

def _get_servico_service() -> ServicoService:
    """Obtém instância do ServicoService."""
    global _servico_service
    if _servico_service is None:
        _servico_service = ServicoService()
    return _servico_service

# =====================================================
# CLIENTES - Funções de compatibilidade
# =====================================================

def listar_clientes(filtro_empresa: str = "") -> List[Dict[str, Any]]:
    """
    Lista clientes (compatibilidade).

    DEPRECATED: Use ClienteService.listar()
    """
    try:
        return _get_cliente_service().listar(filtro_empresa)
    except Exception as e:
        logger.error(f"Erro em listar_clientes: {e}")
        return []

def listar_todos_dados_clientes() -> List[Dict[str, Any]]:
    """
    Lista todos os dados de clientes (compatibilidade).

    DEPRECATED: Use ClienteService.listar_todos()
    """
    try:
        return _get_cliente_service().listar_todos()
    except Exception as e:
        logger.error(f"Erro em listar_todos_dados_clientes: {e}")
        return []

def incluir_cliente(dados: Dict[str, Any]) -> None:
    """
    Inclui cliente (compatibilidade).

    DEPRECATED: Use ClienteService.criar()
    """
    try:
        _get_cliente_service().criar(dados)
    except Exception as e:
        logger.error(f"Erro em incluir_cliente: {e}")
        raise

def alterar_cliente(id_cliente: int, dados: Dict[str, Any]) -> None:
    """
    Altera cliente (compatibilidade).

    DEPRECATED: Use ClienteService.atualizar()
    """
    try:
        _get_cliente_service().atualizar(id_cliente, dados)
    except Exception as e:
        logger.error(f"Erro em alterar_cliente: {e}")
        raise

def excluir_cliente(id_cliente: int) -> None:
    """
    Exclui cliente (compatibilidade).

    DEPRECATED: Use ClienteService.excluir()
    """
    try:
        _get_cliente_service().excluir(id_cliente)
    except Exception as e:
        logger.error(f"Erro em excluir_cliente: {e}")
        raise

# =====================================================
# SERVIÇOS - Funções de compatibilidade
# =====================================================

def listar_servicos(filtro_descricao: str = "") -> List[Dict[str, Any]]:
    """
    Lista serviços (compatibilidade).

    DEPRECATED: Use ServicoService.listar()
    """
    try:
        return _get_servico_service().listar(filtro_descricao)
    except Exception as e:
        logger.error(f"Erro em listar_servicos: {e}")
        return []

def listar_todos_dados_servicos() -> List[Dict[str, Any]]:
    """
    Lista todos os dados de serviços (compatibilidade).

    DEPRECATED: Use ServicoService.listar_todos()
    """
    try:
        return _get_servico_service().listar_todos()
    except Exception as e:
        logger.error(f"Erro em listar_todos_dados_servicos: {e}")
        return []

def incluir_servico(dados: Dict[str, Any]) -> None:
    """
    Inclui serviço (compatibilidade).

    DEPRECATED: Use ServicoService.criar()
    """
    try:
        _get_servico_service().criar(dados)
    except Exception as e:
        logger.error(f"Erro em incluir_servico: {e}")
        raise

def alterar_servico(id_servico: int, dados: Dict[str, Any]) -> None:
    """
    Altera serviço (compatibilidade).

    DEPRECATED: Use ServicoService.atualizar()
    """
    try:
        _get_servico_service().atualizar(id_servico, dados)
    except Exception as e:
        logger.error(f"Erro em alterar_servico: {e}")
        raise

def excluir_servico(id_servico: int) -> None:
    """
    Exclui serviço (compatibilidade).

    DEPRECATED: Use ServicoService.excluir()
    """
    try:
        _get_servico_service().excluir(id_servico)
    except Exception as e:
        logger.error(f"Erro em excluir_servico: {e}")
        raise

def verificar_uso_servico(id_servico: int) -> List[Dict[str, Any]]:
    """
    Verifica uso do serviço (compatibilidade).

    DEPRECATED: Use ServicoService.verificar_uso()
    """
    try:
        return _get_servico_service().verificar_uso(id_servico)
    except Exception as e:
        logger.error(f"Erro em verificar_uso_servico: {e}")
        return []

# =====================================================
# LEGACY - Manter compatibilidade
# =====================================================

class SupabaseProxy:
    """Proxy para manter compatibilidade com código legado."""

    def __init__(self):
        """Inicializa com cliente Supabase direto."""
        from core import get_db
        self._client = get_db()

    def __getattr__(self, name):
        """Delegar chamadas para o cliente Supabase real."""
        return getattr(self._client, name)

# Instância global para compatibilidade
supabase = SupabaseProxy()

# Funções de propostas (mantidas por enquanto)
def criar_proposta(dados):
    """Criar proposta - TODO: refatorar."""
    logger.warning("criar_proposta não implementada na nova arquitetura")
    return None

def atualizar_proposta(id_proposta, dados):
    """Atualizar proposta - TODO: refatorar."""
    logger.warning("atualizar_proposta não implementada na nova arquitetura")
    return None

def excluir_proposta(id_proposta):
    """Excluir proposta - TODO: refatorar."""
    logger.warning("excluir_proposta não implementada na nova arquitetura")
    return None

def buscar_propostas(filtro=""):
    """Buscar propostas - TODO: refatorar."""
    logger.warning("buscar_propostas não implementada na nova arquitetura")
    return []

def adicionar_item(dados):
    """Adicionar item - TODO: refatorar."""
    logger.warning("adicionar_item não implementada na nova arquitetura")
    return None

def buscar_itens(id_proposta):
    """Buscar itens - TODO: refatorar."""
    logger.warning("buscar_itens não implementada na nova arquitetura")
    return []

def atualizar_item(id_item, dados):
    """Atualizar item - TODO: refatorar."""
    logger.warning("atualizar_item não implementada na nova arquitetura")
    return None

def excluir_item(id_item):
    """Excluir item - TODO: refatorar."""
    logger.warning("excluir_item não implementada na nova arquitetura")
    return None

# ####################################################
# CLIENTES  - TABELA CLIENTES
# create table public.clientes (
#   id integer generated by default as identity not null,
#   empresa text not null,
#   cnpj text not null,
#   cep text not null,
#   endereco text not null,
#   cidade text not null,
#   uf text not null,
#   contato text not null,
#   departamento text not null,
#   telefone text not null,
#   mobile text not null,
#   email text not null,
#   constraint clientes_pkey primary key (id)
# ) TABLESPACE pg_default;
# ####################################################

def listar_clientes(filtro_empresa=""):
    query = supabase.table("clientes").select("id, empresa, cidade, telefone, contato")
    if filtro_empresa:
        query = query.filter("empresa", "ilike", f"%{filtro_empresa}%")
    query = query.order("empresa", desc=False)
    response = query.execute()
    return response.data

def listar_todos_dados_clientes():
    query = supabase.table("clientes").select("*").order("empresa", desc=False)
    response = query.execute()
    # print(response.data)
    return response.data
def incluir_cliente(dados):
    existe = supabase.table("clientes").select("*") \
        .eq("empresa", dados["empresa"]).eq("cidade", dados["cidade"]).execute()
    if existe.data:
        raise ValueError("Já existe um cliente com essa empresa e cidade.")
    # dados["id"] = uuid.uuid4().int >> 64
    supabase.table("clientes").insert(dados).execute()

def alterar_cliente(id, dados):
    supabase.table("clientes").update(dados).eq("id", id).execute()

def excluir_cliente(id):
    supabase.table("clientes").delete().eq("id", id).execute()

# ####################################################
# SERVIÇOS  - TABELA SERVICOS
# create table public.servicos (
#   id_servico integer generated by default as identity not null,
#   ref text not null,
#   codigo text not null,
#   tipo text not null,
#   codigo_raiz text not null,
#   descricao text null,
#   valor numeric(12, 2) not null,
#   constraint servicos_pkey primary key (id_servico)
# ) TABLESPACE pg_default;
# ####################################################    
def listar_servicos(filtro_empresa=""):
    query = supabase.table("servicos").select("id_servico, descricao, valor, ref, codigo, tipo")
    if filtro_empresa:
        query = query.filter("descricao", "ilike", f"%{filtro_empresa}%")
    query = query.order("descricao", desc=False)
    response = query.execute()
    return response.data

def listar_todos_dados_servicos():
    query = supabase.table("servicos").select("*").order("descricao", desc=False)
    response = query.execute()
    # print(response.data)
    return response.data

def incluir_servico(dados):
    existe = supabase.table("servicos").select("*") \
        .eq("descricao", dados["descricao"]).execute()
    #   .eq("empresa", dados["empresa"]).eq("cidade", dados["cidade"]).execute()
    if existe.data:
        raise ValueError("Já existe um serviço com essa descricao.")
    supabase.table("servicos").insert(dados).execute()

def alterar_servico(id, dados):
    supabase.table("servicos").update(dados).eq("id_servico", id).execute()

def excluir_servico(id):
    supabase.table("servicos").delete().eq("id_servico", id).execute()

def verificar_uso_servico(id_servico):
    """
    Verifica se o serviço está presente em alguma proposta.
    Retorna uma lista de dicionários com os dados das propostas encontradas,
    ou uma lista vazia se não houver uso.
    """
    response = supabase.table("itens_proposta") \
        .select("propostas(num_proposta, empresa, cidade, data_emissao)") \
        .eq("id_servico", id_servico) \
        .execute()
    
    propostas = []
    if response.data:
        ids_vistos = set()
        for item in response.data:
            # item['propostas'] pode ser um dict ou None se o join falhar (mas aqui deve ser dict)
            prop = item.get('propostas')
            if prop:
                # O join retorna um dicionário simples se for N:1
                # Garantir que num_proposta existe para deduplicação
                num = prop.get('num_proposta')
                if num and num not in ids_vistos:
                    ids_vistos.add(num)
                    propostas.append(prop)
    return propostas

# ####################################################
# PLANILHA DE COMPATIBILIDDE - TABELA SASDATA60
# create table public.sasdata60 (
#   id serial not null,
#   id_proposta integer null,
#   relatorio text null,
#   status_rel_01 text null,
#   dt_agendada_01 text null,
#   motivo_01 text null,
#   dt_emissao_01 text null,
#   cliente text null,
#   local_realizado_02 text null,
#   endereco_02 text null,
#   cidade_02 text null,
#   uf_02 text null,
#   cep_02 text null,
#   cnpj_02 text null,
#   tel_02 text null,
#   email_02 text null,
#   local_teste_03 text null,
#   pessoa_local_03 text null,
#   dt_chegada_03 text null,
#   hr_chegada_03 text null,
#   setor_03 text null,
#   cargo_03 text null,
#   id_sala_03 text null,
#   pedido_03 text null,
#   coment_03 text null,
#   ckl_ponto_04 text null,
#   ckl_espaco_04 text null,
#   ckl_tomada_04 text null,
#   ckl_balan_04 text null,
#   ckl_agua_04 text null,
#   ckl_conex_04 text null,
#   ckl_veda_04 text null,
#   ckl_freez_04 text null,
#   coment_04 text null,
#   linha_05 text null,
#   cat_membr_05 text null,
#   fabricante_05 text null,
#   poro_cat_membr_05 text null,
#   temp_filtra_05 text null,
#   tara_05 text null,
#   produto_05 text null,
#   area_mem_05 text null,
#   tmp_contato_05 text null,
#   tempera_local_05 text null,
#   lote_05 text null,
#   area_dis_05 text null,
#   armaz_05 text null,
#   umidade_05 text null,
#   volume_05 text null,
#   tipo_gas_05 text null,
#   lotem1_06 text null,
#   lotes1_06 text null,
#   cat_disp_06 text null,
#   lotem2_06 text null,
#   lotes2_06 text null,
#   lote_disp_06 text null,
#   lotem3_06 text null,
#   lotes3_06 text null,
#   serial_cat_disp_06 text null,
#   form_01_07 text null,
#   conc_01_07 text null,
#   form_02_07 text null,
#   conc_02_07 text null,
#   form_03_07 text null,
#   conc_03_07 text null,
#   form_04_07 text null,
#   conc_04_07 text null,
#   form_05_07 text null,
#   conc_05_07 text null,
#   form_06_07 text null,
#   conc_06_07 text null,
#   form_07_07 text null,
#   conc_07_07 text null,
#   form_08_07 text null,
#   conc_08_07 text null,
#   estab_08 text null,
#   form_09_07 text null,
#   conc_09_07 text null,
#   form_10_07 text null,
#   conc_10_07 text null,
#   ckl_mat_08 text null,
#   ckl_sens_08 text null,
#   pi_memb_1_09 text null,
#   pi_memb_2_09 text null,
#   pi_memb_3_09 text null,
#   fli_memb_1_09 text null,
#   fli_memb_2_09 text null,
#   fli_memb_3_09 text null,
#   pb_padraowfi_09 text null,
#   wfi_res1_09 text null,
#   wfi_res2_09 text null,
#   wfi_res3_09 text null,
#   wfi_id1_09 text null,
#   wfi_id2_09 text null,
#   wfi_id3_09 text null,
#   dt_wfi_09 text null,
#   hr_wfi_09 text null,
#   dt_wfip_10 text null,
#   hr_wfip_10 text null,
#   horas_contato_10 text null,
#   pb_refproduto_10 text null,
#   prd_res1_10 text null,
#   prd_res2_10 text null,
#   prd_res3_10 text null,
#   prd_id1_10 text null,
#   prd_id2_10 text null,
#   prd_id3_10 text null,
#   tmp_final1_11 text null,
#   tmp_final2_11 text null,
#   tmp_final3_11 text null,
#   res_padr1_12 text null,
#   res_padr2_12 text null,
#   res_padr3_12 text null,
#   id_padr1_12 text null,
#   id_padr2_12 text null,
#   id_padr3_12 text null,
#   pf_memb_1_13 text null,
#   pf_memb_2_13 text null,
#   pf_memb_3_13 text null,
#   peso_calc_14 text null,
#   dis_res1_14 text null,
#   dis_res2_14 text null,
#   dis_id1_14 text null,
#   dis_id2_14 text null,
#   crit_var_peso_15 text null,
#   volume_ref_15 text null,
#   crit_var_vazao_15 text null,
#   var_peso_membr_1 text null,
#   var_peso_membr_2 text null,
#   var_peso_membr_3 text null,
#   pvm text null,
#   status_peso text null,
#   var_vazao_membr_1 text null,
#   var_vazao_membr_2 text null,
#   var_vazao_membr_3 text null,
#   pvv text null,
#   status_vazao text null,
#   rpb_membrana_1 text null,
#   rpb_membrana_2 text null,
#   rpb_membrana_3 text null,
#   media_rpb text null,
#   pb_referencial text null,
#   pb_estimado text null,
#   conclusao text null,
#   constraint sasdata60_pkey primary key (id)
# ) TABLESPACE pg_default;
# ####################################################    
def listar_registros(filtro_relatorio="", tipo=""):
    # seleciona os campos desejados
    query = supabase.table("sasdata60").select("id, relatorio, cliente, status_rel_01")

    # filtro por substring (como antes)
    if filtro_relatorio:
        query = query.filter("relatorio", "ilike", f"%{filtro_relatorio}%")

    # novo filtro: relatorio que começa com o prefixo informado em `tipo`
    if tipo:
        # ilike '<tipo>%': começa com (case-insensitive)
        query = query.filter("relatorio", "ilike", f"{tipo}%")
        

    query = query.order("relatorio", desc=True)

    return query.execute().data

def listar_todos_registros():
    return supabase.table("sasdata60").select("*").order("relatorio", desc=False).execute().data

def incluir_registro(dados):
    supabase.table("sasdata60").insert(dados).execute()

def alterar_registro(id, dados):
    supabase.table("sasdata60").update(dados).eq("id", id).execute()

def excluir_registro(id):
    supabase.table("sasdata60").delete().eq("id", id).execute()    

def ComboBoxClientes():
    response = supabase.table("clientes").select("id, empresa, cidade").order('empresa').execute()
    # Verificar se a resposta tem dados
    if response.data and isinstance(response.data, list):
        clientes = response.data
        opcoes_combobox = [
            f"{cliente['empresa']} - {cliente['cidade']}" for cliente in clientes
        ]
        # print(opcoes_combobox)
    else:
        st.error("Erro ao carregar os dados dos clientes.")
        clientes = []
        opcoes_combobox = []
    return opcoes_combobox 

# ####################################################
# PROPOSTAS  - TABELA PROPOSTAS
# create table public.propostas (
#   id_proposta integer generated by default as identity not null,
#   id_cliente integer not null,
#   num_proposta text not null,
#   empresa text not null,
#   cnpj text not null,
#   endereco text not null,
#   cidade text not null,
#   uf text not null,
#   telefone text not null,
#   email text not null,
#   contato text not null,
#   status_rel_01 text null,
#   local_realizacao text null,
#   dt_agendada_01 date null,
#   dt_emissao_rel_01 date null,
#   motivo_cancelamento text null,
#   data_emissao date not null,
#   validade text not null,
#   cond_pagamento text not null,
#   referencia text null,
#   total_qtd numeric(12, 2) null default 0,
#   total_valor numeric(12, 2) null default 0,
#   created_at timestamp without time zone null default now(),
#   constraint propostas_pkey1 primary key (id_proposta),
#   constraint propostas_num_proposta_key unique (num_proposta),
#   constraint fk_proposta_cliente foreign KEY (id_cliente) references clientes (id) on delete RESTRICT
# ) TABLESPACE pg_default;

# create index IF not exists idx_propostas_cliente on public.propostas using btree (id_cliente) TABLESPACE pg_default;

# create trigger trg_snapshot_cliente BEFORE INSERT on propostas for EACH row
# execute FUNCTION fn_snapshot_cliente ();
# ####################################################  
def criar_proposta(dados: dict) -> int:
    res = supabase.table("propostas").insert(dados).execute()
    return res.data[0]["id_proposta"]

def atualizar_proposta(id_proposta: int, dados: dict):
    supabase.table("propostas").update(dados).eq("id_proposta", id_proposta).execute()

def excluir_proposta(id_proposta: int):
    supabase.table("propostas").delete().eq("id_proposta", id_proposta).execute()

def buscar_propostas(filtro: str = ""):
    q = (
        supabase
        .table("propostas")
        .select("*")
        # .order("data_emissao", desc=True)  # 🔥 ordem pela data (mais recente primeiro)
        .order("num_proposta", desc=True)  # 🔥 ordem pela data (mais recente primeiro)
        .order("id_proposta", desc=True)   # 🔒 desempate seguro
    )
    if filtro:
        q = q.ilike("num_proposta", f"%{filtro}%")
    return q.execute().data

# ####################################################
# ITENS DA PROPOSTA  - TABELA ITENS_PROPOSTA
# create table public.itens_proposta (
#   id_item_prop integer generated by default as identity not null,
#   id_proposta integer not null,
#   id_servico integer not null,
#   codigo_servico text not null,
#   descricao_servico text not null,
#   prazo_ddl text not null,
#   qtd numeric(12, 2) not null default 1,
#   preco_unitario numeric(12, 2) not null,
#   desconto numeric(12, 2) not null default 0,
#   total_item numeric GENERATED ALWAYS as (((qtd * preco_unitario) - desconto)) STORED (12, 2) null,
#   constraint itens_proposta_pkey primary key (id_item_prop),
#   constraint fk_item_proposta foreign KEY (id_proposta) references propostas (id_proposta) on delete CASCADE,
#   constraint fk_item_servico foreign KEY (id_servico) references servicos (id_servico) on delete RESTRICT
# ) TABLESPACE pg_default;
# create index IF not exists idx_itens_proposta_proposta on public.itens_proposta using btree (id_proposta) TABLESPACE pg_default;
# create index IF not exists idx_itens_proposta_servico on public.itens_proposta using btree (id_servico) TABLESPACE pg_default;
# create trigger trg_totais_proposta
# after INSERT
# or DELETE
# or
# update on itens_proposta for EACH row
# execute FUNCTION atualizar_totais_proposta ();
# ####################################################  
def adicionar_item(id_proposta: int, item: dict):
    item["id_proposta"] = id_proposta
    supabase.table("itens_proposta").insert(item).execute()

def atualizar_item(id_item_prop: int, dados: dict):
    supabase.table("itens_proposta").update(dados).eq("id_item_prop", id_item_prop).execute()

def excluir_item(id_item_prop: int):
    supabase.table("itens_proposta").delete().eq("id_item_prop", id_item_prop).execute()

def buscar_itens(id_proposta: int):
    return (
        supabase.table("itens_proposta")
        .select("*")
        .eq("id_proposta", id_proposta)
        .execute()
        .data
    )
# create table public.sequencia (
#   id bigint not null,
#   last_proposta text not null,
#   constraint sequencia_pkey primary key (id)
# ) TABLESPACE pg_default;
def ler_last_proposta() -> str:
    """
    Lê o campo 'last_proposta' do registro com id=1 na tabela 'sequencia'.
    """
    try:
        response = supabase.table("sequencia").select("last_proposta").eq("id", 1).execute()
        
        if response.data:
            return response.data[0]["last_proposta"]
        else:
            # Caso a tabela esteja vazia, retorna um valor padrão ou levanta erro
            return "C-2026001" 
    except Exception as e:
        st.error(f"Erro ao ler do Supabase: {e}")
        return None
    
def atualizar_last_proposta(nova_proposta: str):
    """
    Atualiza o campo 'last_proposta' do registro com id=1 na tabela 'sequencia'.
    """
    try:
        response = supabase.table("sequencia").update({"last_proposta": nova_proposta}).eq("id", 1).execute()
        return response
    except Exception as e:
        st.error(f"Erro ao atualizar o Supabase: {e}")
        return None    