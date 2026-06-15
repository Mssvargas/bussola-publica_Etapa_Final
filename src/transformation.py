import time
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import table, column
import logging

# Força o silenciamento do motor do SQLAlchemy E do logger do root para pacotes terceiros
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy.engine.Engine').setLevel(logging.ERROR)

# Importa as classes especialistas do módulo vizinho
from src.transformers import (
    TransformadorDeputados,
    TransformadorPartidos,
    TransformadorProposicoes,
    TransformadorVotacoes
)

log = logging.getLogger(__name__)

class ValidadorDados:
    """Valida DataFrames antes da carga no banco."""

    def validar(self, df, nome_tabela, campos_obrigatorios=None, coluna_id=None):
        """Aplica todas as validações em sequência e retorna o DataFrame limpo."""
        relatorio = {
            "tabela": nome_tabela,
            "original": len(df),
            "alertas": []
        }

        if df.empty:
            log.warning(f"  [{nome_tabela}] DataFrame vazio - nenhuma validação aplicada.")
            relatorio["final"] = 0
            return df, relatorio

        if campos_obrigatorios:
            df, relatorio = self._validar_nulos(df, campos_obrigatorios, nome_tabela, relatorio)

        if coluna_id and coluna_id in df.columns:
            df, relatorio = self._deduplicar(df, coluna_id, nome_tabela, relatorio)

        colunas_data = [c for c in df.columns if "data" in c.lower()]
        for col in colunas_data:
            df, relatorio = self._validar_datas(df, col, nome_tabela, relatorio)

        relatorio["final"] = len(df)
        removidos = relatorio["original"] - relatorio["final"]
        log.info(f"  [{nome_tabela}] Validação concluída: {relatorio['final']} linhas válidas | {removidos} removidas")

        return df, relatorio

    def _validar_nulos(self, df, campos, nome_tabela, relatorio):
        antes = len(df)
        df_valido = df.dropna(subset=[c for c in campos if c in df.columns])
        nulos = antes - len(df_valido)

        if nulos > 0:
            msg = f"  [{nome_tabela}] {nulos} linhas com nulos em campos obrigatórios {campos}"
            log.warning(msg)
            relatorio["alertas"].append(msg)

            for campo in campos:
                if campo in df.columns:
                    qtd = df[campo].isna().sum()
                    if qtd > 0:
                        log.warning(f"    -> Campo '{campo}': {qtd} nulos")

        return df_valido, relatorio

    def _deduplicar(self, df, coluna_id, nome_tabela, relatorio):
        antes = len(df)
        df_dedup = df.drop_duplicates(subset=[coluna_id], keep="first")
        duplicados = antes - len(df_dedup)

        if duplicados > 0:
            msg = f"  [{nome_tabela}] {duplicados} registros duplicados removidos (por '{coluna_id}')"
            log.warning(msg)
            relatorio["alertas"].append(msg)

        return df_dedup, relatorio

    def _validar_datas(self, df, coluna, nome_tabela, relatorio):
        if coluna not in df.columns:
            return df, relatorio

        if not pd.api.types.is_datetime64_any_dtype(df[coluna]):
            df[coluna] = pd.to_datetime(df[coluna], errors="coerce")

        nulas = df[coluna].isna().sum()
        if nulas > 0:
            msg = f"  [{nome_tabela}] {nulas} datas inválidas/nulas em '{coluna}'"
            log.warning(msg)
            relatorio["alertas"].append(msg)

        data_min = pd.Timestamp("2000-01-01")
        data_max = pd.Timestamp(datetime.today())

        invalidas = df[(df[coluna].notna()) & ((df[coluna] < data_min) | (df[coluna] > data_max))]
        if len(invalidas) > 0:
            msg = f"  [{nome_tabela}] {len(invalidas)} datas fora do range válido em '{coluna}'"
            log.warning(msg)
            relatorio["alertas"].append(msg)
            df = df[~((df[coluna].notna()) & ((df[coluna] < data_min) | (df[coluna] > data_max)))]

        return df, relatorio

    def validar_valores_positivos(self, df, colunas_monetarias, nome_tabela):
        for col in colunas_monetarias:
            if col not in df.columns:
                continue
            negativos = df[df[col] < 0]
            if len(negativos) > 0:
                log.warning(f"  [{nome_tabela}] {len(negativos)} valores negativos em '{col}'")
                df = df[df[col] >= 0]
        return df

