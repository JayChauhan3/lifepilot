"""
OpenTelemetry observability instrumentation
Provides distributed tracing, metrics, and structured logging
"""

import structlog
import time
import traceback
from typing import Dict, Any, Optional, Callable
from functools import wraps
from contextlib import asynccontextmanager, contextmanager
from opentelemetry import trace, metrics, baggage, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import SpanKind
from opentelemetry.propagate import set_global_textmap, extract
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
import asyncio

logger = structlog.get_logger()

class ObservabilityManager:
    """Manages OpenTelemetry instrumentation"""
    
    def __init__(self, service_name: str = "lifepilot-backend", service_version: str = "1.0.0"):
        self.service_name = service_name
        self.service_version = service_version
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        self.meter: Optional[metrics.Meter] = None
        
        # Metrics
        self.request_counter: Optional[metrics.Counter] = None
        self.request_duration: Optional[metrics.Histogram] = None
        self.error_counter: Optional[metrics.Counter] = None
        self.active_requests: Optional[metrics.UpDownCounter] = None
        
    def initialize(self, project_id: Optional[str] = None):
        """Initialize OpenTelemetry instrumentation"""
        try:
            # Create resource with service metadata
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": self.service_version,
                "service.instance.id": f"{self.service_name}-{int(time.time())}"
            })
            
            # Initialize tracing
            self.tracer_provider = TracerProvider(resource=resource)
            self.tracer = self.tracer_provider.get_tracer(__name__)
            
            
            trace.set_tracer_provider(self.tracer_provider)
            set_global_textmap(baggage.propagation.get_global_textmap())
            
            # Initialize metrics
            self.meter_provider = MeterProvider(resource=resource)
            self.meter = self.meter_provider.get_meter(__name__)
            
            
            metrics.set_meter_provider(self.meter_provider)
            
            # Create metrics instruments
            self._create_metrics()
            
            # Auto-instrument common libraries
            self._setup_auto_instrumentation()
            
            logger.info("OpenTelemetry initialized successfully", 
                       service=self.service_name, 
                       version=self.service_version)
            
        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry", error=str(e))
            # Don't raise - allow application to continue without observability
    
    def _create_metrics(self):
        """Create metric instruments"""
        if not self.meter:
            return
        
        self.request_counter = self.meter.create_counter(
            "http_requests_total",
            description="Total number of HTTP requests"
        )
        
        self.request_duration = self.meter.create_histogram(
            "http_request_duration_seconds",
            description="HTTP request duration in seconds"
        )
        
        self.error_counter = self.meter.create_counter(
            "errors_total",
            description="Total number of errors"
        )
        
        self.active_requests = self.meter.create_up_down_counter(
            "active_requests",
            description="Number of currently active requests"
        )
    
    def _setup_auto_instrumentation(self):
        """Set up automatic instrumentation"""
        try:
            # Note: These will be called from the main application
            # FastAPIInstrumentor.instrument()
            # HTTPXClientInstrumentor.instrument()
            # AsyncPGInstrumentor.instrument()
            pass
        except Exception as e:
            logger.warning("Failed to setup auto-instrumentation", error=str(e))
    
    def record_request(self, method: str, path: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        if self.request_counter:
            self.request_counter.add(
                1,
                {"method": method, "path": path, "status_code": str(status_code)}
            )
        
        if self.request_duration:
            self.request_duration.record(
                duration,
                {"method": method, "path": path, "status_code": str(status_code)}
            )
        
        if status_code >= 400 and self.error_counter:
            self.error_counter.add(
                1,
                {"type": "http_error", "status_code": str(status_code)}
            )
    
    def record_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Record error metrics"""
        if self.error_counter:
            attributes = {"type": error_type}
            if context:
                attributes.update(context)
            self.error_counter.add(1, attributes)
    
    def increment_active_requests(self, attributes: Optional[Dict[str, Any]] = None):
        """Increment active requests counter"""
        if self.active_requests:
            self.active_requests.add(1, attributes or {})
    
    def decrement_active_requests(self, attributes: Optional[Dict[str, Any]] = None):
        """Decrement active requests counter"""
        if self.active_requests:
            self.active_requests.add(-1, attributes or {})

# Global observability manager
observability = ObservabilityManager()

def trace_function(span_name: Optional[str] = None, kind: SpanKind = SpanKind.INTERNAL):
    """Decorator to trace function execution"""
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            return _trace_async_function(func, span_name, kind)
        else:
            return _trace_sync_function(func, span_name, kind)
    return decorator

def _trace_sync_function(func: Callable, span_name: Optional[str], kind: SpanKind):
    """Trace synchronous function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        name = span_name or f"{func.__module__}.{func.__name__}"
        
        with observability.tracer.start_as_current_span(name, kind=kind) as span:
            # Add function attributes
            span.set_attribute("function.name", func.__name__)
            span.set_attribute("function.module", func.__module__)
            
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                span.set_attribute("function.duration", duration)
                span.set_status(trace.Status(trace.StatusCode.OK))
                
                return result
            except Exception as e:
                span.set_status(trace.Status(
                    trace.StatusCode.ERROR,
                    description=str(e)
                ))
                span.record_exception(e)
                
                observability.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context={"function": name}
                )
                
                raise
    return wrapper

