import logging
import sys
from datetime import datetime
from functools import wraps
from flask import request, g
import json
import os

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request context if available
        try:
            if hasattr(g, 'request_id'):
                log_entry['request_id'] = g.request_id
            if request:
                log_entry['endpoint'] = request.endpoint
                log_entry['method'] = request.method
                log_entry['ip'] = request.remote_addr
        except RuntimeError:
            # Outside of request context
            pass
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'project_id'):
            log_entry['project_id'] = record.project_id
        if hasattr(record, 'operation'):
            log_entry['operation'] = record.operation
            
        return json.dumps(log_entry)

def setup_logging(app):
    """Configure structured logging for the application"""
    
    # Remove default handlers
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    # Create structured formatter
    formatter = StructuredFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers (console only for serverless)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # Configure root logger
    logging.getLogger().setLevel(logging.INFO)
    
    return app.logger

def log_operation(operation_name, user_id=None, project_id=None):
    """Decorator to log operations with context"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            
            extra = {'operation': operation_name}
            if user_id:
                extra['user_id'] = user_id
            if project_id:
                extra['project_id'] = project_id
                
            logger.info(f"Starting {operation_name}", extra=extra)
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {operation_name}", extra=extra)
                return result
            except Exception as e:
                logger.error(f"Failed {operation_name}: {str(e)}", extra=extra, exc_info=True)
                raise
                
        return wrapper
    return decorator