class CargaPostgreSQL:
    """Gerencia a conexão com o PostgreSQL e a carga incremental dos DataFrames."""

    def __init__(self, database_url):
        self.database_url = database_url
        self.engine = None

    def conectar(self):
        try:
            self.engine = create_engine(self.database_url, echo=False)
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            log.info("  Conexão com PostgreSQL estabelecida com sucesso (Carga Incremental).")
            return True
        except Exception as e:
            log.error(f"  Erro ao conectar no PostgreSQL: {e}")
            return False

    def _garantir_constraint_unica(self, conn, nome_tabela, coluna_id):
        """
        Garante que `coluna_id` tenha uma constraint PRIMARY KEY ou UNIQUE.

        Sem essa constraint, o `INSERT ... ON CONFLICT (coluna_id)` falha
        com "no unique or exclusion constraint" e o carregar() cai no
        fallback de TRUNCATE + append a cada execução - o que reseta
        created_at de toda a tabela e apaga o enriquecimento de IA
        (resumo_executivo, tema). Idempotente: não falha se a tabela ainda
        não existir ou se a constraint já existir.
        """
        try:
            existe_tabela = conn.execute(
                text("SELECT to_regclass(:tabela)"), {"tabela": nome_tabela}
            ).scalar()
            if not existe_tabela:
                return

            existe_constraint = conn.execute(text("""
                SELECT 1
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                  ON tc.constraint_name = kcu.constraint_name
                 AND tc.table_name = kcu.table_name
                WHERE tc.table_name = :tabela
                  AND tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
                  AND kcu.column_name = :coluna
            """), {"tabela": nome_tabela, "coluna": coluna_id}).scalar()

            if not existe_constraint:
                conn.execute(text(
                    f'ALTER TABLE "{nome_tabela}" '
                    f'ADD CONSTRAINT "{nome_tabela}_{coluna_id}_key" UNIQUE ("{coluna_id}")'
                ))
                log.info(f"  [{nome_tabela}] Constraint única criada em '{coluna_id}'.")
        except Exception as e:
            log.warning(f"  [{nome_tabela}] Não foi possível garantir constraint única em '{coluna_id}': {e}")

    def carregar(self, df, nome_tabela, coluna_id=None):
        """Aplica Upsert. Se a tabela não tiver chave única, limpa via TRUNCATE e faz Append."""
        if df.empty:
            log.warning(f"  [{nome_tabela}] DataFrame vazio - carga ignorada.")
            return 0

        if self.engine is None:
            log.error(f"  [{nome_tabela}] Sem conexão com o banco.")
            return 0

        if not coluna_id:
            try:
                df.to_sql(nome_tabela, con=self.engine, if_exists="append", index=False, method="multi", chunksize=500)
                return len(df)
            except Exception as e:
                log.error(f"  [{nome_tabela}] Erro no append simples: {e}")
                return 0

        try:
            # Tenta executar a inserção em modo Upsert nativo
            target_table = table(nome_tabela, *[column(col) for col in df.columns])
            registros = df.to_dict(orient="records")

            with self.engine.begin() as conn:
                # Garante que a coluna usada no ON CONFLICT tenha uma
                # constraint UNIQUE/PK - sem isso, o upsert sempre cai no
                # fallback de TRUNCATE (e created_at é resetado a cada run).
                self._garantir_constraint_unica(conn, nome_tabela, coluna_id)

                stmt = insert(target_table).values(registros)
                colunas_atualizar = {col: stmt.excluded[col] for col in df.columns if col != coluna_id}
                upsert_stmt = stmt.on_conflict_do_update(index_elements=[coluna_id], set_=colunas_atualizar)
                conn.execute(upsert_stmt)
                log.info(f"  [{nome_tabela}] Upsert de {len(df)} registros concluído com sucesso.")
                return len(df)

        except Exception as e:
            # Se cair aqui por falta de unique constraint, aplica a estratégia Truncate + Append
            if "no unique or exclusion constraint" in str(e).lower():
                log.warning(f"  [{nome_tabela}] Sem constraint única definida no banco. Aplicando estratégia de atualização total.")
                try:
                    with self.engine.begin() as conn:
                        conn.execute(text(f"TRUNCATE TABLE {nome_tabela} RESTART IDENTITY CASCADE;"))
                    df.to_sql(nome_tabela, con=self.engine, if_exists="append", index=False, method="multi", chunksize=500)
                    log.info(f"  [{nome_tabela}] Carga de {len(df)} registros atualizada com sucesso via substituição total.")
                    return len(df)
                except Exception as ex:
                    log.error(f"  [{nome_tabela}] Falha crítica na estratégia de atualização alternativa: {ex}")
            else:
                log.error(f"  [{nome_tabela}] Erro ao realizar Upsert: {e}")

        return 0

    def carregar_incremental_assoc(self, df, nome_tabela, coluna_fk):
        """
        Carga incremental para tabelas associativas SEM chave única própria
        (ex: fato_proposicoes_autores, fato_votos).

        Por que não usar TRUNCATE/append puro aqui?
          - TRUNCATE apagaria também os registros de execuções anteriores
            referentes a outras proposições/votações, impedindo o banco de
            ACUMULAR histórico (entregável "Supabase com >= 30 dias de dados").
          - "append" puro duplicaria as linhas a cada execução, já que estas
            tabelas não têm PK/constraint única para um upsert.

        Estratégia: DELETE escopado pelos ids de `coluna_fk` presentes no
        lote atual + INSERT dos registros novos. Isso renova os
        autores/votos das proposições/votações deste lote sem afetar os
        registros de outras proposições/votações carregadas anteriormente.
        """
        if df.empty:
            log.warning(f"  [{nome_tabela}] DataFrame vazio - carga ignorada.")
            return 0

        if self.engine is None:
            log.error(f"  [{nome_tabela}] Sem conexão com o banco.")
            return 0

        if coluna_fk not in df.columns:
            log.warning(
                f"  [{nome_tabela}] Coluna '{coluna_fk}' ausente - "
                f"carga incremental não é possível, usando 'append' simples."
            )
            return self.carregar(df, nome_tabela)

        try:
            with self.engine.begin() as conn:
                existe = conn.execute(
                    text("SELECT to_regclass(:tabela)"),
                    {"tabela": nome_tabela}
                ).scalar()

                if existe:
                    ids = df[coluna_fk].dropna().unique().tolist()
                    if ids:
                        stmt = text(
                            f'DELETE FROM "{nome_tabela}" WHERE "{coluna_fk}" IN :ids'
                        ).bindparams(bindparam("ids", expanding=True))
                        conn.execute(stmt, {"ids": ids})

                df.to_sql(
                    nome_tabela, con=conn,
                    if_exists=("append" if existe else "replace"),
                    index=False, method="multi", chunksize=500
                )

            qtd = len(df)
            log.info(
                f"  [{nome_tabela}] {qtd} registros carregados "
                f"(delete+insert escopado por '{coluna_fk}')."
            )
            return qtd
        except SQLAlchemyError as e:
            log.error(f"  [{nome_tabela}] Erro SQLAlchemy: {e}")
        except Exception as e:
            log.error(f"  [{nome_tabela}] Erro inesperado: {e}")

        return 0

    def desconectar(self):
        if self.engine:
            self.engine.dispose()
            log.info("  Conexão com PostgreSQL encerrada.")

