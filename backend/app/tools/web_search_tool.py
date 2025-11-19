# Web Search Tool
import structlog
from typing import Dict, Any, List
import random

logger = structlog.get_logger()

class WebSearchTool:
    """Mock web search tool for agent use"""
    
    def __init__(self):
        logger.info("WebSearchTool initialized")
        self.mock_results = [
            # Morning/Productivity related
            {
                "title": "Morning Routine Best Practices",
                "url": "https://example.com/morning-routine",
                "snippet": "Learn how to create an effective morning routine that boosts productivity and wellbeing.",
                "keywords": ["morning", "routine", "productivity", "habits"]
            },
            {
                "title": "Health Benefits of Early Rising",
                "url": "https://example.com/early-rising",
                "snippet": "Research shows that waking up early can improve mental health and productivity.",
                "keywords": ["early", "rising", "health", "morning"]
            },
            {
                "title": "Planning Your Day Effectively",
                "url": "https://example.com/daily-planning",
                "snippet": "Discover strategies for effective daily planning and time management.",
                "keywords": ["planning", "day", "time", "management"]
            },
            {
                "title": "Exercise and Morning Energy",
                "url": "https://example.com/morning-exercise",
                "snippet": "How morning exercise can boost your energy levels throughout the day.",
                "keywords": ["exercise", "morning", "energy", "fitness"]
            },
            {
                "title": "Nutrition for Productive Mornings",
                "url": "https://example.com/morning-nutrition",
                "snippet": "Optimal nutrition choices to fuel your morning activities.",
                "keywords": ["nutrition", "morning", "food", "productivity"]
            },
            # Project Management related
            {
                "title": "Best Practices for Project Management",
                "url": "https://example.com/project-management",
                "snippet": "Comprehensive guide to modern project management methodologies and best practices.",
                "keywords": ["project", "management", "best", "practices"]
            },
            {
                "title": "Agile Methodology Overview",
                "url": "https://example.com/agile-methodology",
                "snippet": "Understanding agile principles and how to implement them in your projects.",
                "keywords": ["agile", "methodology", "scrum", "development"]
            },
            {
                "title": "Team Collaboration Tools",
                "url": "https://example.com/collaboration-tools",
                "snippet": "Top tools and platforms for effective team collaboration and communication.",
                "keywords": ["team", "collaboration", "tools", "communication"]
            },
            {
                "title": "Risk Management in Projects",
                "url": "https://example.com/risk-management",
                "snippet": "How to identify, assess, and mitigate risks in project management.",
                "keywords": ["risk", "management", "projects", "assessment"]
            },
            {
                "title": "Project Timeline Planning",
                "url": "https://example.com/timeline-planning",
                "snippet": "Creating realistic project timelines and managing deadlines effectively.",
                "keywords": ["timeline", "planning", "deadlines", "schedule"]
            },
            # Technology/Programming related
            {
                "title": "Python Best Practices Guide",
                "url": "https://example.com/python-best-practices",
                "snippet": "Essential best practices for writing clean, maintainable Python code.",
                "keywords": ["python", "programming", "code", "practices"]
            },
            {
                "title": "Machine Learning Fundamentals",
                "url": "https://example.com/machine-learning",
                "snippet": "Introduction to machine learning concepts and practical applications.",
                "keywords": ["machine", "learning", "ai", "algorithms"]
            },
            {
                "title": "Web Development Trends 2024",
                "url": "https://example.com/web-trends",
                "snippet": "Latest trends and technologies in web development for 2024.",
                "keywords": ["web", "development", "trends", "technology"]
            },
            {
                "title": "Cloud Computing Overview",
                "url": "https://example.com/cloud-computing",
                "snippet": "Understanding cloud computing services and deployment strategies.",
                "keywords": ["cloud", "computing", "aws", "azure"]
            },
            {
                "title": "Database Design Principles",
                "url": "https://example.com/database-design",
                "snippet": "Fundamental principles for designing efficient and scalable databases.",
                "keywords": ["database", "design", "sql", "architecture"]
            },
            # Business/Strategy related
            {
                "title": "Strategic Business Planning",
                "url": "https://example.com/business-strategy",
                "snippet": "How to develop and implement effective business strategies.",
                "keywords": ["business", "strategy", "planning", "growth"]
            },
            {
                "title": "Market Research Techniques",
                "url": "https://example.com/market-research",
                "snippet": "Effective methods for conducting market research and analysis.",
                "keywords": ["market", "research", "analysis", "techniques"]
            },
            {
                "title": "Leadership Best Practices",
                "url": "https://example.com/leadership",
                "snippet": "Essential leadership skills and strategies for team success.",
                "keywords": ["leadership", "management", "team", "skills"]
            },
            {
                "title": "Digital Marketing Trends",
                "url": "https://example.com/digital-marketing",
                "snippet": "Latest trends in digital marketing and customer acquisition.",
                "keywords": ["digital", "marketing", "trends", "customer"]
            },
            {
                "title": "Financial Planning Basics",
                "url": "https://example.com/financial-planning",
                "snippet": "Fundamental principles of personal and business financial planning.",
                "keywords": ["financial", "planning", "money", "investment"]
            }
        ]
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform web search using Gemini AI"""
        logger.info("Web search performed", query=query, max_results=max_results)
        
        try:
            # Use Gemini to generate search results based on knowledge
            from app.core.llm_service import get_llm_service
            llm_service = get_llm_service()
            
            system_prompt = """You are a helpful AI assistant that provides search results.
            Generate realistic search results for the given query.
            Format your response as a JSON array with the following structure:
            [
                {
                    "title": "Result title",
                    "snippet": "Brief description of the content",
                    "url": "https://example.com/result-url"
                }
            ]
            Make the results relevant, informative, and realistic for the query."""
            
            full_prompt = f"{system_prompt}\n\nQuery: {query}\n\nGenerate {max_results} search results:"
            
            response = llm_service.generate_text(full_prompt, max_tokens=1000)
            
            # Try to parse JSON response
            try:
                import json
                results = json.loads(response)
                if isinstance(results, list):
                    # Ensure each result has required fields
                    formatted_results = []
                    for result in results[:max_results]:
                        formatted_results.append({
                            "title": result.get("title", "Search Result"),
                            "snippet": result.get("snippet", "No description available"),
                            "url": result.get("url", "https://example.com")
                        })
                    return formatted_results
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON from Gemini response, using fallback")
            
            # Fallback: generate structured results from text response
            lines = response.split('\n')
            results = []
            for i, line in enumerate(lines[:max_results]):
                if line.strip():
                    results.append({
                        "title": f"Search Result {i+1}",
                        "snippet": line.strip(),
                        "url": f"https://example.com/result-{i+1}"
                    })
            return results
            
        except Exception as e:
            logger.error("Web search failed", error=str(e))
            # Return basic fallback results
            return [
                {
                    "title": "Search temporarily unavailable",
                    "snippet": "Please try again later. The search service is currently experiencing issues.",
                    "url": "https://example.com/error"
                }
            ]
        
        logger.info("Web search completed", query=query, results_count=len(results))
        return results
    
    def _calculate_relevance(self, query: str, result: Dict[str, Any]) -> float:
        """Calculate relevance score for a result"""
        relevance = 0.0
        query_terms = query.lower().split()
        
        # Check query terms in title (highest weight)
        title_matches = sum(1 for term in query_terms if term in result["title"].lower())
        relevance += title_matches * 0.4
        
        # Check query terms in snippet (medium weight)
        snippet_matches = sum(1 for term in query_terms if term in result["snippet"].lower())
        relevance += snippet_matches * 0.3
        
        # Check query terms in keywords (medium weight)
        keywords = result.get("keywords", [])
        keyword_matches = sum(1 for term in query_terms if any(term in keyword.lower() for keyword in keywords))
        relevance += keyword_matches * 0.3
        
        # Add small random variation for realism
        relevance += random.uniform(0.05, 0.15)
        
        return min(relevance, 1.0)  # Cap at 1.0
    
    def get_page_content(self, url: str) -> str:
        """Get page content (mock implementation)"""
        logger.info("Getting page content", url=url)
        
        # Mock content based on URL
        if "morning-routine" in url:
            return "This article discusses the importance of establishing a consistent morning routine. Key points include waking up at the same time, hydration, light exercise, and healthy breakfast."
        elif "early-rising" in url:
            return "Research indicates that early risers tend to be more productive and have better mental health outcomes. The article explores the science behind circadian rhythms."
        else:
            return "This is mock content for the requested page. In a real implementation, this would fetch and parse the actual web page content."