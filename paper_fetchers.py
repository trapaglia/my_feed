import arxiv
import requests
from datetime import datetime, timedelta
from paper_storage import update_source_papers

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
    [Próximamente] Obtiene papers de Google Scholar
    """
    return []

def fetch_twitter_papers():
    """
    [Próximamente] Obtiene papers mencionados por investigadores relevantes en Twitter/X
    """
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