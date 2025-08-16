from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver
from app.core.config import settings
from app.models.schemas import User, Product, Purchase, UserInterest, Recommendation
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Service for managing knowledge graph operations with Neo4j"""
    
    def __init__(self):
        self.driver: Optional[Driver] = None
        self._connect()
    
    def _connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Connected to Neo4j knowledge graph")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def create_user_node(self, user: User) -> bool:
        """Create or update user node in the knowledge graph"""
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (u:User {id: $user_id})
                SET u.email = $email,
                    u.profile_data = $profile_data,
                    u.created_at = $created_at,
                    u.updated_at = $updated_at
                RETURN u
                """
                result = session.run(query, {
                    "user_id": user.id,
                    "email": user.email,
                    "profile_data": user.profile_data,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat()
                })
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating user node for {user.id}: {e}")
            return False
    
    def create_product_node(self, product: Product) -> bool:
        """Create or update product node in the knowledge graph"""
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MERGE (p:Product {id: $product_id})
                SET p.name = $name,
                    p.category = $category,
                    p.price = $price,
                    p.description = $description,
                    p.image_url = $image_url,
                    p.metadata = $metadata,
                    p.created_at = $created_at
                RETURN p
                """
                result = session.run(query, {
                    "product_id": product.id,
                    "name": product.name,
                    "category": product.category.value,
                    "price": product.price,
                    "description": product.description,
                    "image_url": product.image_url,
                    "metadata": product.metadata,
                    "created_at": product.created_at.isoformat()
                })
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating product node for {product.id}: {e}")
            return False
    
    def create_purchase_relationship(self, purchase: Purchase) -> bool:
        """Create purchase relationship between user and product"""
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (u:User {id: $user_id})
                MATCH (p:Product {id: $product_id})
                CREATE (u)-[r:PURCHASED {
                    purchase_id: $purchase_id,
                    amount: $amount,
                    quantity: $quantity,
                    timestamp: $timestamp,
                    metadata: $metadata
                }]->(p)
                RETURN r
                """
                result = session.run(query, {
                    "user_id": purchase.user_id,
                    "product_id": purchase.product_id,
                    "purchase_id": purchase.id,
                    "amount": purchase.amount,
                    "quantity": purchase.quantity,
                    "timestamp": purchase.timestamp.isoformat(),
                    "metadata": purchase.metadata
                })
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating purchase relationship for {purchase.id}: {e}")
            return False
    
    def create_interest_relationship(self, interest: UserInterest) -> bool:
        """Create interest relationship for user"""
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return False
        
        try:
            with self.driver.session() as session:
                # Create or get interest category node
                category_query = """
                MERGE (ic:InterestCategory {name: $category})
                RETURN ic
                """
                session.run(category_query, {"category": interest.interest_category.value})
                
                # Create interest value node and relationships
                query = """
                MATCH (u:User {id: $user_id})
                MATCH (ic:InterestCategory {name: $category})
                MERGE (iv:InterestValue {value: $interest_value, category: $category})
                CREATE (u)-[r:INTERESTED_IN {
                    confidence_score: $confidence_score,
                    source: $source,
                    created_at: $created_at
                }]->(iv)
                CREATE (iv)-[:BELONGS_TO]->(ic)
                RETURN r
                """
                result = session.run(query, {
                    "user_id": interest.user_id,
                    "category": interest.interest_category.value,
                    "interest_value": interest.interest_value,
                    "confidence_score": interest.confidence_score,
                    "source": interest.source,
                    "created_at": interest.created_at.isoformat()
                })
                return result.single() is not None
        except Exception as e:
            logger.error(f"Error creating interest relationship for {interest.id}: {e}")
            return False
    
    def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get product recommendations for a user based on knowledge graph"""
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return []
        
        try:
            with self.driver.session() as session:
                # Find products bought by similar users (collaborative filtering)
                query = """
                MATCH (u:User {id: $user_id})-[:PURCHASED]->(p:Product)
                MATCH (p)<-[:PURCHASED]-(similar_user:User)
                MATCH (similar_user)-[:PURCHASED]->(rec_product:Product)
                WHERE NOT (u)-[:PURCHASED]->(rec_product)
                WITH rec_product, COUNT(*) as similarity_score
                
                // Also find products in categories user is interested in
                OPTIONAL MATCH (u)-[interest:INTERESTED_IN]->(iv:InterestValue)-[:BELONGS_TO]->(ic:InterestCategory)
                OPTIONAL MATCH (rec_product) WHERE rec_product.category = ic.name
                WITH rec_product, similarity_score, SUM(COALESCE(interest.confidence_score, 0)) as interest_score
                
                RETURN rec_product.id as product_id,
                       rec_product.name as name,
                       rec_product.category as category,
                       rec_product.price as price,
                       similarity_score,
                       interest_score,
                       (similarity_score * 0.6 + interest_score * 0.4) as total_score
                ORDER BY total_score DESC
                LIMIT $limit
                """
                result = session.run(query, {"user_id": user_id, "limit": limit})
                
                recommendations = []
                for record in result:
                    recommendations.append({
                        "product_id": record["product_id"],
                        "name": record["name"],
                        "category": record["category"],
                        "price": record["price"],
                        "score": min(record["total_score"] / 10.0, 1.0),  # Normalize to 0-1
                        "reason": f"Based on {record['similarity_score']} similar purchases and interest score {record['interest_score']:.2f}"
                    })
                
                return recommendations
        except Exception as e:
            logger.error(f"Error getting recommendations for user {user_id}: {e}")
            return []
    
    def get_similar_users(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find users with similar purchase patterns"""
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (u:User {id: $user_id})-[:PURCHASED]->(p:Product)
                MATCH (p)<-[:PURCHASED]-(similar_user:User)
                WHERE similar_user.id <> $user_id
                WITH similar_user, COUNT(p) as common_products
                MATCH (similar_user)-[:PURCHASED]->(all_products:Product)
                WITH similar_user, common_products, COUNT(all_products) as total_products
                RETURN similar_user.id as user_id,
                       similar_user.email as email,
                       common_products,
                       total_products,
                       (common_products * 1.0 / total_products) as similarity_score
                ORDER BY similarity_score DESC
                LIMIT $limit
                """
                result = session.run(query, {"user_id": user_id, "limit": limit})
                
                similar_users = []
                for record in result:
                    similar_users.append({
                        "user_id": record["user_id"],
                        "email": record["email"],
                        "common_products": record["common_products"],
                        "total_products": record["total_products"],
                        "similarity_score": record["similarity_score"]
                    })
                
                return similar_users
        except Exception as e:
            logger.error(f"Error finding similar users for {user_id}: {e}")
            return []
    
    def get_trending_products(self, limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        """Get trending products based on recent purchases"""
        if not self.driver:
            logger.warning("Neo4j driver not available")
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (u:User)-[p:PURCHASED]->(product:Product)
                WHERE datetime(p.timestamp) > datetime() - duration({days: $days})
                WITH product, COUNT(p) as purchase_count, SUM(p.amount) as total_revenue
                RETURN product.id as product_id,
                       product.name as name,
                       product.category as category,
                       product.price as price,
                       purchase_count,
                       total_revenue,
                       (purchase_count * 0.7 + total_revenue * 0.3) as trend_score
                ORDER BY trend_score DESC
                LIMIT $limit
                """
                result = session.run(query, {"days": days, "limit": limit})
                
                trending = []
                for record in result:
                    trending.append({
                        "product_id": record["product_id"],
                        "name": record["name"],
                        "category": record["category"],
                        "price": record["price"],
                        "purchase_count": record["purchase_count"],
                        "total_revenue": record["total_revenue"],
                        "trend_score": record["trend_score"]
                    })
                
                return trending
        except Exception as e:
            logger.error(f"Error getting trending products: {e}")
            return []


# Create service instance
knowledge_graph_service = KnowledgeGraphService()