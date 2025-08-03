import os
import signal
import sys
import threading
from app import app

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Stopping Vision Dashboard...')
    # Stop all daemon threads
    for thread in threading.enumerate():
        if thread.daemon and thread != threading.current_thread():
            thread.join(timeout=1)
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting Vision Dashboard on http://0.0.0.0:{port}")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        # Use threaded=True and disable reloader for better signal handling
        app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print('\n🛑 Vision Dashboard stopped')
    finally:
        print('🔄 Cleaning up...')
        os._exit(0)
