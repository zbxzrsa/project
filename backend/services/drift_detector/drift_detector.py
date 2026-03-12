from typing import List, Dict, Any, Optional
from enum import Enum


class DriftSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class DriftType(str, Enum):
    CIRCULAR_DEPENDENCY = "circular_dependency"
    UNEXPECTED_DEPENDENCY = "unexpected_dependency"
    ARCHITECTURE_VIOLATION = "architecture_violation"
    NEW_COUPLING = "new_coupling"


class DriftAlert:
    def __init__(
        self,
        drift_type: DriftType,
        severity: DriftSeverity,
        title: str,
        description: str,
        source: str,
        target: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.drift_type = drift_type
        self.severity = severity
        self.title = title
        self.description = description
        self.source = source
        self.target = target
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.drift_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "source": self.source,
            "target": self.target,
            "suggestion": self.suggestion,
        }


class ArchitectureBlueprint:
    """Define expected architecture rules."""
    
    def __init__(self):
        self.allowed_dependencies: Dict[str, List[str]] = {}
        self.forbidden_dependencies: List[tuple[str, str]] = []
        self.layer_rules: List[Dict[str, Any]] = []
    
    def add_allowed_dependency(self, from_module: str, to_module: str):
        """Add an allowed dependency."""
        if from_module not in self.allowed_dependencies:
            self.allowed_dependencies[from_module] = []
        self.allowed_dependencies[from_module].append(to_module)
    
    def add_forbidden_dependency(self, from_module: str, to_module: str):
        """Add a forbidden dependency."""
        self.forbidden_dependencies.append((from_module, to_module))
    
    def is_dependency_allowed(self, from_module: str, to_module: str) -> bool:
        """Check if a dependency is allowed."""
        if (from_module, to_module) in self.forbidden_dependencies:
            return False
        
        if from_module in self.allowed_dependencies:
            return to_module in self.allowed_dependencies[from_module]
        
        return True


class DriftDetector:
    """Detect architecture drift in the codebase."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.blueprint = ArchitectureBlueprint()
    
    def set_blueprint(self, blueprint: ArchitectureBlueprint):
        """Set architecture blueprint."""
        self.blueprint = blueprint
    
    async def detect_drift(self, graph_data: Dict[str, Any]) -> List[DriftAlert]:
        """Detect architecture drift from graph data."""
        
        alerts = []
        
        circular_deps = await self._detect_circular_dependencies(graph_data)
        alerts.extend(circular_deps)
        
        forbidden_violations = await self._detect_forbidden_dependencies(graph_data)
        alerts.extend(forbidden_violations)
        
        new_couplings = await self._detect_new_couplings(graph_data)
        alerts.extend(new_couplings)
        
        return alerts
    
    async def _detect_circular_dependencies(
        self,
        graph_data: Dict[str, Any],
    ) -> List[DriftAlert]:
        """Detect circular dependencies."""
        
        alerts = []
        
        from backend.services.graph_storage.storage import GraphStorage
        storage = GraphStorage(self.project_id)
        
        try:
            cycles = await storage.find_circular_dependencies()
            
            for cycle in cycles:
                cycle_str = " -> ".join(cycle)
                alerts.append(DriftAlert(
                    drift_type=DriftType.CIRCULAR_DEPENDENCY,
                    severity=DriftSeverity.CRITICAL,
                    title="Circular Dependency Detected",
                    description=f"Found circular dependency: {cycle_str}",
                    source=cycle[0],
                    target=cycle[-1],
                    suggestion="Refactor to break the circular dependency by extracting shared logic into a separate module",
                ))
        except Exception:
            pass
        
        return alerts
    
    async def _detect_forbidden_dependencies(
        self,
        graph_data: Dict[str, Any],
    ) -> List[DriftAlert]:
        """Detect forbidden dependencies based on blueprint."""
        
        alerts = []
        
        edges = graph_data.get("edges", [])
        
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            
            source_module = source.split("::")[0] if "::" in source else source
            target_module = target.split("::")[0] if "::" in target else target
            
            if not self.blueprint.is_dependency_allowed(source_module, target_module):
                alerts.append(DriftAlert(
                    drift_type=DriftType.ARCHITECTURE_VIOLATION,
                    severity=DriftSeverity.WARNING,
                    title="Architecture Violation",
                    description=f"Module '{source_module}' should not depend on '{target_module}'",
                    source=source,
                    target=target,
                    suggestion="Refactor to use dependency injection or move shared code to a lower-level module",
                ))
        
        return alerts
    
    async def _detect_new_couplings(
        self,
        graph_data: Dict[str, Any],
    ) -> List[DriftAlert]:
        """Detect new high-coupling relationships."""
        
        alerts = []
        
        edge_count = {}
        edges = graph_data.get("edges", [])
        
        for edge in edges:
            source = edge.get("source", "")
            target = edge.get("target", "")
            key = f"{source}->{target}"
            
            edge_count[key] = edge_count.get(key, 0) + 1
        
        for key, count in edge_count.items():
            if count > 10:
                source, target = key.split("->")
                alerts.append(DriftAlert(
                    drift_type=DriftType.NEW_COUPLING,
                    severity=DriftSeverity.INFO,
                    title="High Coupling Detected",
                    description=f"Strong coupling between '{source}' and '{target}' ({count} relationships)",
                    source=source,
                    target=target,
                    suggestion="Consider extracting shared functionality to reduce coupling",
                ))
        
        return alerts
    
    async def get_drift_trend(self, days: int = 30) -> Dict[str, Any]:
        """Get drift trend over time."""
        
        return {
            "period_days": days,
            "total_alerts": 0,
            "critical_count": 0,
            "warning_count": 0,
            "info_count": 0,
            "trend": [],
        }
