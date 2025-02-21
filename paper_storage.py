import json
import os
from datetime import datetime

STORAGE_FILE = 'static/data/papers_database.json'
if not os.path.exists(STORAGE_FILE):
    STORAGE_FILE = '/home/matiasdanmansilla/projects/my_feed/static/data/papers_database.json'

def load_papers():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'last_update': None, 'papers': {'arxiv': [], 'papers_with_code': [], 'google_scholar': [], 'twitter': []}}
    return {'last_update': None, 'papers': {'arxiv': [], 'papers_with_code': [], 'google_scholar': [], 'twitter': []}}

def save_papers(papers_data):
    papers_data['last_update'] = datetime.now().isoformat()
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(papers_data, f, ensure_ascii=False, indent=2)

def update_source_papers(source, new_papers):
    papers_data = load_papers()
    papers_data['papers'][source] = new_papers
    save_papers(papers_data)
    return papers_data 