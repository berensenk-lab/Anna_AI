# start_voice_server.py
"""
Standalone Voice Recognition Server Launcher
Run this ONCE before starting any agents
"""
from BASE.tools.internal.voice.X_voice_recognition_server import run_server

if __name__ == "__main__":
    print("="*60)
    print("VOICE RECOGNITION SERVER")
    print("="*60)
    print("This server must run before starting any agents")
    print("All agents will connect to this server for voice input")
    print("="*60)
    print()
    
    run_server()