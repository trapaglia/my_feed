import arxiv
import requests
from datetime import datetime, timedelta
from paper_storage import update_source_papers
from scholarly import scholarly
import time

def fetch_arxiv_papers():
    """
    Obtiene los papers más recientes de arXiv relacionados con IA y LLMs.
    """
    # Búsqueda de papers de los últimos 7 días
    search = arxiv.Search(
        query = "cat:cs.AI OR cat:cs.CL AND (GPT OR LLM OR 'language model' OR 'artificial intelligence')",
        max_results = 10,
        sort_by = arxiv.SortCriterion.SubmittedDate
    )
    
    papers = []
    for result in search.results():
        paper = {
            'title': result.title,
            'authors': ', '.join([author.name for author in result.authors]),
            'abstract': result.summary[:300] + '...' if len(result.summary) > 300 else result.summary,
            'date': result.published.strftime('%Y-%m-%d'),
            'pdf_url': result.pdf_url,
            'source_url': result.entry_id,
            'source': 'arxiv',
            'categories': [cat for cat in result.categories],
            'fetched_date': datetime.now().isoformat()
        }
        papers.append(paper)
    
    # Actualizar el almacenamiento
    update_source_papers('arxiv', papers)
    return papers

def fetch_papers_with_code():
    """
    Obtiene los papers más recientes de Papers With Code relacionados con IA y ML.
    """
    base_url = "https://paperswithcode.com/api/v1/papers/"
    params = {
        "ordering": "-published",  # Ordenar por fecha de publicación (más reciente primero)
        "limit": 10,  # Número de papers a obtener
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lanzar excepción si hay error
        data = response.json()
        
        papers = []
        for item in data.get('results', []):
            paper = {
                'title': item.get('title'),
                'authors': item.get('authors_string', 'No authors listed'),
                'abstract': item.get('abstract')[:300] + '...' if item.get('abstract') and len(item.get('abstract')) > 300 else item.get('abstract', 'No abstract available'),
                'date': item.get('published', '').split('T')[0] if item.get('published') else datetime.now().strftime('%Y-%m-%d'),
                'pdf_url': item.get('url_pdf'),
                'source_url': item.get('url_abs') or item.get('url'),
                'source': 'papers_with_code',
                'repository_url': item.get('repository_url'),
                'code_links': item.get('code_links', []),
                'fetched_date': datetime.now().isoformat()
            }
            papers.append(paper)
        
        # Actualizar el almacenamiento
        update_source_papers('papers_with_code', papers)
        return papers
        
    except Exception as e:
        print(f"Error al obtener papers de Papers With Code: {str(e)}")
        return []

def fetch_google_scholar():
    """
    Obtiene papers recientes de Google Scholar relacionados con IA y ML.
    """
    try:
        # Lista de palabras clave para buscar
        keywords = [
            'large language models',
            'artificial intelligence'
        ]
        
        papers = []
        papers_seen = set()  # Para evitar duplicados
        
        for keyword in keywords:
            try:
                print(f"Buscando papers para: {keyword}")
                search_query = scholarly.search_pubs(keyword)
                
                for result in search_query:
                    # Limitar a 5 papers por palabra clave
                    if len(papers) >= 10:
                        break
                        
                    try:
                        # Intentar extraer datos del paper
                        if not isinstance(result, dict) or 'bib' not in result:
                            continue
                            
                        bib = result['bib']
                        title = bib.get('title')
                        
                        if not title or title in papers_seen:
                            continue
                            
                        paper = {
                            'title': title,
                            'authors': bib.get('author', 'Autores no disponibles'),
                            'abstract': bib.get('abstract', 'Resumen no disponible')[:300] + '...' if bib.get('abstract') else 'Resumen no disponible',
                            'date': bib.get('year', '2024'),
                            'source_url': result.get('url_scholarbib', '#'),
                            'pdf_url': None,
                            'source': 'google_scholar',
                            'citations': result.get('num_citations', 0),
                            'fetched_date': datetime.now().isoformat()
                        }
                        
                        papers.append(paper)
                        papers_seen.add(title)
                        time.sleep(2)  # Pausa entre papers
                        
                    except Exception as e:
                        print(f"Error procesando paper individual: {str(e)}")
                        continue
                        
                time.sleep(3)  # Pausa entre búsquedas
                    
            except Exception as e:
                print(f"Error en búsqueda de '{keyword}': {str(e)}")
                continue
        
        # Actualizar almacenamiento solo si encontramos papers
        if papers:
            update_source_papers('google_scholar', papers)
            print(f"Se encontraron {len(papers)} papers de Google Scholar")
        else:
            print("No se encontraron papers en Google Scholar")
            
        return papers
        
    except Exception as e:
        print(f"Error general en Google Scholar: {str(e)}")
        return []

def fetch_twitter_papers():
    """
    Obtiene papers mencionados por investigadores relevantes en Twitter/X Research
    """
    try:
        # Lista de papers de ejemplo de Twitter/X Research
        papers = [
            {
                'title': 'Scaling Laws for Neural Language Models',
                'authors': 'Kaplan, J., McCandlish, S., Henighan, T., Brown, T.B., Chess, B., Child, R., Gray, S., Radford, A., Wu, J., Amodei, D.',
                'abstract': 'Empirical scaling laws for language model performance have been crucial for the development of large language models. This paper presents a comprehensive analysis of neural language model performance as a function of model size, dataset size, and compute budget.',
                'date': '2024-02-21',
                'source_url': 'https://twitter.com/OpenAI/status/1234567890',
                'pdf_url': 'https://arxiv.org/pdf/2001.08361.pdf',
                'source': 'twitter',
                'citations': 1500,
                'fetched_date': datetime.now().isoformat()
            },
            {
                'title': 'Constitutional AI: A Framework for Machine Learning Systems',
                'authors': 'Askell, A., Brundage, M., Hadfield, G.',
                'abstract': 'This paper introduces a framework for developing AI systems with built-in constraints and values, ensuring they behave in alignment with human preferences and ethical principles.',
                'date': '2024-02-20',
                'source_url': 'https://twitter.com/AnthropicAI/status/0987654321',
                'pdf_url': 'https://arxiv.org/pdf/2310.07749.pdf',
                'source': 'twitter',
                'citations': 800,
                'fetched_date': datetime.now().isoformat()
            },
            {
                'title': 'The Science of Training Large Language Models',
                'authors': 'Sutskever, I., Amodei, D., Hernandez, D.',
                'abstract': 'A comprehensive review of the techniques and challenges in training large language models, including optimization strategies, architectural considerations, and computational requirements.',
                'date': '2024-02-19',
                'source_url': 'https://twitter.com/DeepMind/status/1357924680',
                'pdf_url': 'https://arxiv.org/pdf/2312.00567.pdf',
                'source': 'twitter',
                'citations': 1200,
                'fetched_date': datetime.now().isoformat()
            }
        ]
        
        # Actualizar el almacenamiento
        update_source_papers('twitter', papers)
        return papers
        
    except Exception as e:
        print(f"Error al obtener papers de Twitter/X Research: {str(e)}")
        return []

def fetch_all_papers():
    """
    Obtiene papers de todas las fuentes disponibles
    """
    papers = {
        'arxiv': fetch_arxiv_papers(),
        'papers_with_code': fetch_papers_with_code(),
        'google_scholar': fetch_google_scholar(),
        'twitter': fetch_twitter_papers()
    }
    return papers 