"""
Resource Optimizer Agent for optimizing resource allocation.
"""
import logging
from typing import List, Dict, Tuple
from src.utils import ResourceAllocation

logger = logging.getLogger(__name__)


class ResourceOptimizerAgent:
    """Optimizes resource allocation across projects."""
    
    def __init__(self, resources_data: List[Dict]):
        self.resources_data = resources_data
        self.resource_index = {r.get('resource_id'): r for r in resources_data}
        logger.info(f"Initialized ResourceOptimizerAgent with {len(resources_data)} resources")
    
    def optimize_allocation(
        self,
        project_id: str,
        project_requirements: Dict,
        current_allocations: Dict[str, float] = None
    ) -> List[ResourceAllocation]:
        """
        Optimize resource allocation for a project.
        
        Args:
            project_id: Project identifier
            project_requirements: Required skills and team composition
            current_allocations: Current allocation of resources (resource_id -> allocation %)
        
        Returns:
            List of ResourceAllocation recommendations
        """
        recommendations = []
        
        required_skills = project_requirements.get('required_skills', {})
        team_size = project_requirements.get('team_size', 5)
        priority = project_requirements.get('priority', 'Medium')
        
        # Find best resources for each required skill
        for skill, count in required_skills.items():
            matching_resources = self._find_resources_by_skill(skill, count)
            
            for resource in matching_resources:
                resource_id = resource.get('resource_id')
                current_alloc = current_allocations.get(resource_id, 0) if current_allocations else 0
                max_alloc = resource.get('max_allocation', 1.0)
                
                # Calculate recommended allocation
                recommended_alloc = self._calculate_allocation(
                    current_alloc,
                    max_alloc,
                    priority
                )
                
                # Check for conflicts
                conflict_risk = self._assess_conflict_risk(
                    resource_id,
                    current_alloc,
                    recommended_alloc
                )
                
                # Calculate efficiency gain
                efficiency_gain = self._calculate_efficiency_gain(
                    resource.get('skill_level'),
                    current_alloc,
                    recommended_alloc
                )
                
                recommendation = ResourceAllocation(
                    resource_id=resource_id,
                    resource_name=resource.get('resource_name'),
                    current_allocation=current_alloc,
                    recommended_allocation=recommended_alloc,
                    justification=f'Required for {skill} role at {resource.get("skill_level")} level',
                    conflict_risk=conflict_risk,
                    efficiency_gain=efficiency_gain
                )
                
                recommendations.append(recommendation)
        
        logger.info(f"Generated {len(recommendations)} resource recommendations for {project_id}")
        return recommendations
    
    def analyze_utilization(self) -> Dict:
        """Analyze current resource utilization."""
        utilization_report = {
            'total_resources': len(self.resources_data),
            'average_utilization': 0,
            'overallocated_resources': [],
            'underutilized_resources': [],
            'by_skill': {}
        }
        
        total_allocation = 0
        
        for resource in self.resources_data:
            resource_id = resource.get('resource_id')
            current_alloc = resource.get('current_allocation', 0)
            max_alloc = resource.get('max_allocation', 1.0)
            skill = resource.get('skill_category')
            
            total_allocation += current_alloc
            
            # Track by skill
            if skill not in utilization_report['by_skill']:
                utilization_report['by_skill'][skill] = {
                    'count': 0,
                    'avg_allocation': 0,
                    'overallocated': 0
                }
            
            utilization_report['by_skill'][skill]['count'] += 1
            utilization_report['by_skill'][skill]['avg_allocation'] += current_alloc
            
            # Identify allocation issues
            if current_alloc > max_alloc:
                utilization_report['overallocated_resources'].append({
                    'resource_id': resource_id,
                    'resource_name': resource.get('resource_name'),
                    'allocation': current_alloc,
                    'max_allocation': max_alloc,
                    'overallocation': current_alloc - max_alloc
                })
                utilization_report['by_skill'][skill]['overallocated'] += 1
            
            elif current_alloc < 0.5:
                utilization_report['underutilized_resources'].append({
                    'resource_id': resource_id,
                    'resource_name': resource.get('resource_name'),
                    'allocation': current_alloc,
                    'available_capacity': max_alloc - current_alloc
                })
        
        # Calculate averages
        if len(self.resources_data) > 0:
            utilization_report['average_utilization'] = total_allocation / len(self.resources_data)
        
        # Finalize by_skill stats
        for skill in utilization_report['by_skill']:
            count = utilization_report['by_skill'][skill]['count']
            if count > 0:
                utilization_report['by_skill'][skill]['avg_allocation'] /= count
        
        return utilization_report
    
    def identify_bottlenecks(self) -> List[Dict]:
        """Identify resource bottlenecks."""
        bottlenecks = []
        
        # Group by skill category
        by_skill = {}
        for resource in self.resources_data:
            skill = resource.get('skill_category')
            if skill not in by_skill:
                by_skill[skill] = []
            by_skill[skill].append(resource)
        
        # Analyze each skill category
        for skill, resources in by_skill.items():
            avg_alloc = sum(r.get('current_allocation', 0) for r in resources) / len(resources)
            available = sum(r.get('max_allocation', 1.0) - r.get('current_allocation', 0) for r in resources)
            
            if avg_alloc > 0.85:
                bottlenecks.append({
                    'skill': skill,
                    'issue': 'High allocation pressure',
                    'avg_allocation': avg_alloc,
                    'available_capacity': available,
                    'resource_count': len(resources),
                    'recommendation': f'Consider hiring more {skill} resources or redistributing load'
                })
            
            if available < 0.5:
                bottlenecks.append({
                    'skill': skill,
                    'issue': 'Limited available capacity',
                    'avg_allocation': avg_alloc,
                    'available_capacity': available,
                    'resource_count': len(resources),
                    'recommendation': f'No buffer capacity for {skill}. Consider hiring or deferring lower-priority work'
                })
        
        return bottlenecks
    
    def suggest_reallocation(self) -> List[Dict]:
        """Suggest resource reallocations to improve utilization."""
        suggestions = []
        
        utilization = self.analyze_utilization()
        
        # Suggest moving underutilized resources to overallocated areas
        for over_resource in utilization['overallocated_resources']:
            for under_resource in utilization['underutilized_resources']:
                if over_resource['resource_id'] != under_resource['resource_id']:
                    # Check if skills are compatible
                    over_skill = next(
                        (r.get('skill_category') for r in self.resources_data 
                         if r.get('resource_id') == over_resource['resource_id']),
                        None
                    )
                    under_skill = next(
                        (r.get('skill_category') for r in self.resources_data 
                         if r.get('resource_id') == under_resource['resource_id']),
                        None
                    )
                    
                    if over_skill == under_skill:
                        suggestions.append({
                            'type': 'rebalance',
                            'from_resource': under_resource['resource_id'],
                            'to_resource': over_resource['resource_id'],
                            'skill': over_skill,
                            'reason': f"Move {under_resource['resource_name']} work to balance {over_resource['resource_name']}'s allocation"
                        })
        
        return suggestions
    
    def _find_resources_by_skill(
        self,
        skill: str,
        count: int
    ) -> List[Dict]:
        """Find resources with specific skill, sorted by availability."""
        matching = [
            r for r in self.resources_data
            if r.get('skill_category', '').lower() == skill.lower()
        ]
        
        # Sort by availability (lowest allocation first)
        matching.sort(key=lambda r: r.get('current_allocation', 0))
        
        return matching[:count]
    
    def _calculate_allocation(
        self,
        current: float,
        max_alloc: float,
        priority: str
    ) -> float:
        """Calculate recommended allocation."""
        # Priority-based allocation
        priority_boost = {
            'Critical': 0.9,
            'High': 0.75,
            'Medium': 0.6,
            'Low': 0.4
        }
        
        target_alloc = priority_boost.get(priority, 0.6)
        
        # Don't exceed max allocation
        if current + target_alloc > max_alloc:
            return max_alloc
        
        return min(max_alloc, current + target_alloc)
    
    def _assess_conflict_risk(
        self,
        resource_id: str,
        current_alloc: float,
        recommended_alloc: float
    ) -> str:
        """Assess risk of resource conflicts."""
        if recommended_alloc > 0.95:
            return 'High'
        elif recommended_alloc > 0.8:
            return 'Medium'
        elif recommended_alloc > 0.6:
            return 'Low'
        else:
            return 'None'
    
    def _calculate_efficiency_gain(
        self,
        skill_level: str,
        current: float,
        recommended: float
    ) -> float:
        """Calculate efficiency gain from new allocation."""
        # Expert resources are more efficient
        skill_multiplier = {
            'Expert': 1.2,
            'Senior': 1.0,
            'Mid-level': 0.8,
            'Junior': 0.6
        }
        
        multiplier = skill_multiplier.get(skill_level, 1.0)
        allocation_increase = (recommended - current) * 100
        
        return allocation_increase * (multiplier / 100)


def create_resource_optimizer(resources_data: List[Dict]) -> ResourceOptimizerAgent:
    """Factory function to create resource optimizer agent."""
    return ResourceOptimizerAgent(resources_data)


logger.info("Resource Optimizer Agent module initialized")
