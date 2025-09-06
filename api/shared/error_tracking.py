import logging
import os
from functools import wraps
from flask import request, g
import uuid

logger = logging.getLogger(__name__)

# Optional Sentry integration
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

def init_sentry(app):
    """Initialize Sentry error tracking if available"""
    if not SENTRY_AVAILABLE:
        logger.warning("Sentry SDK not available - install with: pip install sentry-sdk[flask]")
        return
    
    sentry_dsn = os.getenv('SENTRY_DSN')
    if not sentry_dsn:
        logger.info("SENTRY_DSN not configured - skipping Sentry initialization")
        return
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FlaskIntegration(auto_enabling_integrations=False),
            SqlalchemyIntegration()
        ],
        traces_sample_rate=0.1,
        environment=os.getenv('FLASK_ENV', 'production')
    )
    logger.info("Sentry error tracking initialized")

def add_request_id():
    """Add unique request ID for tracking"""
    g.request_id = str(uuid.uuid4())[:8]

def capture_exception(error, context=None):
    """Capture exception with context"""
    extra_context = {
        'request_id': getattr(g, 'request_id', None),
        'endpoint': request.endpoint if request else None,
        'method': request.method if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None
    }
    
    if context:
        extra_context.update(context)
    
    # Log locally
    logger.error(f"Exception captured: {str(error)}", extra=extra_context, exc_info=True)
    
    # Send to Sentry if available
    if SENTRY_AVAILABLE:
        with sentry_sdk.configure_scope() as scope:
            for key, value in extra_context.items():
                if value is not None:
                    scope.set_tag(key, value)
            sentry_sdk.capture_exception(error)

def track_performance(operation_name):
    """Decorator to track operation performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"Performance: {operation_name} completed in {duration:.3f}s", 
                           extra={'operation': operation_name, 'duration': duration})
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Performance: {operation_name} failed after {duration:.3f}s", 
                           extra={'operation': operation_name, 'duration': duration})
                raise
                
        return wrapper
    return decorator