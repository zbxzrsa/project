from typing import List, Dict, Any, Optional
from enum import Enum
import ast
import re


class NodeType(str, Enum):
    FILE = "file"
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"


class GraphNode:
    def __init__(
        self,
        node_id: str,
        node_type: NodeType,
        name: str,
        file_path: str,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.name = name
        self.file_path = file_path
        self.line_start = line_start
        self.line_end = line_end
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.node_id,
            "type": self.node_type.value,
            "name": self.name,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "properties": self.properties,
        }


class GraphRelationship:
    def __init__(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ):
        self.source_id = source_id
        self.target_id = target_id
        self.rel_type = rel_type
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.rel_type,
            "properties": self.properties,
        }


class PythonParser:
    """Parse Python code into AST nodes and relationships."""
    
    def __init__(self):
        self.nodes: List[GraphNode] = []
        self.relationships: List[GraphRelationship] = []
        self.file_path: str = ""
        self.module_name: str = ""
    
    def parse(self, file_path: str, content: str) -> tuple[List[GraphNode], List[GraphRelationship]]:
        """Parse Python file and extract nodes and relationships."""
        
        self.nodes = []
        self.relationships = []
        self.file_path = file_path
        self.module_name = self._get_module_name(file_path)
        
        file_node = GraphNode(
            node_id=f"{self.module_name}::file",
            node_type=NodeType.FILE,
            name=file_path.split("/")[-1],
            file_path=file_path,
        )
        self.nodes.append(file_node)
        
        try:
            tree = ast.parse(content, filename=file_path)
            self._visit_module(tree, file_node.node_id)
        except SyntaxError as e:
            pass
        
        return self.nodes, self.relationships
    
    def _visit_module(self, tree: ast.AST, file_node_id: str):
        """Visit module-level nodes."""
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                self._visit_class(node, file_node_id)
            elif isinstance(node, ast.FunctionDef):
                if not isinstance(node, ast.ClassDef):
                    self._visit_function(node, file_node_id, is_method=False)
            elif isinstance(node, ast.Import):
                self._visit_import(node, file_node_id)
            elif isinstance(node, ast.ImportFrom):
                self._visit_import_from(node, file_node_id)
    
    def _visit_class(self, node: ast.ClassDef, file_node_id: str):
        """Visit class definition."""
        
        class_node = GraphNode(
            node_id=f"{self.module_name}::{node.name}",
            node_type=NodeType.CLASS,
            name=node.name,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno,
            properties={
                "bases": [self._get_base_name(base) for base in node.bases],
                "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
            },
        )
        self.nodes.append(class_node)
        
        self.relationships.append(GraphRelationship(
            source_id=file_node_id,
            target_id=class_node.node_id,
            rel_type="CONTAINS",
        ))
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._visit_method(item, class_node.node_id)
    
    def _visit_method(self, node: ast.FunctionDef, class_node_id: str):
        """Visit class method."""
        
        method_node = GraphNode(
            node_id=f"{class_node_id}.{node.name}",
            node_type=NodeType.METHOD,
            name=node.name,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno,
            properties={
                "args": [arg.arg for arg in node.args.args],
                "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            },
        )
        self.nodes.append(method_node)
        
        self.relationships.append(GraphRelationship(
            source_id=class_node_id,
            target_id=method_node.node_id,
            rel_type="HAS_METHOD",
        ))
        
        for call in ast.walk(node):
            if isinstance(call, ast.Name) and isinstance(call.ctx, ast.Load):
                self.relationships.append(GraphRelationship(
                    source_id=method_node.node_id,
                    target_id=f"{self.module_name}::{call.id}",
                    rel_type="CALLS",
                ))
    
    def _visit_function(self, node: ast.FunctionDef, file_node_id: str, is_method: bool = False):
        """Visit function definition."""
        
        func_node = GraphNode(
            node_id=f"{self.module_name}::{node.name}",
            node_type=NodeType.METHOD if is_method else NodeType.FUNCTION,
            name=node.name,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno,
            properties={
                "args": [arg.arg for arg in node.args.args],
                "decorators": [d.id if isinstance(d, ast.Name) else str(d) for d in node.decorator_list],
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            },
        )
        self.nodes.append(func_node)
        
        self.relationships.append(GraphRelationship(
            source_id=file_node_id,
            target_id=func_node.node_id,
            rel_type="CONTAINS",
        ))
    
    def _visit_import(self, node: ast.Import, file_node_id: str):
        """Visit import statement."""
        
        for alias in node.names:
            import_node = GraphNode(
                node_id=f"import::{alias.name}",
                node_type=NodeType.IMPORT,
                name=alias.name,
                file_path=self.file_path,
            )
            self.nodes.append(import_node)
            
            self.relationships.append(GraphRelationship(
                source_id=file_node_id,
                target_id=import_node.node_id,
                rel_type="IMPORTS",
            ))
    
    def _visit_import_from(self, node: ast.ImportFrom, file_node_id: str):
        """Visit from ... import statement."""
        
        module = node.module or ""
        
        for alias in node.names:
            import_name = f"{module}.{alias.name}" if module else alias.name
            import_node = GraphNode(
                node_id=f"import::{import_name}",
                node_type=NodeType.IMPORT,
                name=import_name,
                file_path=self.file_path,
            )
            self.nodes.append(import_node)
            
            self.relationships.append(GraphRelationship(
                source_id=file_node_id,
                target_id=import_node.node_id,
                rel_type="IMPORTS_FROM",
            ))
    
    def _get_module_name(self, file_path: str) -> str:
        """Get module name from file path."""
        
        if file_path.endswith("__init__.py"):
            return file_path.split("/")[-2] if "/" in file_path else "root"
        
        return file_path.split("/")[-1].replace(".py", "")
    
    def _get_base_name(self, base: ast.expr) -> str:
        """Get base class name."""
        
        if isinstance(base, ast.Name):
            return base.id
        elif isinstance(base, ast.Attribute):
            return f"{self._get_base_name(base.value)}.{base.attr}"
        return str(base)


class JavaScriptParser:
    """Parse JavaScript/TypeScript code into nodes and relationships."""
    
    def __init__(self):
        self.nodes: List[GraphNode] = []
        self.relationships: List[GraphRelationship] = []
        self.file_path: str = ""
    
    def parse(self, file_path: str, content: str) -> tuple[List[GraphNode], List[GraphRelationship]]:
        """Parse JavaScript/TypeScript file."""
        
        self.nodes = []
        self.relationships = []
        self.file_path = file_path
        
        file_node = GraphNode(
            node_id=f"file::{file_path}",
            node_type=NodeType.FILE,
            name=file_path.split("/")[-1],
            file_path=file_path,
        )
        self.nodes.append(file_node)
        
        class_pattern = r'class\s+(\w+)(?:\s+extends\s+(\w+))?'
        func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(?'
        arrow_pattern = r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>'
        
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            extends = match.group(2)
            
            class_node = GraphNode(
                node_id=f"{file_path}::{class_name}",
                node_type=NodeType.CLASS,
                name=class_name,
                file_path=file_path,
                properties={"extends": extends} if extends else {},
            )
            self.nodes.append(class_node)
            
            self.relationships.append(GraphRelationship(
                source_id=file_node.node_id,
                target_id=class_node.node_id,
                rel_type="CONTAINS",
            ))
        
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            if not func_name.startswith("on"):
                func_node = GraphNode(
                    node_id=f"{file_path}::{func_name}",
                    node_type=NodeType.FUNCTION,
                    name=func_name,
                    file_path=file_path,
                )
                self.nodes.append(func_node)
                
                self.relationships.append(GraphRelationship(
                    source_id=file_node.node_id,
                    target_id=func_node.node_id,
                    rel_type="CONTAINS",
                ))
        
        import_pattern = r'import\s+(?:{[^}]+}|\w+)\s+from\s+["\']([^"\']+)["\']|import\s+["\']([^"\']+)["\']'
        
        for match in re.finditer(import_pattern, content):
            module = match.group(1) or match.group(2)
            import_node = GraphNode(
                node_id=f"import::{module}",
                node_type=NodeType.IMPORT,
                name=module,
                file_path=file_path,
            )
            self.nodes.append(import_node)
            
            self.relationships.append(GraphRelationship(
                source_id=file_node.node_id,
                target_id=import_node.node_id,
                rel_type="IMPORTS",
            ))
        
        return self.nodes, self.relationships


def get_parser_for_file(file_path: str) -> Any:
    """Get appropriate parser based on file extension."""
    
    ext = file_path.split(".")[-1].lower() if "." in file_path else ""
    
    if ext in ["py"]:
        return PythonParser()
    elif ext in ["js", "jsx", "ts", "tsx"]:
        return JavaScriptParser()
    
    return None
