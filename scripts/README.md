# Scripts

This directory contains utility scripts for development and deployment.

## Local Development (`local/`)
- `run_local_app.py` - Run FastAPI backend locally
- `start_local.sh` - Start serverless offline with environment variables
- `test_local.py` - Test local API endpoints

## Scanner Scripts
- `scan_all.py` - Run all AWS governance scanners
- `scan_all_buckets.py` - Scan all S3 buckets for compliance

## Usage

### Run Local Development Server
```bash
cd scripts/local
python3 run_local_app.py
```

### Run Scanners
```bash
python3 scripts/scan_all.py --region us-east-1
python3 scripts/scan_all_buckets.py --region us-east-1
```
