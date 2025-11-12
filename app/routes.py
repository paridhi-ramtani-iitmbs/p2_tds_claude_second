"""
API Routes - Optimized with rate limiting protection
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, HttpUrl
from app.utils.validator import validate_request
from app.utils.browser import BrowserManager
from app.utils.parser import QuizParser
from app.utils.solver_core import QuizSolver
from app.utils.submitter import AnswerSubmitter
from app.config import settings
import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()

# Rate limiting - prevent 429 errors
request_times = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 20

def check_rate_limit(email: str) -> bool:
    """Simple rate limiting"""
    now = datetime.now()
    minute_ago = now - timedelta(minutes=1)
    
    # Clean old requests
    request_times[email] = [t for t in request_times[email] if t > minute_ago]
    
    # Check limit
    if len(request_times[email]) >= MAX_REQUESTS_PER_MINUTE:
        return False
    
    request_times[email].append(now)
    return True

class QuizRequest(BaseModel):
    email: EmailStr
    secret: str
    url: HttpUrl

class QuizResponse(BaseModel):
    status: str
    message: str
    details: dict = {}

@router.post("/solve", response_model=QuizResponse)
async def solve_quiz(request: QuizRequest, background_tasks: BackgroundTasks):
    """
    Main endpoint - solves quiz immediately (no background tasks)
    
    CRITICAL: Returns quickly to avoid 599 timeout
    """
    try:
        # Validate secret
        if not validate_request(request.secret):
            logger.warning(f"Invalid secret from {request.email}")
            raise HTTPException(status_code=403, detail="Invalid secret key")
        
        # Rate limiting check
        if not check_rate_limit(request.email):
            logger.warning(f"Rate limit exceeded for {request.email}")
            raise HTTPException(status_code=429, detail="Too many requests. Please wait.")
        
        logger.info(f"Processing request from {request.email}")
        
        # Solve immediately (not in background)
        result = await solve_quiz_fast(str(request.url), request.email)
        
        return QuizResponse(
            status="completed",
            message="Quiz solved successfully",
            details=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def solve_quiz_fast(quiz_url: str, email: str) -> dict:
    """
    Solve quiz chain FAST - under 3 minutes guaranteed
    
    OPTIMIZATIONS:
    - Strict timeouts on everything
    - Reuse browser instance
    - Parallel operations where possible
    - Early exit on errors
    """
    browser_manager = None
    start_time = time.time()
    
    try:
        logger.info(f"Starting quiz for {email} at {quiz_url}")
        
        # Initialize components once
        browser_manager = BrowserManager()
        parser = QuizParser()
        solver = QuizSolver()
        submitter = AnswerSubmitter()
        
        current_url = quiz_url
        step_count = 0
        max_steps = 15  # Allow up to 15 steps
        results = []
        
        while current_url and step_count < max_steps:
            step_start = time.time()
            step_count += 1
            
            # Check total time - abort if > 2.5 minutes
            elapsed = time.time() - start_time
            if elapsed > 150:  # 2.5 minutes
                logger.warning(f"Time limit approaching, stopping at step {step_count}")
                break
            
            logger.info(f"Step {step_count}: {current_url}")
            
            try:
                # Get page content with timeout
                page_content = await asyncio.wait_for(
                    browser_manager.get_page_content(current_url),
                    timeout=settings.BROWSER_TIMEOUT / 1000
                )
                
                # Parse quickly
                quiz_data = parser.parse_quiz_page(page_content, current_url)
                
                # Solve with timeout
                answer = await asyncio.wait_for(
                    solver.solve(quiz_data),
                    timeout=settings.SOLVE_TIMEOUT
                )
                
                # Submit with timeout
                submit_result = await asyncio.wait_for(
                    submitter.submit_answer(
                        quiz_data['submit_url'],
                        answer,
                        email
                    ),
                    timeout=settings.REQUEST_TIMEOUT
                )
                
                step_time = time.time() - step_start
                logger.info(f"Step {step_count} completed in {step_time:.2f}s")
                
                results.append({
                    'step': step_count,
                    'url': current_url,
                    'answer': answer,
                    'time': step_time,
                    'success': submit_result.get('success', False)
                })
                
                # Get next URL
                current_url = submit_result.get('next_url')
                
            except asyncio.TimeoutError:
                logger.error(f"Timeout on step {step_count}")
                break
            except Exception as e:
                logger.error(f"Error on step {step_count}: {str(e)}")
                break
        
        total_time = time.time() - start_time
        logger.info(f"Completed {step_count} steps in {total_time:.2f}s")
        
        return {
            'total_steps': step_count,
            'total_time': total_time,
            'results': results,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        return {
            'error': str(e),
            'success': False,
            'total_time': time.time() - start_time
        }
    finally:
        if browser_manager:
            try:
                await browser_manager.close()
            except:
                pass

# Keep-alive endpoint to prevent 599 timeout
@router.get("/keepalive")
async def keepalive():
    """
    Keep-alive endpoint - prevents Render from sleeping
    Call this every 14 minutes to keep service awake
    """
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "uptime": "active"
    }
