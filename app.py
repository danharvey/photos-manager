"""
Photos Manager - Flask service for Apple Photos analytics and automation

This service provides analytics and automation features for Apple Photos
using the OSXPhotos library. It works on both macOS and Linux.
"""

from flask import Flask, jsonify
from datetime import datetime
from collections import defaultdict
import sys

# OSXPhotos is optional and may not be available on all systems
try:
    import osxphotos
    OSXPHOTOS_AVAILABLE = True
except ImportError:
    osxphotos = None
    OSXPHOTOS_AVAILABLE = False


def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    if test_config:
        app.config.update(test_config)
    
    @app.route('/')
    def index():
        """Root endpoint with service information"""
        return jsonify({
            'service': 'Photos Manager',
            'version': '1.0.0',
            'osxphotos_available': OSXPHOTOS_AVAILABLE,
            'endpoints': {
                '/': 'Service information',
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
            'status': 'healthy',
            'osxphotos_available': OSXPHOTOS_AVAILABLE
        })
    
    @app.route('/analytics')
    def analytics():
        """Get comprehensive analytics from Apple Photos"""
        if not OSXPHOTOS_AVAILABLE:
            return jsonify({
                'error': 'OSXPhotos library not available',
                'message': 'This service requires OSXPhotos to be installed'
            }), 503
        
        try:
            photosdb = osxphotos.PhotosDB()
            photos = photosdb.photos()
            
            total_photos = len(photos)
            total_size = sum(p.original_filesize or 0 for p in photos)
            
            # Count photos by year
            by_year = defaultdict(int)
            for photo in photos:
                if photo.date:
                    year = photo.date.year
                    by_year[year] += 1
            
            # Count photos by month (last 12 months)
            by_month = defaultdict(int)
            for photo in photos:
                if photo.date:
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
        if not OSXPHOTOS_AVAILABLE:
            return jsonify({
                'error': 'OSXPhotos library not available'
            }), 503
        
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
        if not OSXPHOTOS_AVAILABLE:
            return jsonify({
                'error': 'OSXPhotos library not available'
            }), 503
        
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
        if not OSXPHOTOS_AVAILABLE:
            return jsonify({
                'error': 'OSXPhotos library not available'
            }), 503
        
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
