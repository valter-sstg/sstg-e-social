"""
db.py - Camada de acesso ao Supabase (substitui armazenamento em CSV)
Persistencia garantida independente de redeploys no Streamlit Cloud.
"""
import unicodedata
import pandas as pd
import streamlit as st


def _norm_col(nome: str) -> str:
    """Remove acentos de nomes de coluna: media_comunicação → media_comunicacao."""
    nfkd = unicodedata.normalize("NFKD", nome)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


@st.cache_resource(show_spinner=False)
def _get_sb():
    from supabase import create_client
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].replace("\n", "").replace("\r", "").strip()
    return create_client(url, key)


def ping():
    """Acorda o banco apos hibernacao (free tier hiberna apos 7 dias sem uso)."""
    try:
        _get_sb().table("config").select("chave").limit(1).execute()
    except Exception:
        pass


_ACESSOS_A2D = {
    "CPF": "cpf", "Empresa": "empresa", "CNPJ": "cnpj",
    "Funcao": "funcao", "Departamento": "departamento",
    "Data_Acesso_Liberado": "data_acesso_liberado",
    "Data_Inicio_Periodo": "data_inicio_periodo",
    "Data_Fim_Periodo": "data_fim_periodo",
    "Status": "status",
    "Data_Movimentacao": "data_movimentacao",
    "Motivo_Movimentacao": "motivo_movimentacao",
    "Senha_RH_Hash": "senha_rh_hash",
}
_ACESSOS_D2A = {v: k for k, v in _ACESSOS_A2D.items()}

_USUARIOS_A2D = {
    "Usuario": "usuario", "Nome": "nome",
    "Senha_Hash": "senha_hash", "Status": "status",
    "Data_Criacao": "data_criacao",
}
_USUARIOS_D2A = {v: k for k, v in _USUARIOS_A2D.items()}

_RESPOSTAS_D2A = {
    "cpf_hash": "CPF_Hash", "cnpj": "CNPJ", "empresa": "Empresa",
    "funcao": "Funcao", "departamento": "Departamento",
    "data": "Data", "media_geral": "Media_Geral",
}
_RESPOSTAS_A2D = {v: k for k, v in _RESPOSTAS_D2A.items()}
_RESPOSTAS_A2D["Funcao"] = "funcao"


def _to_db(registro, mapa):
    return {mapa.get(k, k.lower()): v for k, v in registro.items()}


def _df_rename(df, mapa):
    return df.rename(columns=mapa)


def carregar_acessos():
    sb = _get_sb()
    res = sb.table("acessos").select("*").execute()
    if not res.data:
        return pd.DataFrame()
    df = pd.DataFrame(res.data).drop(columns=["id"], errors="ignore")
    df = _df_rename(df, _ACESSOS_D2A)
    if "Funcao" in df.columns and "Funcao" not in df.columns:
        df = df.rename(columns={"Funcao": "Funcao"})
    return df


def salvar_acessos_em_lote(registros):
    if not registros:
        return
    sb = _get_sb()
    db_recs = []
    for r in registros:
        rec = {}
        for k, v in r.items():
            key_map = {"Funcao": "funcao"}
            key_map.update(_ACESSOS_A2D)
            rec[key_map.get(k, k.lower())] = v
        db_recs.append(rec)
    sb.table("acessos").upsert(db_recs, on_conflict="cpf,cnpj").execute()


def atualizar_acesso_campos(cpf, cnpj, campos):
    sb = _get_sb()
    db_campos = _to_db(campos, _ACESSOS_A2D)
    sb.table("acessos").update(db_campos).eq("cpf", cpf).eq("cnpj", cnpj).execute()


def atualizar_acessos_por_cnpj(cnpj, campos):
    sb = _get_sb()
    db_campos = _to_db(campos, _ACESSOS_A2D)
    sb.table("acessos").update(db_campos).eq("cnpj", cnpj).execute()


def deletar_acessos_empresa(cnpj):
    sb = _get_sb()
    sb.table("acessos").delete().eq("cnpj", cnpj).execute()


def deletar_todos_acessos():
    sb = _get_sb()
    sb.table("acessos").delete().neq("id", 0).execute()


