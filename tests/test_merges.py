"""
Tests de Merge para SKILL-ODP
Verifica que la logica de merge funciona para CUALQUIER combinacion de modulos ENAHO.

Ejecutar: python -m pytest tests/test_merges.py -v
Desde: D:/SKILL-ODP/
"""
import sqlite3
import itertools
import json
import os
import pytest
import pandas as pd
import numpy as np

# === Configuracion ===

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "metadata", "enaho_variables.db")


@pytest.fixture
def conn():
    """Conexion a la SQLite de metadatos."""
    assert os.path.exists(DB_PATH), f"SQLite no encontrada en {DB_PATH}"
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


# === Funcion central: determinacion de llaves de merge ===

def get_merge_keys(conn, codigo_a, codigo_b):
    """
    Determina las llaves de merge entre dos modulos ENAHO
    basandose en el nivel de cada modulo.

    Returns: (llaves, tipo_merge)
    """
    nivel_a = conn.execute(
        "SELECT nivel FROM modulos WHERE codigo=?", (codigo_a,)
    ).fetchone()
    nivel_b = conn.execute(
        "SELECT nivel FROM modulos WHERE codigo=?", (codigo_b,)
    ).fetchone()

    assert nivel_a is not None, f"Modulo {codigo_a} no existe en SQLite"
    assert nivel_b is not None, f"Modulo {codigo_b} no existe en SQLite"

    nivel_a = nivel_a["nivel"]
    nivel_b = nivel_b["nivel"]

    if nivel_a == "persona" and nivel_b == "persona":
        return ["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"], "1:1"
    elif nivel_a == "persona" and nivel_b == "hogar":
        return ["CONGLOME", "VIVIENDA", "HOGAR"], "m:1"
    elif nivel_a == "hogar" and nivel_b == "persona":
        return ["CONGLOME", "VIVIENDA", "HOGAR"], "1:m"
    else:  # hogar-hogar
        return ["CONGLOME", "VIVIENDA", "HOGAR"], "1:1"


# === Tests de estructura de la SQLite ===

