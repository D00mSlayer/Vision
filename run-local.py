#!/usr/bin/env python3
"""
Simple local runner for Vision Dashboard
Run this directly on your local machine
"""
import os
import sys

# Set environment variables
os.environ['PORT'] = '5099'
os.environ['FLASK_DEBUG'] = 'true'
os.environ['SESSION_SECRET'] = 'local-dev-secret'

print("🚀 Starting Vision Dashboard locally...")
print(f"📍 Port: {os.environ['PORT']}")
print(f"🌐 Access at: http://localhost:{os.environ['PORT']}")
print("🛑 Press Ctrl+C to stop")
print()

# Import and run the app
try:
    from app import app
    port = int(os.environ.get('PORT', 5099))
    app.run(host='0.0.0.0', port=port, debug=True)
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("\nInstall dependencies first:")
    print("pip install flask pyyaml requests python-dotenv pymssql pyodbc")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n🛑 Vision Dashboard stopped")
    sys.exit(0)