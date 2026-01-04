"""
Utility functions for the Predictive Risk & Resource Management System.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RiskPrediction:
    """Data class for risk predictions."""
    risk_type: str
    probability: float  # 0-100
    impact: str  # Low, Medium, High, Critical
    description: str
    mitigation_strategy: str
    confidence_score: float  # 0-1
    reasoning: str


@dataclass
class ResourceAllocation:
    """Data class for resource allocation."""
    resource_id: str
    resource_name: str
    current_allocation: float
    recommended_allocation: float
    justification: str
    conflict_risk: str  # None, Low, Medium, High
    efficiency_gain: float  # percentage


@dataclass
class Bottleneck:
    """Data class for identified bottlenecks."""
    bottleneck_id: str
    task_name: str
    severity: str  # Low, Medium, High, Critical
    expected_delay_days: int
    root_cause: str
    mitigation_recommendation: str
    parallel_task_opportunity: Optional[str]


@dataclass
class ProjectAnalysis:
    """Comprehensive project analysis result."""
    project_id: str
    analysis_timestamp: str
    risks: List[RiskPrediction]
    resource_recommendations: List[ResourceAllocation]
    bottlenecks: List[Bottleneck]
    overall_risk_score: float  # 0-100
    confidence_level: float  # 0-1
    executive_summary: str
    top_recommendations: List[str]


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage."""
    return f"{value:.{decimals}f}%"


def calculate_variance(planned: float, actual: float) -> float:
    """Calculate variance between planned and actual values."""
    if planned == 0:
        return 0
    return ((actual - planned) / planned) * 100


def calculate_delay_ratio(planned_days: int, delay_days: int) -> float:
    """Calculate delay ratio as percentage."""
    if planned_days == 0:
        return 0
    return (delay_days / planned_days) * 100


def calculate_project_health_score(
    budget_variance: float,
    schedule_variance: float,
    quality_score: float  # 0-100
) -> float:
    """
    Calculate overall project health score (0-100).
    Lower budget/schedule variance is better.
    """
    budget_health = max(0, 100 - abs(budget_variance))
    schedule_health = max(0, 100 - abs(schedule_variance))
    
    # Weighted average: 30% budget, 30% schedule, 40% quality
    health_score = (budget_health * 0.3) + (schedule_health * 0.3) + (quality_score * 0.4)
    return max(0, min(100, health_score))


def estimate_risk_probability(
    similar_projects_with_risk: int,
    total_similar_projects: int,
    confidence_adjustment: float = 1.0
) -> float:
    """
    Estimate risk probability based on historical data.
    Returns value between 0-100.
    """
    if total_similar_projects == 0:
        return 50.0  # Default middle estimate
    
    base_probability = (similar_projects_with_risk / total_similar_projects) * 100
    # Apply confidence adjustment (e.g., for smaller sample sizes)
    adjusted_probability = base_probability * confidence_adjustment
    return min(100, max(0, adjusted_probability))


def estimate_impact_level(
    avg_delay_days: float,
    avg_cost_overrun_percent: float
) -> str:
    """Estimate impact level based on historical metrics."""
    # Simple heuristic based on delay and cost impact
    delay_impact = avg_delay_days
    cost_impact = avg_cost_overrun_percent
    
    combined_impact = (delay_impact * 0.5) + (cost_impact * 0.5)
    
    if combined_impact > 30:
        return "Critical"
    elif combined_impact > 20:
        return "High"
    elif combined_impact > 10:
        return "Medium"
    else:
        return "Low"


def normalize_text(text: str) -> str:
    """Normalize text for processing."""
    return text.strip().lower()


def generate_hash(data: str) -> str:
    """Generate SHA256 hash of data."""
    return hashlib.sha256(data.encode()).hexdigest()


def dataclass_to_dict(obj: Any) -> Dict:
    """Convert dataclass to dictionary."""
    if hasattr(obj, '__dataclass_fields__'):
        return asdict(obj)
    return obj


def serialize_analysis(analysis: ProjectAnalysis) -> str:
    """Serialize ProjectAnalysis to JSON string."""
    data = {
        'project_id': analysis.project_id,
        'analysis_timestamp': analysis.analysis_timestamp,
        'risks': [asdict(r) for r in analysis.risks],
        'resource_recommendations': [asdict(r) for r in analysis.resource_recommendations],
        'bottlenecks': [asdict(b) for b in analysis.bottlenecks],
        'overall_risk_score': analysis.overall_risk_score,
        'confidence_level': analysis.confidence_level,
        'executive_summary': analysis.executive_summary,
        'top_recommendations': analysis.top_recommendations
    }
    return json.dumps(data, indent=2, default=str)


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object."""
    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")


def calculate_days_between(start_date: datetime, end_date: datetime) -> int:
    """Calculate days between two dates."""
    delta = end_date - start_date
    return delta.days


def calculate_project_duration(start_date: str, end_date: str) -> int:
    """Calculate project duration in days."""
    start = parse_date(start_date)
    end = parse_date(end_date)
    return calculate_days_between(start, end)


class AnalysisCache:
    """Simple cache for analysis results."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (FIFO)
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache


def create_project_context(
    project_data: Dict,
    historical_projects: List[Dict],
    incidents: List[Dict]
) -> str:
    """Create a rich context string from project and historical data for LLM."""
    context = f"""
PROJECT CONTEXT:
- Project ID: {project_data.get('project_id', 'Unknown')}
- Project Name: {project_data.get('project_name', 'Unknown')}
- Industry: {project_data.get('industry', 'Unknown')}
- Team Size: {project_data.get('team_size', 'Unknown')}
- Budget: ${project_data.get('budget', 0):,}
- Planned Duration: {project_data.get('duration_days', 'Unknown')} days

SIMILAR HISTORICAL PROJECTS:
"""
    for proj in historical_projects[:5]:  # Top 5 similar projects
        context += f"""
- {proj.get('project_name')}: 
  * Budget: ${proj.get('actual_cost', 0):,} (planned: ${proj.get('budget', 0):,})
  * Delay: {proj.get('delays_days', 0)} days
  * Risk: {proj.get('risk_description', 'N/A')}
  * Resolution: {proj.get('resolution', 'N/A')}
"""
    
    if incidents:
        context += "\nRELATED HISTORICAL INCIDENTS:\n"
        for incident in incidents[:5]:
            context += f"""
- {incident.get('description')}
  * Severity: {incident.get('severity', 'Unknown')}
  * Impact: {incident.get('impact', 'Unknown')}
  * Resolution: {incident.get('resolution', 'N/A')}
"""
    
    return context


logger.info("Utils module initialized")
