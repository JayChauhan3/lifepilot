# Shopping Tool
import structlog
from typing import Dict, Any, List

logger = structlog.get_logger()

class ShoppingTool:
    """Mock shopping tool for agent use"""
    
    def __init__(self):
        logger.info("ShoppingTool initialized")
        self.products = [
            {"id": 1, "name": "Organic Oats", "price": 4.99, "category": "groceries"},
            {"id": 2, "name": "Fresh Fruits", "price": 12.99, "category": "groceries"},
            {"id": 3, "name": "Protein Powder", "price": 29.99, "category": "supplements"},
            {"id": 4, "name": "Yoga Mat", "price": 19.99, "category": "fitness"},
            {"id": 5, "name": "Water Bottle", "price": 9.99, "category": "fitness"}
        ]
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search for products"""
        logger.info("Searching products", query=query)
        query_lower = query.lower()
        
        results = []
        for product in self.products:
            if query_lower in product["name"].lower() or query_lower in product["category"].lower():
                results.append(product.copy())
        
        logger.info("Product search completed", query=query, results_count=len(results))
        return results
    
    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get product by ID"""
        for product in self.products:
            if product["id"] == product_id:
                logger.info("Product found", product_id=product_id, product_name=product["name"])
                return product.copy()
        
        logger.info("Product not found", product_id=product_id)
        return {}
    
    def calculate_total(self, items: List[Dict[str, Any]]) -> float:
        """Calculate total price for items"""
        total = 0.0
        for item in items:
            product = self.get_product_by_id(item.get("product_id", 0))
            if product:
                total += product["price"] * item.get("quantity", 1)
        
        logger.info("Total calculated", total=total, items_count=len(items))
        return total