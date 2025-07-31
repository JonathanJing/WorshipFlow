#!/usr/bin/env python3
"""
Test script for the logger functionality
日志功能测试脚本

This script tests the logger in different scenarios to ensure it works correctly.
该脚本在不同场景下测试日志记录器以确保其正常工作。
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logger_standalone():
    """Test logger in standalone mode (outside Streamlit)"""
    print("🔍 Testing logger in standalone mode...")
    
    try:
        from logger import user_logger
        
        # Test basic logging
        user_logger.log_action('test_standalone', {'mode': 'standalone'}, 'testing')
        print("✅ Basic logging test passed")
        
        # Test specific action types
        user_logger.log_page_visit('test_page')
        print("✅ Page visit logging test passed")
        
        user_logger.log_error('test_error', 'This is a test error', {'context': 'testing'})
        print("✅ Error logging test passed")
        
        user_logger.log_ai_action('test_ai', 'gemini-2.5-flash', 'test_prompt', True, {'test': True})
        print("✅ AI action logging test passed")
        
        print("🎉 All standalone tests passed!")
        
    except Exception as e:
        print(f"❌ Standalone test failed: {e}")
        return False
    
    return True

def test_logger_with_mock_streamlit():
    """Test logger with mocked Streamlit context"""
    print("\n🔍 Testing logger with mocked Streamlit context...")
    
    try:
        # Mock session state
        class MockSessionState:
            def __init__(self):
                self._state = {'page': 'test_page'}
            
            def get(self, key, default=None):
                return self._state.get(key, default)
            
            def __contains__(self, key):
                return key in self._state
            
            def __setitem__(self, key, value):
                self._state[key] = value
            
            def __getitem__(self, key):
                return self._state[key]
        
        # Temporarily replace streamlit session_state
        import streamlit as st
        original_session_state = getattr(st, 'session_state', None)
        st.session_state = MockSessionState()
        
        from logger import user_logger
        
        # Test with mocked context
        user_logger.log_action('test_mock', {'mode': 'mock_streamlit'}, 'testing')
        print("✅ Mocked Streamlit context test passed")
        
        # Restore original session state
        if original_session_state:
            st.session_state = original_session_state
        
    except Exception as e:
        print(f"❌ Mocked Streamlit test failed: {e}")
        return False
    
    return True

def check_log_output():
    """Check if log files are created and contain valid JSON"""
    print("\n🔍 Checking log file output...")
    
    try:
        log_file = f"logs/user_actions_{datetime.now().strftime('%Y-%m-%d')}.log"
        
        if not os.path.exists(log_file):
            print(f"❌ Log file not found: {log_file}")
            return False
        
        print(f"✅ Log file exists: {log_file}")
        
        # Read and validate recent log entries
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("❌ Log file is empty")
            return False
        
        print(f"✅ Log file contains {len(lines)} entries")
        
        # Check recent entries for valid JSON
        recent_entries = lines[-10:]  # Last 10 entries
        valid_json_count = 0
        
        for line in recent_entries:
            try:
                if ' - INFO - {' in line:
                    # Extract JSON part
                    json_part = line.split(' - INFO - ')[1].strip()
                    import json
                    data = json.loads(json_part)
                    
                    # Validate required fields
                    required_fields = ['category', 'action', 'user_id', 'timestamp']
                    if all(field in data for field in required_fields):
                        valid_json_count += 1
                        
            except (json.JSONDecodeError, IndexError):
                continue
        
        print(f"✅ Found {valid_json_count} valid JSON log entries")
        
        if valid_json_count > 0:
            print("✅ Log format validation passed")
            
            # Show sample log entry
            print("\n📋 Sample log entry:")
            for line in reversed(recent_entries):
                if ' - INFO - {' in line:
                    json_part = line.split(' - INFO - ')[1].strip()
                    print(f"   {json_part}")
                    break
                    
            return True
        else:
            print("❌ No valid JSON entries found")
            return False
            
    except Exception as e:
        print(f"❌ Log file check failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting WorshipFlow Logger Tests")
    print("=" * 50)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    success = True
    
    # Run tests
    if not test_logger_standalone():
        success = False
    
    if not test_logger_with_mock_streamlit():
        success = False
    
    if not check_log_output():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Logger is working correctly.")
        print("\n💡 Tips:")
        print("- View logs in the 'logs/' directory")
        print("- Use log_analyzer.py to analyze log data")
        print("- In production, logs will also go to Google Cloud Logging")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())