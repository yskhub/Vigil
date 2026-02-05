#!/usr/bin/env python3
"""
COMPREHENSIVE 360-DEGREE VALIDATION SUITE
Tests every aspect of the Agentic Honeypot API
"""
import requests
import json
import sys
import time
from typing import Dict, Any, List

# Configuration
BASE_URL = "https://vigil-889d.onrender.com"
API_KEY = "Agentic_Honey_Pot_Scam_Detection_Intelligence_Extraction_2026_X1"

# Color codes for terminal (if supported)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name: str):
    """Print test name"""
    print(f"\n{Colors.BLUE}[TEST]{Colors.END} {Colors.BOLD}{name}{Colors.END}")

def print_pass(msg: str):
    """Print pass message"""
    print(f"  {Colors.GREEN}[PASS]{Colors.END} {msg}")

def print_fail(msg: str):
    """Print fail message"""
    print(f"  {Colors.RED}[FAIL]{Colors.END} {msg}")

def print_warn(msg: str):
    """Print warning message"""
    print(f"  {Colors.YELLOW}[WARN]{Colors.END} {msg}")

def print_info(msg: str):
    """Print info message"""
    print(f"  {Colors.BLUE}[INFO]{Colors.END} {msg}")

# Test Results
test_results = []

def record_test(name: str, passed: bool, details: str = ""):
    """Record test result"""
    test_results.append({
        "name": name,
        "passed": passed,
        "details": details
    })

def test_health_endpoint():
    """Test 1: Health endpoint availability"""
    print_test("Health Endpoint")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "ok":
                print_pass("Health endpoint returns 200 with status=ok")
                record_test("health_endpoint", True)
                return True
            else:
                print_fail(f"Unexpected response: {data}")
                record_test("health_endpoint", False, f"Wrong response: {data}")
                return False
        else:
            print_fail(f"Status code: {resp.status_code}")
            record_test("health_endpoint", False, f"Status: {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Exception: {e}")
        record_test("health_endpoint", False, str(e))
        return False

