#!/usr/bin/env python3

import urllib.request
import json
import time
import sys
from datetime import datetime

class HealthChecker:
    def __init__(self, base_url="http://localhost:4000", timeout=5):
        self.base_url = base_url
        self.timeout = timeout
        
    def print_status(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "ERROR" else "⚠️" if status == "WARNING" else "🔍"
        print(f"{timestamp} {status_icon} {message}")
    
    def make_request(self, url):
        """Make HTTP request and handle both JSON and text responses"""
        try:
            start_time = time.time()
            req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                response_data = response.read().decode('utf-8')
                response_time = round((time.time() - start_time) * 1000, 2)
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                
                if 'application/json' in content_type:
                    try:
                        data = json.loads(response_data)
                    except:
                        data = response_data  # Fallback to text if JSON parsing fails
                else:
                    data = response_data  # Keep as text for non-JSON responses
                
                return response.getcode(), response_time, data
                
        except Exception as e:
            return 0, 0, None
    
    def check_endpoint(self, endpoint, description, expected_status=200):
        url = f"{self.base_url}{endpoint}"
        
        status_code, response_time, data = self.make_request(url)
        
        if status_code == expected_status:
            self.print_status(f"{description} - HTTP {status_code} ({response_time}ms)", "SUCCESS")
            return True, response_time, data
        else:
            self.print_status(f"{description} - HTTP {status_code} (expected {expected_status})", "ERROR")
            return False, response_time, data
    
    def check_endpoint_content(self, endpoint, description, expected_string):
        """Check endpoint and verify content contains expected string"""
        success, response_time, data = self.check_endpoint(endpoint, description)
        
        if success:
            # Convert data to string for searching
            content = str(data)
            if expected_string in content:
                self.print_status(f"{description} - content verified", "SUCCESS")
                return True
            else:
                self.print_status(f"{description} - content missing '{expected_string}'", "WARNING")
                return False
        return False

    def wait_for_service(self, max_attempts=30):
        self.print_status("Waiting for service to be ready...", "INFO")
        
        for attempt in range(max_attempts):
            try:
                status_code, _, _ = self.make_request(f"{self.base_url}/health")
                if status_code == 200:
                    self.print_status("Service is ready!", "SUCCESS")
                    return True
            except:
                pass
            
            if attempt == max_attempts - 1:
                self.print_status("Service failed to start within timeout", "ERROR")
                return False
            
            time.sleep(1)
        
        return False
    
    def run_all_checks(self):
        self.print_status(f"Starting health check for {self.base_url}", "INFO")
        print("=" * 50)
        
        if not self.wait_for_service():
            return False
        
        print("\nRunning endpoint checks...")
        print("-" * 30)
        
        # Basic endpoint checks
        basic_checks = [
            ("/", "Main page"),
            ("/health", "Health endpoint"), 
            ("/metrics", "Metrics endpoint"),
            ("/memory-info", "Memory info endpoint"),
            ("/heavy", "CPU load endpoint"),
            ("/slow?delay=100", "Slow endpoint"),
            ("/debug-container", "Container debug endpoint"),
        ]
        
        successful_checks = 0
        
        for endpoint, description in basic_checks:
            success, _, _ = self.check_endpoint(endpoint, description)
            if success:
                successful_checks += 1
        
        # Content verification (only for JSON endpoints)
        print("\nContent verification...")
        print("-" * 30)
        
        content_checks = [
            ("/health", "Health status", "healthy"),
            ("/", "Main page message", "Привет"),
        ]
        
        content_successful = 0
        for endpoint, description, expected_content in content_checks:
            if self.check_endpoint_content(endpoint, description, expected_content):
                content_successful += 1
        
        # Summary
        print("\n" + "=" * 50)
        self.print_status(f"Endpoint checks: {successful_checks}/{len(basic_checks)} passed", 
                         "SUCCESS" if successful_checks == len(basic_checks) else "WARNING")
        self.print_status(f"Content checks: {content_successful}/{len(content_checks)} passed", 
                         "SUCCESS" if content_successful == len(content_checks) else "WARNING")
        
        overall_success = successful_checks == len(basic_checks)
        self.print_status(f"Overall: {'PASS' if overall_success else 'PARTIAL PASS'}", 
                         "SUCCESS" if overall_success else "WARNING")
        
        return overall_success

def main():
    base_url = "http://localhost:4000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    checker = HealthChecker(base_url)
    
    try:
        success = checker.run_all_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        checker.print_status("Health check interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        checker.print_status(f"Unexpected error: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()