class PipelineEtapa3:
    """Orquestra o pipeline ETL da Etapa 3."""

    def __init__(self, raw_dir, database_url):
        self.raw_dir = Path(raw_dir)
        self.t_deputados = TransformadorDeputados(raw_dir)
        self.t_partidos = TransformadorPartidos(raw_dir)
        self.t_props = TransformadorProposicoes(raw_dir)
        self.t_vots = TransformadorVotacoes(raw_dir)
        self.validador = ValidadorDados()
        self.banco = CargaPostgreSQL(database_url)

    def executar(self):
        inicio = time.time()
        log.info("BUSSOLA PUBLICA - Pipeline ETL | Etapa 3: Transformação + Carga")
        log.info(f"  Fonte   : {self.raw_dir}")

        resumo = {}

        if not self.banco.conectar():
            log.error("Pipeline abortado: não foi possível conectar ao banco.")
            return resumo

        # --- 1. Dimensão: Deputados ---
        try:
            df_dep = self.t_deputados.transformar()
            df_dep, _ = self.validador.validar(
                df_dep, "dim_deputados",
                campos_obrigatorios=["id_deputado", "nome"],
                coluna_id="id_deputado"
            )
            resumo["dim_deputados"] = self.banco.carregar(df_dep, "dim_deputados", coluna_id="id_deputado")
        except Exception as e:
            log.error(f"Falha em dim_deputados: {e}")
            resumo["dim_deputados"] = "ERRO"

        # --- 2. Dimensão: Partidos ---
        try:
            df_part = self.t_partidos.transformar()
            df_part, _ = self.validador.validar(
                df_part, "dim_partidos",
                campos_obrigatorios=["id_partido", "sigla"],
                coluna_id="id_partido"
            )
            resumo["dim_partidos"] = self.banco.carregar(df_part, "dim_partidos", coluna_id="id_partido")
        except Exception as e:
            log.error(f"Falha em dim_partidos: {e}")
            resumo["dim_partidos"] = "ERRO"

        # --- 3. Fato: Proposições + Autores ---
        try:
            resultado_props = self.t_props.transformar()

            df_props = resultado_props["proposicoes"]
            df_props, _ = self.validador.validar(
                df_props, "fato_proposicoes",
                campos_obrigatorios=["id_proposicao", "ementa"],
                coluna_id="id_proposicao"
            )
            # Upsert por id_proposicao: preserva resumo_executivo/tema (Etapa 4/5)
            # já gravados em proposições existentes.
            resumo["fato_proposicoes"] = self.banco.carregar(df_props, "fato_proposicoes", coluna_id="id_proposicao")

            df_autores = resultado_props["autores"]
            df_autores, _ = self.validador.validar(
                df_autores, "fato_proposicoes_autores",
                campos_obrigatorios=["id_proposicao"]
            )
            # Delete+insert escopado por id_proposicao: renova os autores das
            # proposições deste lote sem apagar autores de execuções anteriores.
            resumo["fato_proposicoes_autores"] = self.banco.carregar_incremental_assoc(
                df_autores, "fato_proposicoes_autores", coluna_fk="id_proposicao"
            )
        except Exception as e:
            log.error(f"Falha em fato_proposicoes: {e}")
            resumo["fato_proposicoes"] = "ERRO"


        # --- 4. Fato: Votações + Votos ---
        try:
            resultado_vots = self.t_vots.transformar()

            # TABELA: fato_votacoes
            df_vots = resultado_vots["votacoes"]
            df_vots, _ = self.validador.validar(
                df_vots, "fato_votacoes",
                campos_obrigatorios=["id_votacao"], # Valida apenas o ID base
                coluna_id="id_votacao"
            )

            # Upsert por id_votacao: substitui o TRUNCATE CASCADE anterior,
            # que zerava created_at e impedia o acúmulo histórico de votações.
            resumo["fato_votacoes"] = self.banco.carregar(df_vots, "fato_votacoes", coluna_id="id_votacao")

            # TABELA: fato_votos
            df_votos = resultado_vots["votos"]
            df_votos, _ = self.validador.validar(
                df_votos, "fato_votos",
                campos_obrigatorios=["id_votacao", "tipo_voto"] # Valida as colunas reais
            )
            # Delete+insert escopado por id_votacao: renova os votos das
            # votações deste lote sem apagar votos de execuções anteriores.
            resumo["fato_votos"] = self.banco.carregar_incremental_assoc(
                df_votos, "fato_votos", coluna_fk="id_votacao"
            )

        except Exception as e:
            log.error(f"Falha em fato_votacoes: {e}")
            resumo["fato_votacoes"] = "ERRO"
            resumo["fato_votos"] = "ERRO"

        # --- Finaliza ---
        self.banco.desconectar()
        duracao = time.time() - inicio

        log.info("")
        log.info("ETAPA 3 CONCLUÍDA - Resumo de carga:")
        for tabela, qtd in resumo.items():
            status = f"{qtd} registros" if isinstance(qtd, int) else qtd
            log.info(f"  {tabela:35s}: {status}")
        log.info(f"  Duração total: {duracao:.1f}s")

        return resumo