def _trace_async_function(func: Callable, span_name: Optional[str], kind: SpanKind):
    """Trace asynchronous function"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        name = span_name or f"{func.__module__}.{func.__name__}"
        
        with observability.tracer.start_as_current_span(name, kind=kind) as span:
            # Add function attributes
            span.set_attribute("function.name", func.__name__)
            span.set_attribute("function.module", func.__module__)
            
            try:
                start_time = time.time()
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                span.set_attribute("function.duration", duration)
                span.set_status(trace.Status(trace.StatusCode.OK))
                
                return result
            except Exception as e:
                span.set_status(trace.Status(
                    trace.StatusCode.ERROR,
                    description=str(e)
                ))
                span.record_exception(e)
                
                observability.record_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context={"function": name}
                )
                
                raise
    return wrapper

@contextmanager
def trace_context(span_name: str, attributes: Optional[Dict[str, Any]] = None):
    """Context manager for tracing arbitrary code blocks"""
    with observability.tracer.start_as_current_span(span_name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        try:
            yield span
        except Exception as e:
            span.set_status(trace.Status(
                trace.StatusCode.ERROR,
                description=str(e)
            ))
            span.record_exception(e)
            raise

@asynccontextmanager
async def trace_context_async(span_name: str, attributes: Optional[Dict[str, Any]] = None):
    """Async context manager for tracing arbitrary code blocks"""
    with observability.tracer.start_as_current_span(span_name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        try:
            yield span
        except Exception as e:
            span.set_status(trace.Status(
                trace.StatusCode.ERROR,
                description=str(e)
            ))
            span.record_exception(e)
            raise

def add_span_attribute(key: str, value: Any):
    """Add attribute to current span"""
    span = trace.get_current_span()
    if span:
        span.set_attribute(key, value)

def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Add event to current span"""
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes or {})

def get_trace_id() -> Optional[str]:
    """Get current trace ID"""
    span = trace.get_current_span()
    if span:
        span_context = span.get_span_context()
        return format(span_context.trace_id, "032x")
    return None

def get_span_id() -> Optional[str]:
    """Get current span ID"""
    span = trace.get_current_span()
    if span:
        span_context = span.get_span_context()
        return format(span_context.span_id, "016x")
    return None

class StructuredLogger:
    """Enhanced structured logger with observability integration"""
    
    @staticmethod
    def log_request(method: str, path: str, user_id: Optional[str] = None):
        """Log HTTP request with trace context"""
        trace_id = get_trace_id()
        span_id = get_span_id()
        
        logger.info(
            "HTTP request started",
            method=method,
            path=path,
            user_id=user_id,
            trace_id=trace_id,
            span_id=span_id
        )
    
    @staticmethod
    def log_response(method: str, path: str, status_code: int, duration: float):
        """Log HTTP response with trace context"""
        trace_id = get_trace_id()
        span_id = get_span_id()
        
        logger.info(
            "HTTP request completed",
            method=method,
            path=path,
            status_code=status_code,
            duration=duration,
            trace_id=trace_id,
            span_id=span_id
        )
    
    @staticmethod
    def log_agent_interaction(agent_name: str, action: str, user_id: Optional[str] = None):
        """Log agent interaction with trace context"""
        trace_id = get_trace_id()
        span_id = get_span_id()
        
        logger.info(
            "Agent interaction",
            agent=agent_name,
            action=action,
            user_id=user_id,
            trace_id=trace_id,
            span_id=span_id
        )
    
    @staticmethod
    def log_error(error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with trace context"""
        trace_id = get_trace_id()
        span_id = get_span_id()
        
        logger.error(
            "Error occurred",
            error_type=type(error).__name__,
            error_message=str(error),
            error_traceback=traceback.format_exc(),
            context=context or {},
            trace_id=trace_id,
            span_id=span_id
        )

# Initialize structured logger
structured_logger = StructuredLogger()
