import csv
import collections
import re
import time

class MotorBuscaTMDB:
    def __init__(self):
        # Índice Primário (Hash Table)
        self.indice_primario_id = {}
        
        # Índices Secundários Invertidos
        self.indice_genero = collections.defaultdict(list)
        self.indice_palavras_titulo = collections.defaultdict(list)

    def _normalizar_texto(self, texto):
        """Pipeline de ORI: remove pontuação e padroniza em minúsculo."""
        if not texto: return ""
        return re.sub(r'[^\w\s]', '', texto).lower()

    def _extrair_ano(self, data_str):
        if not data_str or len(data_str) < 4: return "Desconhecido"
        return data_str[:4]

    def carregar_e_indexar(self, caminho_csv):
        print(f"Indexando arquivo do TMDB: {caminho_csv}")
        tempo_inicio = time.time()
        count = 0

        with open(caminho_csv, mode='r', encoding='utf-8') as arquivo:
            leitor = csv.DictReader(arquivo)
            
            for linha in leitor:
                try:
                    # Validação das colunas exatas do dataset do TMDB
                    if not linha['id'] or not linha['title']: 
                        continue

                    id_filme = int(linha['id'])
                    titulo = linha['title']
                    ano = self._extrair_ano(linha['release_date'])
                    nota = linha.get('vote_average', '0.0')
                    
                    # Separa a string de gêneros do TMDB (Ex: "Action, Adventure")
                    generos_lista = [g.strip() for g in linha['genres'].split(',') if g.strip()]

                    # Salva o registro estruturado
                    self.indice_primario_id[id_filme] = {
                        "id": id_filme,
                        "titulo": titulo,
                        "ano": ano,
                        "generos": generos_lista,
                        "nota": nota
                    }

                    # Alimenta o Índice Secundário Invertido de Gêneros
                    for genero in generos_lista:
                        self.indice_genero[genero.lower()].append(id_filme)

                    # Alimenta o Índice Secundário Invertido de Palavras do Título
                    palavras = self._normalizar_texto(titulo).split()
                    for palavra in palavras:
                        if not self.indice_palavras_titulo[palavra] or self.indice_palavras_titulo[palavra][-1] != id_filme:
                            self.indice_palavras_titulo[palavra].append(id_filme)

                    count += 1
                except Exception:
                    continue

        print(f"{count} filmes indexados em {time.time() - tempo_inicio:.2f} segundos.\n")

    def buscar_por_id(self, id_filme):
        return self.indice_primario_id.get(id_filme, None)

    def buscar_por_termo_titulo(self, termo):
        """Busca textual que aceita múltiplas palavras (Busca Booleana AND implícita)."""
        palavras_busca = self._normalizar_texto(termo).split()
        
        if not palavras_busca:
            return []
        
        # Pega a lista de IDs da primeira palavra para iniciar o conjunto de resultados
        primeira_palavra = palavras_busca[0]
        ids_finais = set(self.indice_palavras_titulo.get(primeira_palavra, []))
        
        # Faz a intersecção com as listas de IDs das próximas palavras
        for palavra in palavras_busca[1:]:
            ids_palavra_atual = set(self.indice_palavras_titulo.get(palavra, []))
            ids_finais = ids_finais.intersection(ids_palavra_atual)
            
            # Se em algum momento a intersecção ficar vazia, não há motivo para continuar
            if not ids_finais:
                break
                
        # Retorna os dados dos filmes correspondentes aos IDs filtrados
        return [self.indice_primario_id[idx] for idx in ids_finais]

    def busca_booleana_and(self, termo_titulo, genero):
        """Busca avançada: Múltiplas palavras no título AND um gênero específico."""
        palavras_busca = self._normalizar_texto(termo_titulo).split()
        genero_norm = genero.lower()
        
        # Pega os IDs do gênero selecionado para iniciar o nosso conjunto base
        ids_finais = set(self.indice_genero.get(genero_norm, []))
        
        # Se o gênero digitado não existir ou não tiver filmes, retorna vazio imediatamente
        if not ids_finais:
            return []
            
        # Faz a intersecção sucessiva com cada palavra digitada para o título
        for palavra in palavras_busca:
            ids_palavra = set(self.indice_palavras_titulo.get(palavra, []))
            ids_finais = ids_finais.intersection(ids_palavra)
            
            # Otimização: se o conjunto zerar, interrompe o loop mais cedo
            if not ids_finais:
                break
                
        # Retorna a lista com os dados dos filmes estruturados
        return [self.indice_primario_id[idx] for idx in ids_finais]

# --- MENU INTERATIVO ---
if __name__ == "__main__":
    motor = MotorBuscaTMDB()
    
    # Certifique-se de que o CSV descompactado está na mesma pasta ORI com este nome:
    arquivo_csv = "TMDB_movie_dataset_v11.csv"
    
    try:
        motor.carregar_e_indexar(arquivo_csv)
    except FileNotFoundError:
        print(f"❌ Arquivo '{arquivo_csv}' não encontrado na pasta local.")
        exit()

    while True:
        print("1. Buscar por ID | 2. Buscar por Título | 3. Busca por Título + Gênero) | 4. Sair")
        opcao = input("Escolha: ")
        
        if opcao == "1":
            idx = int(input("ID (ex: 27205): "))
            print(motor.buscar_por_id(idx))
        elif opcao == "2":
            termo = input("Palavra do título: ")
            for f in motor.buscar_por_termo_titulo(termo)[:5]:
                print(f"- {f['titulo']} ({f['ano']})")
        elif opcao == "3":
            termo = input("Palavra: ")
            gen = input("Gênero: ")
            for f in motor.busca_booleana_and(termo, gen)[:5]:
                print(f"- {f['titulo']} | Gêneros: {f['generos']}")
        elif opcao == "4":
            break