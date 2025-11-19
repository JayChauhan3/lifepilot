#!/usr/bin/env python3

import os
import sys
import json
import requests
import time
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class RAGAPITester:
    """Comprehensive RAG API testing suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        
    def make_request(self, message: str, user_id: str, session_id: str = None) -> Dict[str, Any]:
        """Make a chat API request"""
        if not session_id:
            session_id = f"session_{int(time.time())}"
            
        payload = {
            "message": message,
            "user_id": user_id,
            "session_id": session_id
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def test_memory_storage_and_retrieval(self):
        """Test memory storage and retrieval functionality"""
        print("\n=== Testing Memory Storage & Retrieval ===")
        
        user_id = "memory_test_user"
        
        # Test 1: Store memory
        print("\n1. Storing memory...")
        memory_message = "Remember: I prefer working in the morning and I have a project deadline next Friday"
        response1 = self.make_request(memory_message, user_id, "memory_session_1")
        print(f"Response: {response1.get('reply', 'No reply')[:200]}...")
        
        # Test 2: Retrieve memory
        print("\n2. Retrieving stored memory...")
        retrieve_message = "What do you know about my work preferences?"
        response2 = self.make_request(retrieve_message, user_id, "memory_session_1")
        print(f"Response: {response2.get('reply', 'No reply')[:200]}...")
        
        # Test 3: Ask about deadline
        print("\n3. Asking about deadline...")
        deadline_message = "What deadlines do I have coming up?"
        response3 = self.make_request(deadline_message, user_id, "memory_session_1")
        print(f"Response: {response3.get('reply', 'No reply')[:200]}...")
        
        # Store results
        self.test_results.append({
            "test": "Memory Storage & Retrieval",
            "status": "completed",
            "responses": [response1, response2, response3]
        })
    
    def test_knowledge_retrieval(self):
        """Test knowledge retrieval functionality"""
        print("\n=== Testing Knowledge Retrieval ===")
        
        user_id = "knowledge_test_user"
        
        # Test 1: General knowledge query
        print("\n1. General knowledge query...")
        query1 = "What are the best practices for machine learning model development?"
        response1 = self.make_request(query1, user_id, "knowledge_session_1")
        print(f"Response: {response1.get('reply', 'No reply')[:200]}...")
        
        # Test 2: Specific technical question
        print("\n2. Specific technical question...")
        query2 = "How do I implement transformer attention mechanism?"
        response2 = self.make_request(query2, user_id, "knowledge_session_1")
        print(f"Response: {response2.get('reply', 'No reply')[:200]}...")
        
        # Test 3: Current trends
        print("\n3. Current trends query...")
        query3 = "What are the latest trends in AI and deep learning?"
        response3 = self.make_request(query3, user_id, "knowledge_session_1")
        print(f"Response: {response3.get('reply', 'No reply')[:200]}...")
        
        self.test_results.append({
            "test": "Knowledge Retrieval",
            "status": "completed", 
            "responses": [response1, response2, response3]
        })
    
    def test_planning_functionality(self):
        """Test planning functionality"""
        print("\n=== Testing Planning Functionality ===")
        
        user_id = "planning_test_user"
        
        # Test 1: Simple planning request
        print("\n1. Simple planning request...")
        plan1 = "Help me plan my week for better productivity"
        response1 = self.make_request(plan1, user_id, "planning_session_1")
        print(f"Response: {response1.get('reply', 'No reply')[:200]}...")
        
        # Test 2: Complex project planning
        print("\n2. Complex project planning...")
        plan2 = "I need to launch a new mobile app in 3 months. Create a detailed project plan"
        response2 = self.make_request(plan2, user_id, "planning_session_1")
        print(f"Response: {response2.get('reply', 'No reply')[:200]}...")
        
        # Test 3: Daily planning
        print("\n3. Daily planning...")
        plan3 = "Help me organize my day tomorrow"
        response3 = self.make_request(plan3, user_id, "planning_session_1")
        print(f"Response: {response3.get('reply', 'No reply')[:200]}...")
        
        self.test_results.append({
            "test": "Planning Functionality",
            "status": "completed",
            "responses": [response1, response2, response3]
        })
    
    def test_context_continuity(self):
        """Test context continuity across sessions"""
        print("\n=== Testing Context Continuity ===")
        
        user_id = "context_test_user"
        session_id = "context_session_1"
        
        # Test 1: Establish context
        print("\n1. Establishing context...")
        context1 = "I'm a software engineer working on AI projects"
        response1 = self.make_request(context1, user_id, session_id)
        print(f"Response: {response1.get('reply', 'No reply')[:200]}...")
        
        # Test 2: Reference previous context
        print("\n2. Referencing previous context...")
        context2 = "Based on what I told you, suggest some learning resources"
        response2 = self.make_request(context2, user_id, session_id)
        print(f"Response: {response2.get('reply', 'No reply')[:200]}...")
        
        # Test 3: Complex context reference
        print("\n3. Complex context reference...")
        context3 = "What tools would be most helpful for my work?"
        response3 = self.make_request(context3, user_id, session_id)
        print(f"Response: {response3.get('reply', 'No reply')[:200]}...")
        
        self.test_results.append({
            "test": "Context Continuity",
            "status": "completed",
            "responses": [response1, response2, response3]
        })
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n=== Testing Error Handling ===")
        
        # Test 1: Empty message
        print("\n1. Empty message...")
        response1 = self.make_request("", "error_test_user")
        print(f"Response: {response1}")
        
        # Test 2: Very long message
        print("\n2. Very long message...")
        long_message = "Test " * 1000
        response2 = self.make_request(long_message, "error_test_user")
        print(f"Response length: {len(response2.get('reply', ''))}")
        
        # Test 3: Special characters
        print("\n3. Special characters...")
        special_message = "Test with émojis 🚀 and spëcial chars & symbols #$%"
        response3 = self.make_request(special_message, "error_test_user")
        print(f"Response: {response3.get('reply', 'No reply')[:100]}...")
        
        self.test_results.append({
            "test": "Error Handling",
            "status": "completed",
            "responses": [response1, response2, response3]
        })
    
    def analyze_responses(self):
        """Analyze test responses for RAG functionality"""
        print("\n=== Response Analysis ===")
        
        for result in self.test_results:
            test_name = result["test"]
            responses = result["responses"]
            
            print(f"\n{test_name}:")
            
            # Check for template responses (indicating mock responses)
            template_indicators = [
                "📋 **Your Personalized Plan**",
                "Analyze requirements",
                "Create detailed plan", 
                "Execute plan",
                "Morning Routine Best Practices"
            ]
            
            real_responses = 0
            for i, response in enumerate(responses, 1):
                reply = response.get('reply', '')
                is_template = any(indicator in reply for indicator in template_indicators)
                
                if not is_template:
                    real_responses += 1
                    print(f"  Response {i}: ✅ Real RAG response detected")
                else:
                    print(f"  Response {i}: ❌ Template/mock response detected")
            
            print(f"  Summary: {real_responses}/{len(responses)} real responses")
    
    def run_all_tests(self):
        """Run all RAG API tests"""
        print("🚀 Starting Comprehensive RAG API Testing")
        print("=" * 50)
        
        try:
            # Test server health
            print("\n=== Server Health Check ===")
            health_response = requests.get(f"{self.base_url}/health")
            if health_response.status_code == 200:
                print("✅ Server is healthy")
            else:
                print("❌ Server health check failed")
                return
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            return
        
        # Run all test suites
        self.test_memory_storage_and_retrieval()
        self.test_knowledge_retrieval()
        self.test_planning_functionality()
        self.test_context_continuity()
        self.test_error_handling()
        
        # Analyze results
        self.analyze_responses()
        
        # Generate summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        print(f"Total test suites: {total_tests}")
        print(f"Test suites completed: {len(self.test_results)}")
        
        # Save results to file
        with open("rag_api_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: rag_api_test_results.json")

if __name__ == "__main__":
    tester = RAGAPITester()
    tester.run_all_tests()
