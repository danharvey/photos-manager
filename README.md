# Photos Manager

A Flask-based service for managing and analyzing Apple Photos libraries with automation capabilities not available directly in the Photos app.

## Features

- **Analytics Dashboard**: Get insights into your photo library
  - Total photo counts
  - Photos organized by year and month
  - Storage size analysis
  - Average photo sizes
- **Cross-Platform**: Works on both macOS and Linux
- **RESTful API**: Easy-to-use JSON API endpoints
- **OSXPhotos Integration**: Leverages the powerful OSXPhotos library for Apple Photos access

## Requirements

- Python 3.9 or higher
- OSXPhotos library (for Apple Photos access on macOS)
- Flask web framework

## Installation

1. Clone the repository:
```bash
git clone https://github.com/danharvey/photos-manager.git
cd photos-manager
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Service

Start the Flask server:
```bash
python app.py
```

The service will be available at `http://localhost:5000`

### API Endpoints

#### Get Service Information
```bash
GET /
```
Returns service information and available endpoints.

#### Health Check
```bash
GET /health
```
Returns the health status of the service.

#### Get Analytics Summary
```bash
GET /analytics
```
Returns comprehensive analytics including:
- Total photo count
- Total storage size (in bytes, MB, and GB)
- Photos grouped by year
- Photos grouped by month (last 12 months)

Example response:
```json
{
  "total_photos": 1500,
  "total_size_bytes": 5368709120,
  "total_size_mb": 5120.0,
  "total_size_gb": 5.0,
  "by_year": {
    "2022": 450,
    "2023": 600,
    "2024": 450
  },
  "by_month": {
    "2024-10": 50,
    "2024-09": 45,
    ...
  }
}
```

#### Get Photos by Month
```bash
GET /analytics/by-month
```
Returns all photos grouped by month.

#### Get Photos by Year
```bash
GET /analytics/by-year
```
Returns all photos grouped by year.

#### Get Storage Size Information
```bash
GET /analytics/size
```
Returns detailed storage size information including averages.

## Development

### Running Tests

Run the test suite:
```bash
pytest test_app.py -v
```

### Testing with Different Python Versions

The project is tested against Python 3.9, 3.10, and 3.11 on both Ubuntu and macOS via GitHub Actions.

## Platform Notes

### macOS
On macOS, the service can access your Apple Photos library directly through OSXPhotos. Make sure you grant the necessary permissions when prompted.

### Linux
On Linux, OSXPhotos can still be used to access Photos libraries that have been copied from macOS or accessed via network shares.

## GitHub Actions

The project includes automated testing via GitHub Actions that runs tests on:
- Ubuntu Latest
- macOS Latest
- Python versions: 3.9, 3.10, 3.11

Tests run automatically on pushes and pull requests to the `main` and `develop` branches.

## Future Enhancements

- Photo tagging automation
- Duplicate detection
- Batch processing capabilities
- Advanced filtering options
- Export and backup automation
- Machine learning-based photo organization

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