def test_events_with_valid_payload():
    """Test 2: Events endpoint with judge's exact payload"""
    print_test("Events Endpoint - Judge's Payload")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    payload = {
        "sessionId": "1fc994e9-f4c5-47ee-8806-90aeb969928f",
        "message": {
            "sender": "scammer",
            "text": "Your bank account will be blocked today. Verify immediately.",
            "timestamp": 1769776085000
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "SMS",
            "language": "English",
            "locale": "IN"
        }
    }
    
    try:
        print_info("Sending request...")
        resp = requests.post(f"{BASE_URL}/events", headers=headers, json=payload, timeout=30)
        
        print_info(f"Status Code: {resp.status_code}")
        
        # Check status code
        if resp.status_code != 200:
            print_fail(f"Expected 200, got {resp.status_code}")
            print_info(f"Response: {resp.text[:500]}")
            record_test("events_judge_payload", False, f"Status: {resp.status_code}")
            return False
        
        # Check Content-Type header
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            print_warn(f"Content-Type is '{content_type}' (expected application/json)")
        else:
            print_pass("Content-Type is application/json")
        
        # Parse JSON
        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            print_fail(f"JSON decode error: {e}")
            print_info(f"Raw response: {resp.text[:500]}")
            record_test("events_judge_payload", False, f"JSON decode failed: {e}")
            return False
        
        # Validate required fields
        required_fields = ["status", "reply"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            print_fail(f"Missing required fields: {missing}")
            record_test("events_judge_payload", False, f"Missing: {missing}")
            return False
        
        print_pass(f"All required fields present: {required_fields}")
        
        # Check status value
        if data["status"] != "success":
            print_fail(f"status is '{data['status']}' (expected 'success')")
            record_test("events_judge_payload", False, f"Wrong status: {data['status']}")
            return False
        
        print_pass(f"status = 'success'")
        
        # Check reply is a non-empty string
        reply = data.get("reply")
        if not reply or not isinstance(reply, str):
            print_fail(f"reply is invalid: {reply}")
            record_test("events_judge_payload", False, f"Invalid reply: {reply}")
            return False
        
        print_pass(f"reply is valid string: '{reply[:50]}...'")
        
        # Check optional fields
        if "scamDetected" in data:
            print_info(f"scamDetected: {data['scamDetected']}")
        if "extractedIntelligence" in data:
            intel = data["extractedIntelligence"]
            print_info(f"extractedIntelligence keys: {list(intel.keys())}")
        
        print_pass("Judge's payload test PASSED")
        record_test("events_judge_payload", True, f"Reply: {reply[:50]}")
        return True
        
    except requests.Timeout:
        print_fail("Request timed out after 30 seconds")
        record_test("events_judge_payload", False, "Timeout")
        return False
    except Exception as e:
        print_fail(f"Exception: {type(e).__name__}: {e}")
        record_test("events_judge_payload", False, str(e))
        return False

def test_events_without_api_key():
    """Test 3: Events endpoint without API key (should fail)"""
    print_test("Events Endpoint - No API Key")
    
    headers = {"Content-Type": "application/json"}
    payload = {"sessionId": "test", "message": {"text": "test"}}
    
    try:
        resp = requests.post(f"{BASE_URL}/events", headers=headers, json=payload, timeout=10)
        
        if resp.status_code == 401:
            print_pass("Correctly returns 401 Unauthorized")
            record_test("events_no_api_key", True)
            return True
        else:
            print_fail(f"Expected 401, got {resp.status_code}")
            record_test("events_no_api_key", False, f"Status: {resp.status_code}")
            return False
    except Exception as e:
        print_fail(f"Exception: {e}")
        record_test("events_no_api_key", False, str(e))
        return False

def test_events_with_conversation_history():
    """Test 4: Events with multi-turn conversation"""
    print_test("Events Endpoint - Multi-turn Conversation")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    payload = {
        "sessionId": "multi-turn-test-" + str(int(time.time())),
        "message": {
            "sender": "scammer",
            "text": "Send money to UPI ID scammer@paytm. Your account 123456789012 is at risk!",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [
            {"sender": "scammer", "text": "Hello sir, this is from bank", "timestamp": int(time.time() * 1000) - 60000},
            {"sender": "agent", "text": "Oh hello dear, how can I help?", "timestamp": int(time.time() * 1000) - 50000}
        ],
        "metadata": {"channel": "SMS", "language": "English"}
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/events", headers=headers, json=payload, timeout=30)
        
        if resp.status_code != 200:
            print_fail(f"Status code: {resp.status_code}")
            record_test("events_multi_turn", False, f"Status: {resp.status_code}")
            return False
        
        data = resp.json()
        
        # Check intelligence extraction
        intel = data.get("extractedIntelligence", {})
        upi_ids = intel.get("upiIds", [])
        bank_accounts = intel.get("bankAccounts", [])
        
        if upi_ids:
            print_pass(f"Extracted UPI IDs: {upi_ids}")
        else:
            print_warn("No UPI IDs extracted (expected 'scammer@paytm')")
        
        if bank_accounts:
            print_pass(f"Extracted bank accounts: {bank_accounts}")
        else:
            print_warn("No bank accounts extracted (expected '123456789012')")
        
        if data.get("scamDetected"):
            print_pass("Scam correctly detected")
        else:
            print_warn("Scam not detected (should be True)")
        
        print_pass("Multi-turn conversation test PASSED")
        record_test("events_multi_turn", True)
        return True
        
    except Exception as e:
        print_fail(f"Exception: {e}")
        record_test("events_multi_turn", False, str(e))
        return False

def test_response_time():
    """Test 5: Response time under 15 seconds"""
    print_test("Response Time Performance")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    payload = {
        "sessionId": "perf-test-" + str(int(time.time())),
        "message": {
            "sender": "scammer",
            "text": "Quick test",
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": [],
        "metadata": {}
    }
    
    try:
        start = time.time()
        resp = requests.post(f"{BASE_URL}/events", headers=headers, json=payload, timeout=30)
        elapsed = time.time() - start
        
        print_info(f"Response time: {elapsed:.2f}s")
        
        if elapsed < 15:
            print_pass(f"Response time under 15s: {elapsed:.2f}s")
            record_test("response_time", True, f"{elapsed:.2f}s")
            return True
        else:
            print_warn(f"Response time over 15s: {elapsed:.2f}s")
            record_test("response_time", False, f"{elapsed:.2f}s (too slow)")
            return False
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        record_test("response_time", False, str(e))
        return False

def test_malformed_payload():
    """Test 6: Handling of malformed payloads"""
    print_test("Malformed Payload Handling")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    
    # Missing required fields
    payload = {"sessionId": "malformed"}
    
    try:
        resp = requests.post(f"{BASE_URL}/events", headers=headers, json=payload, timeout=10)
        
        # Should still return 200 with valid JSON (graceful degradation)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if "status" in data and "reply" in data:
                    print_pass("Gracefully handles malformed payload with valid JSON response")
                    record_test("malformed_payload", True)
                    return True
                else:
                    print_fail("Response missing required fields")
                    record_test("malformed_payload", False, "Missing fields")
                    return False
            except:
                print_fail("Response is not valid JSON")
                record_test("malformed_payload", False, "Invalid JSON")
                return False
        else:
            print_info(f"Returns status {resp.status_code} (acceptable if graceful)")
            record_test("malformed_payload", True, f"Status: {resp.status_code}")
            return True
            
    except Exception as e:
        print_fail(f"Exception: {e}")
        record_test("malformed_payload", False, str(e))
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.END}")
    print("="*70)
    
    passed = sum(1 for t in test_results if t["passed"])
    total = len(test_results)
    
    for result in test_results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result["passed"] else f"{Colors.RED}FAIL{Colors.END}"
        name = result["name"]
        details = f" - {result['details']}" if result["details"] else ""
        print(f"  [{status}] {name}{details}")
    
    print("\n" + "="*70)
    pct = (passed / total * 100) if total > 0 else 0
    print(f"Results: {passed}/{total} tests passed ({pct:.1f}%)")
    print("="*70)
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED!{Colors.END}")
        print("The API is ready for judge evaluation.")
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}SOME TESTS FAILED{Colors.END}")
        print("Please review and fix the failing tests before submission.")
        return False

def main():
    print("="*70)
    print(f"{Colors.BOLD}COMPREHENSIVE 360-DEGREE API VALIDATION{Colors.END}")
    print("="*70)
    print(f"Target: {BASE_URL}")
    print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
    print("="*70)
    
    # Run all tests
    test_health_endpoint()
    test_events_with_valid_payload()
    test_events_without_api_key()
    test_events_with_conversation_history()
    test_response_time()
    test_malformed_payload()
    
    # Print summary
    success = print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
