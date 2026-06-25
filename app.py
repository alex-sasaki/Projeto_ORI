import streamlit as st
import time
from index_hash import MotorBuscaTMDB  # Certifique-se de que o seu index.py está sem hash

# Configuração da página web do Streamlit
st.set_page_config(page_title="Índice de Filmes TMDB", page_icon="🎬", layout="wide")

# Inicializa o motor de busca na memória do Streamlit
@st.cache_resource
def inicializar_motor():
    motor = MotorBuscaTMDB()
    # O arquivo deve estar na mesma pasta ORI no VS Code
    motor.carregar_e_indexar("TMDB_movie_dataset_v11.csv")
    return motor

try:
    motor = inicializar_motor()
except FileNotFoundError:
    st.error("Arquivo 'TMDB_movie_dataset_v11.csv' não encontrado na pasta local. Adicione o arquivo para iniciar.")
    st.stop()

# --- INTERFACE VISUAL ---
st.title("🎬 Índice de Filmes TMDB")
st.markdown("""
Esta interface utiliza um **Índice Primário Sequencial Ordenado** (Busca Binária $O(\log n)$) 
e **Índices Secundários Invertidos** para a resolução de termos e categorias. *Estrutura 100% livre de Tabelas Hash.*
""")

# Métricas rápidas no topo para impressionar na apresentação
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.metric(label="Total de Filmes no Índice Primário", value=f"{len(motor.indice_primario_id):,}")
with col_m2:
    st.metric(label="Algoritmo de Busca de Chave", value="Busca Binária O(log n)")

st.divider()

# Criando abas para separar as operações de consulta
aba1, aba2, aba3 = st.tabs(["Busca por Título (Multipalavra)", "Busca por ID (Busca Binária)", "Busca Combinada (Título AND Gênero)"])

# ABA 1: BUSCA POR TÍTULO
with aba1:
    st.header("Busca Textual no Índice Invertido")
    st.caption("Mapeia os termos digitados, faz a intersecção dos ponteiros e recupera os dados via Busca Binária.")
    
    termo_titulo = st.text_input("Digite o título do filme (ex: Dark Knight, Star Wars):", key="txt_titulo")
    
    if termo_titulo:
        t_ini = time.time()
        resultados = motor.buscar_por_termo_titulo(termo_titulo)
        t_fim = (time.time() - t_ini) * 1000
        
        st.success(f"Encontrados {len(resultados)} filmes em {t_fim:.4f} ms")
        if resultados:
            st.dataframe(resultados, use_container_width=True)
        else:
            st.info("Nenhum filme corresponde a todas as palavras digitadas.")

# ABA 2: BUSCA POR ID
with aba2:
    st.header("Busca Binária no Índice Primário Ordenado")
    st.caption("Demonstração clássica do algoritmo de divisão e conquista cortando o espaço de busca pela metade a cada passo.")
    
    id_busca = st.number_input("Digite o ID numérico exato (ex: 27205):", min_value=1, step=1)
    
    if st.button("Executar Busca Binária"):
        t_ini = time.time()
        resultado = motor.buscar_por_id(id_busca)
        t_fim = (time.time() - t_ini) * 1000
        
        if resultado:
            st.success(f"Registro localizado em {t_fim:.4f} ms")
            # Apresenta os dados isolados de forma organizada
            st.json(resultado)
        else:
            st.warning("ID não localizado no arquivo indexado.")

# ABA 3: BUSCA BOOLEANA COMBINADA
with aba3:
    st.header("Intersecção de Listas Invertidas")
    st.caption("Combina restrições textuais com filtros de categorias cruzando conjuntos de ponteiros.")
    
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        adv_titulo = st.text_input("Palavras contidas no título:")
    with col_input2:
        adv_genero = st.text_input("Gênero exato (ex: Action, Adventure, Drama):")
        
    if adv_titulo and adv_genero:
        t_ini = time.time()
        resultados_adv = motor.busca_booleana_and(adv_titulo, adv_genero)
        t_fim = (time.time() - t_ini) * 1000
        
        st.success(f"{len(resultados_adv)} registros interceptados em {t_fim:.4f} ms")
        if resultados_adv:
            st.dataframe(resultados_adv, use_container_width=True)
        else:
            st.info("Nenhum registro atende simultaneamente aos critérios de Título AND Gênero.")