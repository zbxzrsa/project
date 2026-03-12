from typing import List, Dict, Any, Optional
from backend.services.ast_parser.parser import GraphNode, GraphRelationship


class GraphStorage:
    """Storage layer for graph data in Neo4j."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
    
    async def store_nodes(self, nodes: List[GraphNode]) -> None:
        """Store nodes in Neo4j."""
        from backend.core.neo4j import neo4j_connection
        
        for node in nodes:
            query = """
            MERGE (n:GraphNode {
                node_id: $node_id,
                project_id: $project_id
            })
            SET n.type = $type,
                n.name = $name,
                n.file_path = $file_path,
                n.line_start = $line_start,
                n.line_end = $line_end,
                n.properties = $properties
            """
            await neo4j_connection.execute_write(
                query,
                {
                    "node_id": node.node_id,
                    "project_id": self.project_id,
                    "type": node.node_type.value,
                    "name": node.name,
                    "file_path": node.file_path,
                    "line_start": node.line_start,
                    "line_end": node.line_end,
                    "properties": node.properties,
                }
            )
    
    async def store_relationships(self, relationships: List[GraphRelationship]) -> None:
        """Store relationships in Neo4j."""
        from backend.core.neo4j import neo4j_connection
        
        for rel in relationships:
            query = """
            MATCH (a:GraphNode {node_id: $source_id, project_id: $project_id})
            MATCH (b:GraphNode {node_id: $target_id, project_id: $project_id})
            MERGE (a)-[r:RELATES {type: $rel_type}]->(b)
            SET r.properties = $properties
            """
            await neo4j_connection.execute_write(
                query,
                {
                    "source_id": rel.source_id,
                    "target_id": rel.target_id,
                    "project_id": self.project_id,
                    "rel_type": rel.rel_type,
                    "properties": rel.properties,
                }
            )
    
    async def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes for the project."""
        from backend.core.neo4j import neo4j_connection
        
        query = """
        MATCH (n:GraphNode {project_id: $project_id})
        RETURN n
        """
        results = await neo4j_connection.execute_query(
            query,
            {"project_id": self.project_id}
        )
        
        return [dict(record["n"]) for record in results]
    
    async def get_all_relationships(self) -> List[Dict[str, Any]]:
        """Get all relationships for the project."""
        from backend.core.neo4j import neo4j_connection
        
        query = """
        MATCH (a:GraphNode {project_id: $project_id})-[r]->(b:GraphNode {project_id: $project_id})
        RETURN a.node_id as source, b.node_id as target, type(r) as type, r.properties as properties
        """
        results = await neo4j_connection.execute_query(
            query,
            {"project_id": self.project_id}
        )
        
        return results
    
    async def get_node_dependencies(self, node_id: str) -> List[Dict[str, Any]]:
        """Get dependencies for a specific node."""
        from backend.core.neo4j import neo4j_connection
        
        query = """
        MATCH (a:GraphNode {node_id: $node_id, project_id: $project_id})-[r]->(b:GraphNode {project_id: $project_id})
        RETURN b.node_id as node_id, b.name as name, b.type as type, type(r) as relationship
        """
        results = await neo4j_connection.execute_query(
            query,
            {"node_id": node_id, "project_id": self.project_id}
        )
        
        return results
    
    async def calculate_coupling(self) -> Dict[str, Any]:
        """Calculate coupling metrics for the project."""
        from backend.core.neo4j import neo4j_connection
        
        query = """
        MATCH (a:GraphNode {project_id: $project_id})-[r:RELATES]->(b:GraphNode {project_id: $project_id})
        WITH a, b, count(r) as rel_count
        RETURN a.name as source, collect(b.name) as targets, sum(rel_count) as coupling
        ORDER BY coupling DESC
        LIMIT 10
        """
        results = await neo4j_connection.execute_query(
            query,
            {"project_id": self.project_id}
        )
        
        return results
    
    async def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in the graph."""
        from backend.core.neo4j import neo4j_connection
        
        query = """
        MATCH path = (a:GraphNode {project_id: $project_id})-[:RELATES*]->(a)
        WHERE length(path) > 1
        RETURN [n IN nodes(path) | n.name] as cycle
        LIMIT 20
        """
        results = await neo4j_connection.execute_query(
            query,
            {"project_id": self.project_id}
        )
        
        return [record["cycle"] for record in results]
    
    async def clear_project_graph(self) -> None:
        """Clear all graph data for the project."""
        from backend.core.neo4j import neo4j_connection
        
        query = """
        MATCH (n:GraphNode {project_id: $project_id})
        DETACH DELETE n
        """
        await neo4j_connection.execute_write(
            query,
            {"project_id": self.project_id}
        )
    
    async def get_graph_data(self) -> Dict[str, Any]:
        """Get complete graph data for visualization."""
        nodes = await self.get_all_nodes()
        relationships = await self.get_all_relationships()
        
        return {
            "nodes": nodes,
            "edges": relationships,
            "nodeCount": len(nodes),
            "edgeCount": len(relationships),
        }
