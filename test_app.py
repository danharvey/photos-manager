"""
Tests for Photos Manager Flask application
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys

# Import the app
from app import create_app, OSXPHOTOS_AVAILABLE


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestBasicEndpoints:
    """Test basic endpoints without OSXPhotos"""
    
    def test_index(self, client):
        """Test the index endpoint"""
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['service'] == 'Photos Manager'
        assert data['version'] == '1.0.0'
        assert 'endpoints' in data
        assert 'osxphotos_available' in data
    
    def test_health(self, client):
        """Test the health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'osxphotos_available' in data


class TestAnalyticsWithoutOSXPhotos:
    """Test analytics endpoints when OSXPhotos is not available"""
    
    @patch('app.OSXPHOTOS_AVAILABLE', False)
    def test_analytics_without_osxphotos(self, client):
        """Test analytics endpoint returns error when OSXPhotos not available"""
        with patch('app.OSXPHOTOS_AVAILABLE', False):
            # Create a new app with the patched value
            test_app = create_app({'TESTING': True})
            test_client = test_app.test_client()
            
            response = test_client.get('/analytics')
            assert response.status_code == 503
            data = response.get_json()
            assert 'error' in data
    
    @patch('app.OSXPHOTOS_AVAILABLE', False)
    def test_analytics_by_month_without_osxphotos(self, client):
        """Test by-month endpoint returns error when OSXPhotos not available"""
        with patch('app.OSXPHOTOS_AVAILABLE', False):
            test_app = create_app({'TESTING': True})
            test_client = test_app.test_client()
            
            response = test_client.get('/analytics/by-month')
            assert response.status_code == 503
    
    @patch('app.OSXPHOTOS_AVAILABLE', False)
    def test_analytics_by_year_without_osxphotos(self, client):
        """Test by-year endpoint returns error when OSXPhotos not available"""
        with patch('app.OSXPHOTOS_AVAILABLE', False):
            test_app = create_app({'TESTING': True})
            test_client = test_app.test_client()
            
            response = test_client.get('/analytics/by-year')
            assert response.status_code == 503
    
    @patch('app.OSXPHOTOS_AVAILABLE', False)
    def test_analytics_size_without_osxphotos(self, client):
        """Test size endpoint returns error when OSXPhotos not available"""
        with patch('app.OSXPHOTOS_AVAILABLE', False):
            test_app = create_app({'TESTING': True})
            test_client = test_app.test_client()
            
            response = test_client.get('/analytics/size')
            assert response.status_code == 503


