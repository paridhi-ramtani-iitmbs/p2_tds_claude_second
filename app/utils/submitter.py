"""
Answer Submitter - FAST with retry logic
"""
import aiohttp
import json
import asyncio
from typing import Any, Dict
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class AnswerSubmitter:
    """Fast answer submitter"""
    
    async def submit_answer(self, submit_url: str, answer: Any, email: str) -> Dict:
        """
        Submit answer FAST with retries
        """
        payload = self._prepare_payload(answer, email)
        
        logger.info(f"Submitting to: {submit_url}")
        
        for attempt in range(settings.MAX_RETRIES):
            try:
                timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT)
                
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        submit_url,
                        json=payload,
                        headers={'Content-Type': 'application/json'}
                    ) as response:
                        
                        status = response.status
                        text = await response.text()
                        
                        logger.info(f"Response: {status}")
                        
                        if status == 200:
                            try:
                                data = json.loads(text)
                            except:
                                data = {'text': text}
                            
                            next_url = self._extract_next_url(data, text)
                            
                            return {
                                'success': True,
                                'status': status,
                                'response': data,
                                'next_url': next_url
                            }
                        
                        elif status >= 500:
                            # Server error - retry
                            if attempt < settings.MAX_RETRIES - 1:
                                await asyncio.sleep(1)
                                continue
                        
                        # Client error or final retry
                        return {
                            'success': False,
                            'status': status,
                            'error': text
                        }
                
            except asyncio.TimeoutError:
                logger.error(f"Timeout attempt {attempt + 1}")
                if attempt < settings.MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                return {'success': False, 'error': 'Timeout'}
            
            except Exception as e:
                logger.error(f"Submit error: {str(e)}")
                if attempt < settings.MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Max retries exceeded'}
    
    def _prepare_payload(self, answer: Any, email: str) -> Dict:
        """Prepare JSON payload"""
        return {
            'answer': answer,
            'email': email
        }
    
    def _extract_next_url(self, response_data: Dict, response_text: str) -> str:
        """Extract next quiz URL"""
        if isinstance(response_data, dict):
            for key in ['next_url', 'nextUrl', 'next', 'continue', 'next_task']:
                if key in response_data:
                    return response_data[key]
        
        # Search in text
        import re
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', response_text)
        
        if urls:
            quiz_urls = [u for u in urls if 'quiz' in u.lower() or 'task' in u.lower()]
            return quiz_urls[0] if quiz_urls else urls[0]
        
        return None
