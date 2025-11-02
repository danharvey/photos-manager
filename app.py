"""
Photos Manager - Flask service for Apple Photos analytics and automation

This service provides analytics and automation features for Apple Photos
using the OSXPhotos library. It works on both macOS and Linux.
"""

from flask import Flask, jsonify, render_template
from datetime import datetime
from collections import defaultdict
import sys

# Import OSXPhotos - this is required for the service to function
try:
    import osxphotos
except ImportError as e:
    print("ERROR: OSXPhotos library is required but not installed.", file=sys.stderr)
    print("Please install it with: pip install osxphotos", file=sys.stderr)
    sys.exit(1)


def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    if test_config:
        app.config.update(test_config)
    
    # Demo mode for testing UI without Photos library
    import os
    demo_mode = os.environ.get('DEMO_MODE', 'False').lower() in ('true', '1', 'yes')
    
    def get_demo_data():
        """Return mock data for demo mode"""
        return {
            'total_photos': 2450,
            'total_size_bytes': 12884901888,
            'total_size_mb': 12288.0,
            'total_size_gb': 12.0,
            'by_year': {
                '2020': 450,
                '2021': 520,
                '2022': 580,
                '2023': 600,
                '2024': 300
            },
            'by_month': {
                '2024-11': 45,
                '2024-10': 52,
                '2024-09': 48,
                '2024-08': 55,
                '2024-07': 50,
                '2024-06': 43,
                '2024-05': 47,
                '2024-04': 51,
                '2024-03': 49,
                '2024-02': 44,
                '2024-01': 46,
                '2023-12': 50
            }
        }
    
    @app.route('/')
    def index():
        """Serve the web UI dashboard"""
        return render_template('index.html')
    
    @app.route('/api')
    def api_info():
        """API endpoint with service information"""
        return jsonify({
            'service': 'Photos Manager',
            'version': '1.0.0',
            'endpoints': {
                '/': 'Web UI Dashboard',
                '/api': 'API information',
                '/health': 'Health check',
                '/analytics': 'Get analytics summary',
                '/analytics/by-month': 'Photos grouped by month',
                '/analytics/by-year': 'Photos grouped by year',
                '/analytics/size': 'Storage size information'
            }
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy'
        })
    
    @app.route('/analytics')
    def analytics():
        """Get comprehensive analytics from Apple Photos"""
        if demo_mode:
            return jsonify(get_demo_data())
        
        try:
            photosdb = osxphotos.PhotosDB()
            photos = photosdb.photos()
            
            total_photos = len(photos)
            total_size = 0
            by_year = defaultdict(int)
            by_month = defaultdict(int)
            
            # Single loop to calculate all metrics
            for photo in photos:
                # Sum file sizes
                if photo.original_filesize:
                    total_size += photo.original_filesize
                
                # Count by year and month
                if photo.date:
                    year = photo.date.year
                    by_year[year] += 1
                    
                    month_key = photo.date.strftime('%Y-%m')
                    by_month[month_key] += 1
            
            return jsonify({
                'total_photos': total_photos,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2),
                'by_year': dict(sorted(by_year.items())),
                'by_month': dict(sorted(by_month.items(), reverse=True)[:12])
            })
        except Exception as e:
            # Log the error for debugging but don't expose details to users
            app.logger.error(f"Analytics error: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve analytics',
                'message': 'An internal error occurred while processing your request'
            }), 500
    
    @app.route('/analytics/by-month')
    def analytics_by_month():
        """Get photos grouped by month"""
        try:
            photosdb = osxphotos.PhotosDB()
            photos = photosdb.photos()
            
            by_month = defaultdict(int)
            for photo in photos:
                if photo.date:
                    month_key = photo.date.strftime('%Y-%m')
                    by_month[month_key] += 1
            
            return jsonify({
                'by_month': dict(sorted(by_month.items(), reverse=True))
            })
        except Exception as e:
            app.logger.error(f"Monthly analytics error: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve monthly analytics',
                'message': 'An internal error occurred while processing your request'
            }), 500
    
    @app.route('/analytics/by-year')
    def analytics_by_year():
        """Get photos grouped by year"""
        try:
            photosdb = osxphotos.PhotosDB()
            photos = photosdb.photos()
            
            by_year = defaultdict(int)
            for photo in photos:
                if photo.date:
                    year = photo.date.year
                    by_year[year] += 1
            
            return jsonify({
                'by_year': dict(sorted(by_year.items()))
            })
        except Exception as e:
            app.logger.error(f"Yearly analytics error: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve yearly analytics',
                'message': 'An internal error occurred while processing your request'
            }), 500
    
    @app.route('/analytics/size')
    def analytics_size():
        """Get storage size information"""
        try:
            photosdb = osxphotos.PhotosDB()
            photos = photosdb.photos()
            
            total_size = sum(p.original_filesize or 0 for p in photos)
            
            # Calculate average size
            photos_with_size = [p for p in photos if p.original_filesize]
            avg_size = sum(p.original_filesize for p in photos_with_size) / len(photos_with_size) if photos_with_size else 0
            
            return jsonify({
                'total_photos': len(photos),
                'photos_with_size_info': len(photos_with_size),
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2),
                'average_size_bytes': round(avg_size, 2),
                'average_size_mb': round(avg_size / (1024 * 1024), 2)
            })
        except Exception as e:
            app.logger.error(f"Size analytics error: {str(e)}")
            return jsonify({
                'error': 'Failed to retrieve size analytics',
                'message': 'An internal error occurred while processing your request'
            }), 500
    
    return app


if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    app = create_app()
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