class TestAnalyticsWithMockedOSXPhotos:
    """Test analytics endpoints with mocked OSXPhotos data"""
    
    def create_mock_photo(self, date, filesize):
        """Create a mock photo object"""
        photo = Mock()
        photo.date = date
        photo.original_filesize = filesize
        return photo
    
    @patch('app.OSXPHOTOS_AVAILABLE', True)
    @patch('app.osxphotos')
    def test_analytics_endpoint(self, mock_osxphotos, client):
        """Test analytics endpoint with mocked data"""
        # Create mock photos
        mock_photos = [
            self.create_mock_photo(datetime(2023, 1, 15), 1024 * 1024),  # 1 MB
            self.create_mock_photo(datetime(2023, 2, 20), 2 * 1024 * 1024),  # 2 MB
            self.create_mock_photo(datetime(2024, 1, 10), 3 * 1024 * 1024),  # 3 MB
        ]
        
        mock_db = Mock()
        mock_db.photos.return_value = mock_photos
        mock_osxphotos.PhotosDB.return_value = mock_db
        
        with patch('app.OSXPHOTOS_AVAILABLE', True):
            with patch('app.osxphotos', mock_osxphotos):
                test_app = create_app({'TESTING': True})
                test_client = test_app.test_client()
                
                response = test_client.get('/analytics')
                assert response.status_code == 200
                data = response.get_json()
                
                assert data['total_photos'] == 3
                assert data['total_size_bytes'] == 6 * 1024 * 1024
                assert data['total_size_mb'] == 6.0
                assert 'by_year' in data
                assert 'by_month' in data
    
    @patch('app.OSXPHOTOS_AVAILABLE', True)
    @patch('app.osxphotos')
    def test_analytics_by_month_endpoint(self, mock_osxphotos, client):
        """Test by-month analytics endpoint"""
        mock_photos = [
            self.create_mock_photo(datetime(2023, 1, 15), 1024),
            self.create_mock_photo(datetime(2023, 1, 20), 1024),
            self.create_mock_photo(datetime(2023, 2, 10), 1024),
        ]
        
        mock_db = Mock()
        mock_db.photos.return_value = mock_photos
        mock_osxphotos.PhotosDB.return_value = mock_db
        
        with patch('app.OSXPHOTOS_AVAILABLE', True):
            with patch('app.osxphotos', mock_osxphotos):
                test_app = create_app({'TESTING': True})
                test_client = test_app.test_client()
                
                response = test_client.get('/analytics/by-month')
                assert response.status_code == 200
                data = response.get_json()
                
                assert 'by_month' in data
                assert data['by_month']['2023-01'] == 2
                assert data['by_month']['2023-02'] == 1
    
    @patch('app.OSXPHOTOS_AVAILABLE', True)
    @patch('app.osxphotos')
    def test_analytics_by_year_endpoint(self, mock_osxphotos, client):
        """Test by-year analytics endpoint"""
        mock_photos = [
            self.create_mock_photo(datetime(2022, 1, 15), 1024),
            self.create_mock_photo(datetime(2023, 1, 20), 1024),
            self.create_mock_photo(datetime(2023, 6, 10), 1024),
        ]
        
        mock_db = Mock()
        mock_db.photos.return_value = mock_photos
        mock_osxphotos.PhotosDB.return_value = mock_db
        
        with patch('app.OSXPHOTOS_AVAILABLE', True):
            with patch('app.osxphotos', mock_osxphotos):
                test_app = create_app({'TESTING': True})
                test_client = test_app.test_client()
                
                response = test_client.get('/analytics/by-year')
                assert response.status_code == 200
                data = response.get_json()
                
                assert 'by_year' in data
                # JSON converts integer keys to strings
                assert data['by_year']['2022'] == 1
                assert data['by_year']['2023'] == 2
    
    @patch('app.OSXPHOTOS_AVAILABLE', True)
    @patch('app.osxphotos')
    def test_analytics_size_endpoint(self, mock_osxphotos, client):
        """Test size analytics endpoint"""
        mock_photos = [
            self.create_mock_photo(datetime(2023, 1, 15), 1024 * 1024),
            self.create_mock_photo(datetime(2023, 2, 20), 2 * 1024 * 1024),
            self.create_mock_photo(datetime(2024, 1, 10), 3 * 1024 * 1024),
        ]
        
        mock_db = Mock()
        mock_db.photos.return_value = mock_photos
        mock_osxphotos.PhotosDB.return_value = mock_db
        
        with patch('app.OSXPHOTOS_AVAILABLE', True):
            with patch('app.osxphotos', mock_osxphotos):
                test_app = create_app({'TESTING': True})
                test_client = test_app.test_client()
                
                response = test_client.get('/analytics/size')
                assert response.status_code == 200
                data = response.get_json()
                
                assert data['total_photos'] == 3
                assert data['total_size_bytes'] == 6 * 1024 * 1024
                assert data['total_size_mb'] == 6.0
                assert 'average_size_bytes' in data
                assert 'average_size_mb' in data
    
    @patch('app.OSXPHOTOS_AVAILABLE', True)
    @patch('app.osxphotos')
    def test_analytics_with_photos_without_dates(self, mock_osxphotos, client):
        """Test analytics handles photos without dates gracefully"""
        mock_photos = [
            self.create_mock_photo(datetime(2023, 1, 15), 1024),
            self.create_mock_photo(None, 1024),  # Photo without date
        ]
        
        mock_db = Mock()
        mock_db.photos.return_value = mock_photos
        mock_osxphotos.PhotosDB.return_value = mock_db
        
        with patch('app.OSXPHOTOS_AVAILABLE', True):
            with patch('app.osxphotos', mock_osxphotos):
                test_app = create_app({'TESTING': True})
                test_client = test_app.test_client()
                
                response = test_client.get('/analytics')
                assert response.status_code == 200
                data = response.get_json()
                
                assert data['total_photos'] == 2
                # Only one photo has a date
                assert sum(data['by_year'].values()) == 1
    
    @patch('app.OSXPHOTOS_AVAILABLE', True)
    @patch('app.osxphotos')
    def test_analytics_with_photos_without_filesize(self, mock_osxphotos, client):
        """Test analytics handles photos without filesize gracefully"""
        mock_photos = [
            self.create_mock_photo(datetime(2023, 1, 15), 1024),
            self.create_mock_photo(datetime(2023, 2, 20), None),  # Photo without filesize
        ]
        
        mock_db = Mock()
        mock_db.photos.return_value = mock_photos
        mock_osxphotos.PhotosDB.return_value = mock_db
        
        with patch('app.OSXPHOTOS_AVAILABLE', True):
            with patch('app.osxphotos', mock_osxphotos):
                test_app = create_app({'TESTING': True})
                test_client = test_app.test_client()
                
                response = test_client.get('/analytics/size')
                assert response.status_code == 200
                data = response.get_json()
                
                assert data['total_photos'] == 2
                assert data['photos_with_size_info'] == 1
                assert data['total_size_bytes'] == 1024
    
    @patch('app.OSXPHOTOS_AVAILABLE', True)
    @patch('app.osxphotos')
    def test_analytics_error_handling(self, mock_osxphotos, client):
        """Test analytics endpoint handles errors gracefully"""
        mock_osxphotos.PhotosDB.side_effect = Exception("Database error")
        
        with patch('app.OSXPHOTOS_AVAILABLE', True):
            with patch('app.osxphotos', mock_osxphotos):
                test_app = create_app({'TESTING': True})
                test_client = test_app.test_client()
                
                response = test_client.get('/analytics')
                assert response.status_code == 500
                data = response.get_json()
                assert 'error' in data
                assert 'message' in data
