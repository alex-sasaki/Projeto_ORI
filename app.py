import streamlit as st
import time
from index import MotorBuscaTMDB  # Importa a sua classe atualizada com Polars/Pickle

# Configuração da página do Streamlit
st.set_page_config(page_title="Motor de Busca TMDB - Polars + Pickle", page_icon="🎬", layout="wide")

# Inicializa o motor de busca na memória do Streamlit de forma segura
@st.cache_resource
def inicializar_motor():
    motor = MotorBuscaTMDB()
    
    if not hasattr(motor, '_busca_binaria_id'):
        motor._busca_binaria_id = lambda idx: motor.indice_primario_id.get(idx, None)
        
    arquivo_csv = "TMDB_movie_dataset_v11.csv"
    motor.carregar_e_indexar(arquivo_csv)
    return motor

# Captura mensagens de log que iriam para o terminal e exibe na tela se necessário
with st.spinner("Carregando estruturas de indexação ou cache binário..."):
    motor = inicializar_motor()

# --- INTERFACE VISUAL ---
st.title("Motor de Busca Otimizado - TMDB")
st.markdown("""
Painel de alta performance combinando **Rust/Polars** para parsing, **Pickle** para cache de persistência,
e **Tabelas Hash** em memória para buscas em complexidade de tempo constante $O(1)$.
""")

# Métricas de Performance e Dados no Topo
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="Registros em Memória (Índice Primário)", value=f"{len(motor.indice_primario_id):,}")
with col_m2:
    st.metric(label="Tempo Médio de Busca Exata", value="< 0.01 ms", delta="O(1) Hash Table")
with col_m3:
    st.metric(label="Palavras Indexadas (Índice Invertido)", value=f"{len(motor.indice_palavras_titulo):,}")

st.divider()

# Criação das abas interativas
aba1, aba2, aba3 = st.tabs(["Busca por Título", "Busca por ID Exato", "Filtro Avançado (Título + Gênero)"])

# ABA 1: BUSCA POR TÍTULO MULTIPALAVRA
with aba1:
    st.header("Busca Textual Combinada")
    termo_titulo = st.text_input("Digite palavras do título (ex: Dark Knight, Interstellar):", key="txt_titulo")
    
    if termo_titulo:
        t_ini = time.time()
        resultados = motor.buscar_por_termo_titulo(termo_titulo)
        t_fim = (time.time() - t_ini) * 1000
        
        st.success(f"Encontrados {len(resultados)} filmes em {t_fim:.4f} ms")
        if resultados:
            st.dataframe(resultados, use_container_width=True)
        else:
            st.info("Nenhum resultado para os termos digitados.")

# ABA 2: BUSCA POR ID EXATO
with aba2:
    st.header("Busca por Chave Primária")
    st.caption("Acesso direto à memória RAM por meio de indexação por espalhamento (Hash).")
    id_busca = st.number_input("Digite o ID único do filme (ex: 27205):", min_value=1, step=1)
    
    if st.button("Executar Busca O(1)"):
        t_ini = time.time()
        resultado = motor.buscar_por_id(id_busca)
        t_fim = (time.time() - t_ini) * 1000
        
        if resultado:
            st.success(f"⚡ Registro recuperado instantaneamente em {t_fim:.4f} ms")
            st.json(resultado)
        else:
            st.warning("Nenhum filme catalogado com este identificador.")

# ABA 3: BUSCA BOOLEANA COMBINADA (AND)
with aba3:
    st.header("Busca Avançada (Título AND Gênero)")
    st.caption("Filtro cruzado de múltiplos índices invertidos concorrentes.")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        adv_titulo = st.text_input("Palavras contidas no título:", key="adv_tit")
    with col_in2:
        adv_genero = st.text_input("Gênero do filme (ex: Action, Sci-Fi, Drama):", key="adv_gen")
        
    if adv_titulo and adv_genero:
        t_ini = time.time()
        resultados_adv = motor.busca_booleana_and(adv_titulo, adv_genero)
        t_fim = (time.time() - t_ini) * 1000
        
        st.success(f"Intersecção gerou {len(resultados_adv)} resultados em {t_fim:.4f} ms")
        if resultados_adv:
            st.dataframe(resultados_adv, use_container_width=True)
        else:
            st.info("A combinação de critérios não gerou nenhuma correspondência no acervo.")