from ..core.embedder import Embedder
from ..core.vectordb import VectorDB
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Dict, Any

def retrieve_relevant_chunks(query: str, embedder: Embedder, vectordb: VectorDB, user_role: str, top_k: int = 5):
    """
    Função orquestradora (Retriever) que recebe uma query e os serviços 
    (embedder, vectordb), aplica os filtros de segurança e retorna os chunks relevantes.
    """
    
    print(f"[RETRIEVER] --- Iniciando processo de busca (Cargo: {user_role}) ---")
    print(f"[RETRIEVER] Consulta recebida: '{query}'")
    print("[RETRIEVER] Gerando embedding da query...")
    
    try:
        query_embedding = embedder.embed([query])[0].tolist()
    except Exception as e:
        print(f"[ERRO RETRIEVER] Falha ao gerar embedding. Verifique se o método 'embed' existe: {e}")
        raise RuntimeError(f"Falha ao gerar embedding: {e}")

    security_filter = Filter(
        must=[
            FieldCondition(
                key="allowed_roles",
                match=MatchValue(value=user_role) 
            )
        ]
    )

    print(f"[RETRIEVER] Buscando top {top_k} resultados no Qdrant...")
    try:
        top_results = vectordb.search(
            query_embedding,
            top_k=top_k,
            query_filter=security_filter,
        )
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar no Qdrant: {e}")

    if not top_results:
        raise ValueError("Nenhum documento relevante foi encontrado com base na sua consulta e permissões de acesso.")
    
    print(f"[RETRIEVER] {len(top_results)} resultados encontrados.\n")

    # Recuperação Expandida (Retrieval Expansion)
    # Esta lista será o conjunto de chunks que terão o contexto expandido.
    chunks_a_expandir = top_results[:2] # Pega o Chunk Top 1 e o Chunk Top 2
    
    # Usa um dicionário para garantir que todos os chunks (principais + vizinhos) sejam únicos
    final_context_map = {hit['id']: hit for hit in chunks_a_expandir}
    
    # Lista de chunks que têm metadados suficientes para expansão
    chunks_to_expand = [
        hit for hit in chunks_a_expandir 
        if 'chunk_index' in hit and 'source' in hit and hit.get('chunk_index') is not None
    ]

    print(f"[RETRIEVER] Iniciando Expansão de Contexto para {len(chunks_to_expand)} chunks...")
    
    for hit in chunks_to_expand:
        source = hit.get('source')
        
        try:
            chunk_index = int(hit.get('chunk_index'))
        except (TypeError, ValueError):
            print(f"Aviso: chunk_index inválido no chunk ID {hit['id']}. Pulando expansão.")
            continue
            
        neighbor_indices = []
        
        # Vizinho anterior: index - 1. (O índice começa em 1, então o mínimo é 1)
        if chunk_index > 1:
            neighbor_indices.append(chunk_index - 1)
        
        # Vizinho posterior: index + 1
        neighbor_indices.append(chunk_index + 1)
        
        # Busca e adiciona os vizinhos
        for neighbor_index in neighbor_indices:
            neighbor_hits = vectordb.get_chunks_by_metadata(
                source=source, 
                chunk_index=neighbor_index,
                user_role=user_role # Filtro de segurança obrigatório
            )
            
            # Adiciona os vizinhos ao mapa (final_context_map)
            for neighbor in neighbor_hits:
                if neighbor['id'] not in final_context_map:
                    final_context_map[neighbor['id']] = neighbor
                    print(f"[RETRIEVER] -> Adicionado chunk vizinho (Index {neighbor_index}) do documento {source}.")

    # Retorna a lista final de chunks (principais + vizinhos)
    final_context_list = list(final_context_map.values())
    
    # Ordenar o contexto final por documento (source) e índice (index) para passar para o LLM
    final_context_list.sort(key=lambda x: (x.get('source', ''), x.get('chunk_index', 9999)))
    
    print(f"\nBusca concluída. {len(final_context_list)} chunks no contexto final (principais + vizinhos).\n")
    
    return final_context_list
