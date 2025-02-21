import arxiv
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
    [Próximamente] Obtiene papers de Papers With Code
    """
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