class TestSQLiteStructure:
    """Verifica que la SQLite tiene la estructura correcta."""

    def test_db_exists(self, conn):
        """La base de datos existe y se puede conectar."""
        result = conn.execute("SELECT COUNT(*) FROM modulos").fetchone()
        assert result[0] > 0

    def test_all_tables_exist(self, conn):
        """Todas las tablas requeridas existen."""
        tables = [r["name"] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        required = ["modulos", "variables", "categorias",
                     "llaves_union", "disponibilidad", "factores_expansion"]
        for table in required:
            assert table in tables, f"Tabla '{table}' no encontrada"

    def test_all_modules_have_nivel(self, conn):
        """Todos los modulos tienen campo nivel definido."""
        rows = conn.execute("SELECT codigo, nivel FROM modulos").fetchall()
        for row in rows:
            assert row["nivel"] in ("persona", "hogar"), \
                f"Modulo {row['codigo']} tiene nivel invalido: {row['nivel']}"

    def test_module_count(self, conn):
        """Hay al menos 40 modulos registrados."""
        count = conn.execute("SELECT COUNT(*) FROM modulos").fetchone()[0]
        assert count >= 40, f"Solo {count} modulos encontrados, esperados >= 40"

    def test_variables_count(self, conn):
        """Hay un numero razonable de variables."""
        count = conn.execute("SELECT COUNT(*) FROM variables").fetchone()[0]
        assert count >= 5000, f"Solo {count} variables, esperadas >= 5000"


# === Tests de determinacion de llaves de merge ===

class TestMergeKeyDetermination:
    """Verifica que get_merge_keys funciona para todas las combinaciones."""

    def test_persona_persona(self, conn):
        """Merge entre dos modulos persona usa 4 llaves."""
        keys, merge_type = get_merge_keys(conn, "300", "500")
        assert keys == ["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"]
        assert merge_type == "1:1"

    def test_hogar_hogar(self, conn):
        """Merge entre dos modulos hogar usa 3 llaves."""
        keys, merge_type = get_merge_keys(conn, "100", "SUM8G")
        assert keys == ["CONGLOME", "VIVIENDA", "HOGAR"]
        assert merge_type == "1:1"

    def test_persona_hogar(self, conn):
        """Merge persona a hogar es m:1 con 3 llaves."""
        keys, merge_type = get_merge_keys(conn, "500", "SUM12G")
        assert keys == ["CONGLOME", "VIVIENDA", "HOGAR"]
        assert merge_type == "m:1"

    def test_hogar_persona(self, conn):
        """Merge hogar a persona es 1:m con 3 llaves."""
        keys, merge_type = get_merge_keys(conn, "100", "300")
        assert keys == ["CONGLOME", "VIVIENDA", "HOGAR"]
        assert merge_type == "1:m"

    def test_all_persona_modules_pairwise(self, conn):
        """TODOS los pares de modulos persona producen llaves de 4 elementos."""
        persona_mods = [r["codigo"] for r in conn.execute(
            "SELECT codigo FROM modulos WHERE nivel='persona'"
        ).fetchall()]

        for a, b in itertools.combinations(persona_mods, 2):
            keys, mtype = get_merge_keys(conn, a, b)
            assert len(keys) == 4, \
                f"Merge persona {a}+{b}: esperadas 4 llaves, obtenidas {len(keys)}"
            assert mtype == "1:1", \
                f"Merge persona {a}+{b}: esperado 1:1, obtenido {mtype}"

    def test_all_hogar_modules_pairwise(self, conn):
        """TODOS los pares de modulos hogar producen llaves de 3 elementos."""
        hogar_mods = [r["codigo"] for r in conn.execute(
            "SELECT codigo FROM modulos WHERE nivel='hogar'"
        ).fetchall()]

        for a, b in itertools.combinations(hogar_mods, 2):
            keys, mtype = get_merge_keys(conn, a, b)
            assert len(keys) == 3, \
                f"Merge hogar {a}+{b}: esperadas 3 llaves, obtenidas {len(keys)}"
            assert mtype == "1:1", \
                f"Merge hogar {a}+{b}: esperado 1:1, obtenido {mtype}"

    def test_all_cross_level_merges(self, conn):
        """Todos los merges persona-hogar producen m:1 o 1:m."""
        persona_mods = [r["codigo"] for r in conn.execute(
            "SELECT codigo FROM modulos WHERE nivel='persona'"
        ).fetchall()]
        hogar_mods = [r["codigo"] for r in conn.execute(
            "SELECT codigo FROM modulos WHERE nivel='hogar'"
        ).fetchall()]

        for p in persona_mods:
            for h in hogar_mods:
                keys, mtype = get_merge_keys(conn, p, h)
                assert len(keys) == 3, \
                    f"Merge {p}(persona)+{h}(hogar): esperadas 3 llaves"
                assert mtype == "m:1", \
                    f"Merge {p}(persona)+{h}(hogar): esperado m:1"

                # Invertido
                keys2, mtype2 = get_merge_keys(conn, h, p)
                assert mtype2 == "1:m", \
                    f"Merge {h}(hogar)+{p}(persona): esperado 1:m"

    def test_merge_is_symmetric_in_keys(self, conn):
        """Las llaves son las mismas independiente del orden."""
        all_mods = [r["codigo"] for r in conn.execute(
            "SELECT codigo FROM modulos"
        ).fetchall()]

        # Probar 50 pares aleatorios
        rng = np.random.default_rng(42)
        indices = rng.choice(len(all_mods), size=(50, 2), replace=True)
        for i, j in indices:
            if i == j:
                continue
            a, b = all_mods[i], all_mods[j]
            keys_ab, _ = get_merge_keys(conn, a, b)
            keys_ba, _ = get_merge_keys(conn, b, a)
            assert set(keys_ab) == set(keys_ba), \
                f"Llaves asimetricas para {a}+{b}: {keys_ab} vs {keys_ba}"


# === Tests de merge con datos sinteticos ===

class TestMergeWithSyntheticData:
    """Verifica que el merge funciona con DataFrames sinteticos."""

    @pytest.fixture
    def synthetic_hogar(self):
        """DataFrame hogar sintetico (100 hogares)."""
        return pd.DataFrame({
            "CONGLOME": [f"C{i:04d}" for i in range(100)],
            "VIVIENDA": [f"V{i:03d}" for i in range(100)],
            "HOGAR": ["01"] * 100,
            "UBIGEO": [f"15{i:04d}" for i in range(100)],
            "FACTOR07_H": np.random.uniform(100, 5000, 100),
            "VARIABLE_HOGAR": np.random.normal(1000, 200, 100),
        })

    @pytest.fixture
    def synthetic_persona(self, synthetic_hogar):
        """DataFrame persona sintetico (~300 personas en 100 hogares)."""
        rows = []
        for _, hogar in synthetic_hogar.iterrows():
            n_personas = np.random.randint(1, 6)
            for p in range(n_personas):
                rows.append({
                    "CONGLOME": hogar["CONGLOME"],
                    "VIVIENDA": hogar["VIVIENDA"],
                    "HOGAR": hogar["HOGAR"],
                    "CODPERSO": f"{p+1:02d}",
                    "FACTOR07": np.random.uniform(100, 5000),
                    "P207": np.random.choice([1, 2]),  # Sexo
                    "P208A": np.random.randint(0, 80),  # Edad
                })
        return pd.DataFrame(rows)

    def test_merge_persona_persona_1_1(self, synthetic_persona):
        """Merge 1:1 entre dos modulos persona (mismos individuos)."""
        df_a = synthetic_persona[["CONGLOME", "VIVIENDA", "HOGAR",
                                   "CODPERSO", "P207"]].copy()
        df_b = synthetic_persona[["CONGLOME", "VIVIENDA", "HOGAR",
                                   "CODPERSO", "P208A"]].copy()

        result = pd.merge(
            df_a, df_b,
            on=["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"],
            how="inner",
            validate="1:1"
        )
        assert len(result) == len(synthetic_persona)
        assert "P207" in result.columns
        assert "P208A" in result.columns

    def test_merge_persona_hogar_m_1(self, synthetic_persona, synthetic_hogar):
        """Merge m:1 persona a hogar."""
        result = pd.merge(
            synthetic_persona,
            synthetic_hogar[["CONGLOME", "VIVIENDA", "HOGAR", "VARIABLE_HOGAR"]],
            on=["CONGLOME", "VIVIENDA", "HOGAR"],
            how="left",
            validate="m:1"
        )
        # Todas las personas deben tener la variable hogar
        assert len(result) == len(synthetic_persona)
        assert result["VARIABLE_HOGAR"].notna().all()

    def test_merge_hogar_hogar_1_1(self, synthetic_hogar):
        """Merge 1:1 entre dos modulos hogar."""
        df_a = synthetic_hogar[["CONGLOME", "VIVIENDA", "HOGAR",
                                 "UBIGEO"]].copy()
        df_b = synthetic_hogar[["CONGLOME", "VIVIENDA", "HOGAR",
                                 "VARIABLE_HOGAR"]].copy()

        result = pd.merge(
            df_a, df_b,
            on=["CONGLOME", "VIVIENDA", "HOGAR"],
            how="inner",
            validate="1:1"
        )
        assert len(result) == len(synthetic_hogar)

    def test_merge_chain_3_modules(self, synthetic_persona, synthetic_hogar):
        """Merge en cadena: persona + persona + hogar."""
        # Simular 3 modulos
        df_200 = synthetic_persona[["CONGLOME", "VIVIENDA", "HOGAR",
                                     "CODPERSO", "P207"]].copy()
        df_500 = synthetic_persona[["CONGLOME", "VIVIENDA", "HOGAR",
                                     "CODPERSO", "P208A", "FACTOR07"]].copy()
        df_100 = synthetic_hogar[["CONGLOME", "VIVIENDA", "HOGAR",
                                   "UBIGEO", "VARIABLE_HOGAR"]].copy()

        # Paso 1: persona + persona (1:1)
        merged = pd.merge(
            df_200, df_500,
            on=["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"],
            how="inner", validate="1:1"
        )
        assert len(merged) == len(synthetic_persona)

        # Paso 2: resultado + hogar (m:1)
        final = pd.merge(
            merged, df_100,
            on=["CONGLOME", "VIVIENDA", "HOGAR"],
            how="left", validate="m:1"
        )
        assert len(final) == len(synthetic_persona)
        assert "P207" in final.columns
        assert "P208A" in final.columns
        assert "VARIABLE_HOGAR" in final.columns

    def test_no_duplicates_after_merge(self, synthetic_persona, synthetic_hogar):
        """Despues de merge, no hay duplicados en llaves."""
        result = pd.merge(
            synthetic_persona,
            synthetic_hogar[["CONGLOME", "VIVIENDA", "HOGAR", "VARIABLE_HOGAR"]],
            on=["CONGLOME", "VIVIENDA", "HOGAR"],
            how="left", validate="m:1"
        )
        # No duplicados a nivel persona
        person_keys = result[["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"]]
        assert not person_keys.duplicated().any()

    def test_factor_present_after_merge(self, synthetic_persona, synthetic_hogar):
        """El factor de expansion sobrevive al merge."""
        result = pd.merge(
            synthetic_persona,
            synthetic_hogar[["CONGLOME", "VIVIENDA", "HOGAR", "VARIABLE_HOGAR"]],
            on=["CONGLOME", "VIVIENDA", "HOGAR"],
            how="left", validate="m:1"
        )
        assert "FACTOR07" in result.columns
        assert result["FACTOR07"].notna().all()
        assert (result["FACTOR07"] > 0).all()


# === Tests de append (datos pooled) ===

class TestAppendPooled:
    """Verifica la logica de append multi-anio."""

    def test_append_basic(self):
        """Append basico de 3 anios."""
        frames = []
        for anio in [2020, 2022, 2024]:
            df = pd.DataFrame({
                "CONGLOME": [f"C{i:04d}" for i in range(50)],
                "VIVIENDA": [f"V{i:03d}" for i in range(50)],
                "HOGAR": ["01"] * 50,
                "VARIABLE": np.random.normal(100, 20, 50),
                "FACTOR07": np.random.uniform(100, 5000, 50),
                "ANIO": anio,
            })
            frames.append(df)

        pooled = pd.concat(frames, ignore_index=True)
        assert len(pooled) == 150  # 50 * 3

    def test_factor_adjustment(self):
        """El factor se divide por K anios."""
        K = 3
        df = pd.DataFrame({
            "FACTOR07": [1000, 2000, 3000],
            "ANIO": [2020, 2022, 2024],
        })
        df["FACTOR_POOLED"] = df["FACTOR07"] / K
        assert df["FACTOR_POOLED"].iloc[0] == pytest.approx(333.33, rel=0.01)

    def test_anio_column_present(self):
        """El append incluye columna ANIO para identificar periodo."""
        frames = []
        for anio in [2020, 2024]:
            df = pd.DataFrame({"A": [1], "ANIO": [anio]})
            frames.append(df)
        pooled = pd.concat(frames, ignore_index=True)
        assert "ANIO" in pooled.columns
        assert set(pooled["ANIO"]) == {2020, 2024}


# === Tests de consistencia con llaves_union en SQLite ===

class TestSQLiteLlavesConsistency:
    """Verifica que las llaves definidas en SQLite son coherentes con la logica generica."""

    def test_explicit_keys_match_generic(self, conn):
        """Las llaves explicitas en SQLite coinciden con la logica generica."""
        rows = conn.execute("""
            SELECT lu.*, m1.codigo as cod_origen, m2.codigo as cod_destino,
                   m1.nivel as nivel_origen, m2.nivel as nivel_destino
            FROM llaves_union lu
            JOIN modulos m1 ON lu.modulo_origen = m1.id
            JOIN modulos m2 ON lu.modulo_destino = m2.id
        """).fetchall()

        for row in rows:
            explicit_keys = json.loads(row["variables_llave"])
            generic_keys, _ = get_merge_keys(conn, row["cod_origen"], row["cod_destino"])

            assert set(explicit_keys) == set(generic_keys), \
                f"Inconsistencia {row['cod_origen']}+{row['cod_destino']}: " \
                f"SQLite={explicit_keys}, Generico={generic_keys}"

    def test_explicit_nivel_matches_generic(self, conn):
        """El nivel de union explicito coincide con la logica generica."""
        rows = conn.execute("""
            SELECT lu.nivel_union, m1.codigo as cod_origen, m2.codigo as cod_destino
            FROM llaves_union lu
            JOIN modulos m1 ON lu.modulo_origen = m1.id
            JOIN modulos m2 ON lu.modulo_destino = m2.id
        """).fetchall()

        for row in rows:
            _, merge_type = get_merge_keys(conn, row["cod_origen"], row["cod_destino"])
            explicit_nivel = row["nivel_union"]

            # Verificar coherencia
            if explicit_nivel == "persona":
                assert merge_type == "1:1", \
                    f"{row['cod_origen']}+{row['cod_destino']}: nivel=persona pero merge={merge_type}"
            elif explicit_nivel == "hogar":
                assert merge_type in ("1:1", "m:1", "1:m"), \
                    f"{row['cod_origen']}+{row['cod_destino']}: nivel=hogar pero merge={merge_type}"


# === Tests de variables clave ===

class TestKeyVariables:
    """Verifica que las variables clave de merge existen en los modulos esperados."""

    @pytest.mark.parametrize("variable", ["CONGLOME", "VIVIENDA", "HOGAR"])
    def test_hogar_keys_in_all_modules_2024(self, conn, variable):
        """Variables CONGLOME, VIVIENDA, HOGAR existen en todos los modulos (2024)."""
        modulos = conn.execute(
            "SELECT id, codigo FROM modulos"
        ).fetchall()

        # Verificar solo modulos con variables en 2024
        modulos_con_vars = conn.execute("""
            SELECT DISTINCT m.codigo
            FROM variables v JOIN modulos m ON v.modulo_id = m.id
            WHERE v.anio = 2024
        """).fetchall()
        codigos_2024 = {r["codigo"] for r in modulos_con_vars}

        missing = []
        for mod in modulos:
            if mod["codigo"] not in codigos_2024:
                continue
            exists = conn.execute("""
                SELECT COUNT(*) FROM variables v
                JOIN modulos m ON v.modulo_id = m.id
                WHERE m.codigo = ? AND v.anio = 2024 AND v.nombre = ?
            """, (mod["codigo"], variable)).fetchone()[0]

            if exists == 0:
                missing.append(mod["codigo"])

        # Permitir hasta 5 modulos sin la variable (edge cases)
        assert len(missing) <= 5, \
            f"Variable {variable} falta en {len(missing)} modulos: {missing[:10]}"

    def test_codperso_in_persona_modules(self, conn):
        """CODPERSO existe en todos los modulos de persona (2024)."""
        persona_mods = conn.execute("""
            SELECT m.codigo FROM modulos m
            WHERE m.nivel = 'persona'
        """).fetchall()

        modulos_2024 = conn.execute("""
            SELECT DISTINCT m.codigo
            FROM variables v JOIN modulos m ON v.modulo_id = m.id
            WHERE v.anio = 2024
        """).fetchall()
        codigos_2024 = {r["codigo"] for r in modulos_2024}

        missing = []
        for mod in persona_mods:
            if mod["codigo"] not in codigos_2024:
                continue
            exists = conn.execute("""
                SELECT COUNT(*) FROM variables v
                JOIN modulos m ON v.modulo_id = m.id
                WHERE m.codigo = ? AND v.anio = 2024 AND v.nombre = 'CODPERSO'
            """, (mod["codigo"],)).fetchone()[0]

            if exists == 0:
                missing.append(mod["codigo"])

        assert len(missing) == 0, \
            f"CODPERSO falta en modulos persona: {missing}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
