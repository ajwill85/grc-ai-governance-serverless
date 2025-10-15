"""
Lambda handler for API Gateway
Wraps the FastAPI application using Mangum
"""
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../webapp/backend'))

from mangum import Mangum
from app.main import app

# Wrap FastAPI with Mangum for Lambda
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """AWS Lambda handler function"""
    return handler(event, context)
