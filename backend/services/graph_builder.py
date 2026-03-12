from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass
from pathlib import Path

from backend.core.neo4j import neo4j_connection
from backend.core.logging import logger


@dataclass
class CodeEntity:
    id: str
    name: str
    type: str
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    docstring: Optional[str] = None
    language: str = "python"


@dataclass
class CodeRelation:
    source_id: str
    target_id: str
    relation_type: str


class GraphBuilder:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.entities: List[CodeEntity] = []
        self.relations: List[CodeRelation] = []

    async def analyze_codebase(self, code_dir: str) -> None:
        path = Path(code_dir)
        for file_path in path.rglob("*.py"):
            await self._analyze_python_file(str(file_path))

    async def _analyze_python_file(self, file_path: str) -> None:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self._extract_modules(file_path, content)
            self._extract_classes(file_path, content)
            self._extract_functions(file_path, content)
            self._extract_imports(file_path, content)

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

    def _extract_modules(self, file_path: str, content: str) -> None:
        module_name = Path(file_path).stem
        entity = CodeEntity(
            id=f"{self.project_id}:module:{module_name}",
            name=module_name,
            type="Module",
            file_path=file_path,
            language="python",
        )
        self.entities.append(entity)

    def _extract_classes(self, file_path: str, content: str) -> None:
        class_pattern = r"^class\s+(\w+)(?:\(([^)]+)\))?:"
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            line_no = content[:match.start()].count("\n") + 1
            base_classes = match.group(2) or ""

            entity = CodeEntity(
                id=f"{self.project_id}:class:{class_name}",
                name=class_name,
                type="Class",
                file_path=file_path,
                line_start=line_no,
                language="python",
            )
            self.entities.append(entity)

            if base_classes:
                for base in base_classes.split(","):
                    base = base.strip()
                    if base and base != "object":
                        self.relations.append(
                            CodeRelation(
                                source_id=f"{self.project_id}:class:{class_name}",
                                target_id=f"{self.project_id}:class:{base}",
                                relation_type="INHERITS",
                            )
                        )

    def _extract_functions(self, file_path: str, content: str) -> None:
        func_pattern = r"^(?:async\s+)?def\s+(\w+)\s*\([^)]*\):"
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            if func_name.startswith("_") and not func_name.startswith("__"):
                continue
            line_no = content[:match.start()].count("\n") + 1

            entity = CodeEntity(
                id=f"{self.project_id}:function:{func_name}",
                name=func_name,
                type="Function",
                file_path=file_path,
                line_start=line_no,
                language="python",
            )
            self.entities.append(entity)

    def _extract_imports(self, file_path: str, content: str) -> None:
        import_pattern = r"^(?:from\s+([\w.]+)\s+)?import\s+([\w., ]+)"
        module_name = Path(file_path).stem

        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1)
            imports = match.group(2)

            if module:
                for imp in imports.split(","):
                    imp = imp.strip()
                    if imp:
                        self.relations.append(
                            CodeRelation(
                                source_id=f"{self.project_id}:module:{module_name}",
                                target_id=f"{self.project_id}:module:{imp.split('.')[-1]}",
                                relation_type="IMPORTS",
                            )
                        )

    async def build_graph(self) -> Dict[str, Any]:
        logger.info(f"Building graph for project {self.project_id}")

        for entity in self.entities:
            await self._create_entity_node(entity)

        for relation in self.relations:
            await self._create_relation(relation)

        stats = {
            "entities_created": len(self.entities),
            "relations_created": len(self.relations),
        }
        logger.info(f"Graph built: {stats}")
        return stats

    async def _create_entity_node(self, entity: CodeEntity) -> None:
        query = """
        MERGE (e:CodeEntity {
            id: $id,
            project_id: $project_id,
            name: $name,
            type: $type,
            file_path: $file_path,
            line_start: $line_start,
            line_end: $line_end,
            language: $language
        })
        """
        await neo4j_connection.execute_write(
            query,
            {
                "id": entity.id,
                "project_id": self.project_id,
                "name": entity.name,
                "type": entity.type,
                "file_path": entity.file_path,
                "line_start": entity.line_start,
                "line_end": entity.line_end,
                "language": entity.language,
            },
        )

    async def _create_relation(self, relation: CodeRelation) -> None:
        query = """
        MATCH (source:CodeEntity {id: $source_id})
        MATCH (target:CodeEntity {id: $target_id})
        MERGE (source)-[r:DEPENDS_ON {type: $relation_type}]->(target)
        """
        await neo4j_connection.execute_write(
            query,
            {
                "source_id": relation.source_id,
                "target_id": relation.target_id,
                "relation_type": relation.relation_type,
            },
        )

    async def get_dependency_graph(
        self,
        entity_id: Optional[str] = None,
        depth: int = 3,
    ) -> Dict[str, Any]:
        if entity_id:
            query = """
            MATCH path = (e:CodeEntity {id: $entity_id})-[r:DEPENDS_ON*1..%d]->(target)
            RETURN path, length(path) as depth
            ORDER BY depth
            LIMIT 100
            """ % depth
            records = await neo4j_connection.execute_query(query, {"entity_id": entity_id})
        else:
            query = """
            MATCH (e:CodeEntity {project_id: $project_id})
            RETURN e.id, e.name, e.type, e.file_path
            ORDER BY e.type, e.name
            """
            records = await neo4j_connection.execute_query(query, {"project_id": self.project_id})

        return {"data": records}

    async def find_circular_dependencies(self) -> List[Dict[str, Any]]:
        query = """
        MATCH path = (a:CodeEntity)-[:DEPENDS_ON*]->(a)
        WHERE a.project_id = $project_id
        RETURN path, length(path) as cycle_length
        ORDER BY cycle_length
        """
        records = await neo4j_connection.execute_query(query, {"project_id": self.project_id})
        return records

    async def clear_graph(self) -> None:
        query = """
        MATCH (e:CodeEntity {project_id: $project_id})
        DETACH DELETE e
        """
        await neo4j_connection.execute_write(query, {"project_id": self.project_id})
        logger.info(f"Cleared graph for project {self.project_id}")
