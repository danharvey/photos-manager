#!/bin/bash
# Simple script to run the Photos Manager service

echo "Starting Photos Manager service..."
echo "The service will be available at http://localhost:5000"
echo ""
echo "Available endpoints:"
echo "  GET /              - Service information"
echo "  GET /health        - Health check"
echo "  GET /analytics     - Analytics summary"
echo "  GET /analytics/by-month - Photos by month"
echo "  GET /analytics/by-year  - Photos by year"
echo "  GET /analytics/size     - Storage size info"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

python3 app.py
