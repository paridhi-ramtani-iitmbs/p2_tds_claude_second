"""
Quiz page parser - Fast and simple
"""
from bs4 import BeautifulSoup
import re
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class QuizParser:
    """Parse quiz pages quickly"""
    
    def parse_quiz_page(self, page_content: dict, base_url: str) -> Dict[str, Any]:
        """Parse quiz page"""
        html = page_content['html']
        text = page_content['text']
        
        soup = BeautifulSoup(html, 'html.parser')
        
        question = self._extract_question(soup, text)
        data_source = self._extract_data_source(page_content, base_url)
        task_type = self._identify_task_type(question)
        submit_url = self._extract_submit_url(page_content, base_url)
        
        return {
            'question': question,
            'data_source': data_source,
            'task_type': task_type,
            'submit_url': submit_url,
            'raw_text': text,
            'base_url': base_url
        }
    
    def _extract_question(self, soup: BeautifulSoup, text: str) -> str:
        """Extract question"""
        for selector in ['h1', 'h2', '.question', '#question']:
            element = soup.select_one(selector)
            if element and len(element.get_text().strip()) > 20:
                return element.get_text().strip()
        
        return text[:500] if text else ""
    
    def _extract_data_source(self, page_content: dict, base_url: str) -> Dict[str, Any]:
        """Extract data source"""
        file_links = page_content.get('file_links', [])
        
        if file_links:
            for link in file_links:
                href = link['href']
                if '.csv' in href.lower():
                    return {'type': 'csv', 'url': href}
            
            for link in file_links:
                href = link['href']
                if any(ext in href.lower() for ext in ['.xlsx', '.xls']):
                    return {'type': 'excel', 'url': href}
            
            for link in file_links:
                href = link['href']
                if '.json' in href.lower():
                    return {'type': 'json', 'url': href}
            
            return {'type': 'file', 'url': file_links[0]['href']}
        
        text = page_content['text']
        if self._looks_like_csv(text):
            return {'type': 'inline_csv', 'data': text}
        
        if self._looks_like_json(text):
            return {'type': 'inline_json', 'data': text}
        
        return {'type': 'none', 'url': base_url}
    
    def _identify_task_type(self, question: str) -> str:
        """Identify task type"""
        q = question.lower()
        
        if any(w in q for w in ['sum', 'total', 'add up']):
            return 'sum'
        if any(w in q for w in ['count', 'how many', 'number of']):
            return 'count'
        if any(w in q for w in ['average', 'mean', 'avg']):
            return 'average'
        if any(w in q for w in ['filter', 'find', 'where']):
            return 'filter'
        if any(w in q for w in ['group', 'by category']):
            return 'groupby'
        if any(w in q for w in ['maximum', 'max', 'highest']):
            return 'max'
        if any(w in q for w in ['minimum', 'min', 'lowest']):
            return 'min'
        if any(w in q for w in ['sort', 'order', 'rank']):
            return 'sort'
        
        return 'general'
    
    def _extract_submit_url(self, page_content: dict, base_url: str) -> str:
        """Extract submit URL"""
        submit_info = page_content.get('submit_info', {})
        forms = submit_info.get('forms', [])
        
        if forms and forms[0].get('action'):
            action = forms[0]['action']
            if action.startswith('http'):
                return action
            else:
                from urllib.parse import urljoin
                return urljoin(base_url, action)
        
        from urllib.parse import urljoin
        return urljoin(base_url, '/submit')
    
    def _looks_like_csv(self, text: str) -> bool:
        """Check if CSV"""
        lines = text.strip().split('\n')[:5]
        if len(lines) < 2:
            return False
        comma_counts = [line.count(',') for line in lines]
        return len(set(comma_counts)) == 1 and comma_counts[0] > 0
    
    def _looks_like_json(self, text: str) -> bool:
        """Check if JSON"""
        text = text.strip()
        return (text.startswith('{') or text.startswith('[')) and \
               (text.endswith('}') or text.endswith(']'))