def carregar_respostas(cnpj):
    sb = _get_sb()
    res = sb.table("respostas").select("*").eq("cnpj", cnpj).execute()
    if not res.data:
        return pd.DataFrame()
    df = pd.DataFrame(res.data).drop(columns=["id"], errors="ignore")
    rename = dict(_RESPOSTAS_D2A)
    for col in df.columns:
        if col.startswith("media_") and col != "media_geral":
            rename[col] = "Media_" + col[len("media_"):]
    return _df_rename(df, rename)


def cpf_respondeu(cnpj, cpf_hash):
    sb = _get_sb()
    res = (sb.table("respostas")
             .select("cpf_hash")
             .eq("cnpj", cnpj)
             .eq("cpf_hash", cpf_hash)
             .execute())
    return bool(res.data)


def salvar_resposta(dados):
    sb = _get_sb()
    db_rec = {}
    for k, v in dados.items():
        if k in _RESPOSTAS_A2D:
            db_rec[_RESPOSTAS_A2D[k]] = v
        elif k.startswith("Media_"):
            db_rec[k.lower()] = v
        else:
            db_rec[k.lower()] = v
    # Normaliza acentos em nomes de coluna (ex: media_comunicação → media_comunicacao)
    db_rec = {_norm_col(k): v for k, v in db_rec.items()}
    sb.table("respostas").upsert(db_rec, on_conflict="cpf_hash,cnpj").execute()


def deletar_respostas_empresa(cnpj):
    sb = _get_sb()
    sb.table("respostas").delete().eq("cnpj", cnpj).execute()


def deletar_todas_respostas():
    sb = _get_sb()
    sb.table("respostas").delete().neq("id", 0).execute()


def listar_cnpjs_com_respostas():
    sb = _get_sb()
    res = sb.table("respostas").select("cnpj").execute()
    if not res.data:
        return []
    return list({r["cnpj"] for r in res.data})


def carregar_usuarios():
    sb = _get_sb()
    res = sb.table("usuarios").select("*").execute()
    if not res.data:
        return pd.DataFrame(columns=["Usuario", "Nome", "Senha_Hash", "Status", "Data_Criacao"])
    df = pd.DataFrame(res.data).drop(columns=["id"], errors="ignore")
    return _df_rename(df, _USUARIOS_D2A)


def salvar_usuario(registro):
    sb = _get_sb()
    db_rec = _to_db(registro, _USUARIOS_A2D)
    sb.table("usuarios").upsert(db_rec, on_conflict="usuario").execute()


def atualizar_usuario_campos(usuario, campos):
    sb = _get_sb()
    db_campos = _to_db(campos, _USUARIOS_A2D)
    sb.table("usuarios").update(db_campos).eq("usuario", usuario).execute()


def get_config(chave):
    sb = _get_sb()
    res = sb.table("config").select("valor").eq("chave", chave).execute()
    return res.data[0]["valor"] if res.data else None


def set_config(chave, valor):
    sb = _get_sb()
    sb.table("config").upsert({"chave": chave, "valor": valor}, on_conflict="chave").execute()


def exportar_backup_zip():
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        df_a = carregar_acessos()
        if not df_a.empty:
            zf.writestr("db_acessos_autorizados.csv",
                        df_a.to_csv(index=False, sep=";", encoding="utf-8-sig"))
        df_u = carregar_usuarios()
        if not df_u.empty:
            zf.writestr("db_usuarios_operacionais.csv",
                        df_u.to_csv(index=False, sep=";", encoding="utf-8-sig"))
        sb = _get_sb()
        res_cfg = sb.table("config").select("*").execute()
        if res_cfg.data:
            import pandas as _pd
            df_cfg = _pd.DataFrame(res_cfg.data).drop(columns=["id"], errors="ignore")
            zf.writestr("db_admin_config.csv",
                        df_cfg.to_csv(index=False, sep=";", encoding="utf-8-sig"))
        for cnpj in listar_cnpjs_com_respostas():
            df_r = carregar_respostas(cnpj)
            if not df_r.empty:
                zf.writestr(f"respostas_CNPJ_{cnpj}.csv",
                            df_r.to_csv(index=False, sep=";", encoding="utf-8-sig"))
    buf.seek(0)
    return buf.getvalue()
