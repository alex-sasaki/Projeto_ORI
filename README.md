# Índice de Filmes TMDB

Resumo

- Projeto em Python que fornece uma interface (Streamlit) para indexação e busca sobre um dataset do TMDB (`TMDB_movie_dataset_v11.csv`). O sistema demonstra o uso de um índice primário e índices secundários invertidos para consultas por título, ID e buscas combinadas.

O que faz

- Indexa o CSV e cria:
  - Índice primário por `id` (acesso direto / busca por ID).
  - Índices secundários invertidos para palavras do título e gêneros.
- Permite:
  - Busca de múltiplas palavras em títulos (intersecção de listas invertidas).
  - Busca por ID (busca direta no índice primário).
  - Busca booleana combinada: título (palavras) AND gênero.

Requisitos mínimos

- Python 3.8+
- Pacotes: `streamlit` (instalar com `pip install streamlit`)

Como executar

1. Coloque o arquivo `TMDB_movie_dataset_v11.csv` na mesma pasta do projeto.
2. Instale dependências:

```bash
pip install streamlit
```

3. Execute a interface web:

```bash
streamlit run app.py
```
