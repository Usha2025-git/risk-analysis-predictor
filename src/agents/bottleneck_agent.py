"""
Bottleneck Detector Agent for identifying workflow bottlenecks.
"""
import logging
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from src.utils import Bottleneck

logger = logging.getLogger(__name__)


class BottleneckDetectorAgent:
    """Detects bottlenecks in project workflows and dependencies."""
    
    def __init__(self, historical_projects: List[Dict], incidents: List[Dict]):
        self.historical_projects = historical_projects
        self.incidents = incidents
        # Pre-index incident text for faster keyword matching during analysis
        self._incident_ids_by_token: Dict[str, set[int]] = {}
        self._high_incident_ids_by_token: Dict[str, set[int]] = {}
        self._build_incident_token_index()
        logger.info("Initialized BottleneckDetectorAgent")

    def _build_incident_token_index(self) -> None:
        """Build inverted index from token -> incident ids (and high severity incident ids)."""
        if not self.incidents:
            self._incident_ids_by_token = {}
            self._high_incident_ids_by_token = {}
            return

        incident_ids_by_token: Dict[str, set[int]] = {}
        high_ids_by_token: Dict[str, set[int]] = {}

        for idx, inc in enumerate(self.incidents):
            desc = (inc.get('description') or '')
            tokens = set(re.findall(r"[a-z0-9]+", desc.lower()))
            if not tokens:
                continue

            severity = (inc.get('severity') or '').strip()
            is_high = severity in {"Critical", "High"}

            for tok in tokens:
                incident_ids_by_token.setdefault(tok, set()).add(idx)
                if is_high:
                    high_ids_by_token.setdefault(tok, set()).add(idx)

        self._incident_ids_by_token = incident_ids_by_token
        self._high_incident_ids_by_token = high_ids_by_token
    
    def analyze_project_bottlenecks(
        self,
        project_id: str,
        project_data: Dict,
        workflow_tasks: List[Dict] = None,
        similar_projects: List[Dict] = None
    ) -> List[Bottleneck]:
        """
        Analyze bottlenecks in project workflow.
        
        Args:
            project_id: Project identifier
            project_data: Project details
            workflow_tasks: List of tasks with dependencies
            similar_projects: Historical projects for comparison
        
        Returns:
            List of identified bottlenecks
        """
        bottlenecks = []
        
        # Use default workflow if not provided
        if workflow_tasks is None:
            workflow_tasks = self._create_default_workflow(project_data)
        
        # Analyze each task
        for idx, task in enumerate(workflow_tasks):
            bottleneck = self._analyze_task_bottleneck(
                task,
                idx,
                workflow_tasks,
                project_data,
                similar_projects or []
            )
            
            if bottleneck:
                bottlenecks.append(bottleneck)
        
        # Identify critical path issues
        critical_path_bottleneck = self._analyze_critical_path(workflow_tasks, project_data)
        if critical_path_bottleneck:
            bottlenecks.append(critical_path_bottleneck)
        
        # Identify resource contention
        resource_bottlenecks = self._identify_resource_contentions(workflow_tasks, project_data)
        bottlenecks.extend(resource_bottlenecks)
        
        # Sort by severity
        severity_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
        bottlenecks.sort(
            key=lambda x: (severity_order.get(x.severity, 4), x.expected_delay_days),
            reverse=True
        )
        
        logger.info(f"Identified {len(bottlenecks)} bottlenecks for {project_id}")
        return bottlenecks[:10]  # Return top 10 bottlenecks
    
    def predict_delays(
        self,
        project_data: Dict,
        similar_projects: List[Dict]
    ) -> Dict:
        """
        Predict potential delays based on historical patterns.
        
        Returns:
            Dictionary with delay predictions
        """
        if not similar_projects:
            return {
                'expected_delay_days': 0,
                'delay_probability': 0.0,
                'confidence': 0.0,
                'reasoning': 'No similar historical projects'
            }
        
        # Calculate average delay from similar projects
        delays = [p.get('delays_days', 0) for p in similar_projects]
        avg_delay = sum(delays) / len(delays) if delays else 0
        
        # Calculate probability
        projects_with_delays = sum(1 for d in delays if d > 5)
        delay_probability = (projects_with_delays / len(similar_projects)) * 100 if similar_projects else 0
        
        # Assess confidence based on similarity
        confidence = min(0.9, len(similar_projects) / 10)
        
        # Get reasoning
        team_size = project_data.get('team_size', 5)
        reasoning = f"Based on {len(similar_projects)} similar projects with team size ~{team_size}"
        
        return {
            'expected_delay_days': int(avg_delay),
            'delay_probability': delay_probability,
            'confidence': confidence,
            'reasoning': reasoning,
            'similar_projects': len(similar_projects)
        }
    
    def identify_parallel_opportunities(
        self,
        workflow_tasks: List[Dict]
    ) -> List[Tuple[str, str]]:
        """
        Identify opportunities to parallelize tasks.
        
        Returns:
            List of (task1, task2) tuples that can be executed in parallel
        """
        opportunities = []
        
        for i, task1 in enumerate(workflow_tasks):
            for task2 in workflow_tasks[i+1:]:
                # Check if tasks have no dependencies between them
                task1_deps = task1.get('dependencies', [])
                task2_deps = task2.get('dependencies', [])
                
                task1_name = task1.get('name', f'Task {i}')
                task2_name = task2.get('name', f'Task {i+1}')
                
                # Can parallelize if no dependency chain
                if (task2_name not in task1_deps and 
                    task1_name not in task2_deps):
                    opportunities.append((task1_name, task2_name))
        
        return opportunities
    
    def suggest_mitigation(self, bottleneck: Bottleneck) -> List[str]:
        """Suggest mitigation strategies for a bottleneck."""
        suggestions = []
        
        severity = bottleneck.severity
        root_cause = bottleneck.root_cause.lower()
        
        # Generic mitigations
        if severity in ['Critical', 'High']:
            suggestions.append('Assign additional senior resources to unblock this task')
        
        # Cause-specific mitigations
        if 'resource' in root_cause:
            suggestions.append('Cross-train team members to reduce resource dependency')
            suggestions.append('Consider contractor/augmented staffing')
        
        if 'dependency' in root_cause or 'waiting' in root_cause:
            suggestions.append('Parallelize dependencies where possible')
            suggestions.append('Implement concurrent task execution strategy')
        
        if 'technical' in root_cause or 'complexity' in root_cause:
            suggestions.append('Conduct technical spike to reduce uncertainty')
            suggestions.append('Break down complex task into smaller sub-tasks')
        
        if 'vendor' in root_cause or 'third' in root_cause:
            suggestions.append('Establish direct communication with vendor')
            suggestions.append('Plan for vendor delays in schedule')
        
        # Recommendation from bottleneck
        if bottleneck.mitigation_recommendation:
            suggestions.append(bottleneck.mitigation_recommendation)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _analyze_task_bottleneck(
        self,
        task: Dict,
        task_index: int,
        all_tasks: List[Dict],
        project_data: Dict,
        similar_projects: List[Dict]
    ) -> Optional[Bottleneck]:
        """Analyze if a task is a bottleneck."""
        task_name = task.get('name', f'Task {task_index}')
        dependencies = task.get('dependencies', [])
        estimated_days = task.get('duration_days', 5)
        
        # Assess severity factors
        severity_factors = 0
        
        # Factor 1: Many dependencies (blocking many tasks)
        dependent_count = sum(
            1 for t in all_tasks
            if task_name in t.get('dependencies', [])
        )
        if dependent_count > 3:
            severity_factors += 2
        
        # Factor 2: Long duration
        if estimated_days > 14:
            severity_factors += 2
        elif estimated_days > 7:
            severity_factors += 1
        
        # Factor 3: Complex dependencies
        if len(dependencies) > 2:
            severity_factors += 1
        
        # Factor 4: Historical risk
        task_tokens = set(re.findall(r"[a-z0-9]+", task_name.lower()))
        if task_tokens and self._incident_ids_by_token:
            related_ids = set()
            high_ids = set()
            for tok in task_tokens:
                related_ids |= self._incident_ids_by_token.get(tok, set())
                high_ids |= self._high_incident_ids_by_token.get(tok, set())

            if high_ids:
                # Increase severity based on unique high-severity incidents touching this task area.
                severity_factors += len(high_ids)
        else:
            related_ids = set()
            high_ids = set()
        
        # Determine severity
        if severity_factors > 4:
            severity = 'Critical'
        elif severity_factors > 2:
            severity = 'High'
        elif severity_factors > 1:
            severity = 'Medium'
        else:
            return None  # Not a bottleneck
        
        # Expected delay
        expected_delay = (severity_factors * 2) + (len(dependencies) * 1)
        
        # Determine root cause
        if dependent_count > 2:
            root_cause = f'Critical task blocking {dependent_count} downstream tasks'
        elif len(dependencies) > 2:
            root_cause = f'Multiple dependencies ({len(dependencies)}) create scheduling complexity'
        elif high_ids:
            root_cause = f'{len(high_ids)} historical high-severity incidents in this area'
        else:
            root_cause = 'Extended duration creates schedule pressure'
        
        return Bottleneck(
            bottleneck_id=f'BN_{task_index}',
            task_name=task_name,
            severity=severity,
            expected_delay_days=expected_delay,
            root_cause=root_cause,
            mitigation_recommendation=self._suggest_task_mitigation(task, dependent_count),
            parallel_task_opportunity=self._find_parallel_task(task, all_tasks)
        )
    
    def _analyze_critical_path(
        self,
        workflow_tasks: List[Dict],
        project_data: Dict
    ) -> Optional[Bottleneck]:
        """Analyze critical path for bottlenecks."""
        if not workflow_tasks:
            return None
        
        # Simplified critical path analysis
        critical_path_length = sum(t.get('duration_days', 5) for t in workflow_tasks)
        planned_duration = project_data.get('planned_duration_days', 90)
        
        if critical_path_length > planned_duration * 0.8:
            return Bottleneck(
                bottleneck_id='BN_CRIT_PATH',
                task_name='Critical Path',
                severity='High',
                expected_delay_days=int((critical_path_length - planned_duration) * 1.2),
                root_cause=f'Critical path length ({critical_path_length} days) exceeds planned duration ({planned_duration} days)',
                mitigation_recommendation='Parallelize non-dependent tasks, reduce scope, or extend timeline',
                parallel_task_opportunity='Review task dependencies for parallelization opportunities'
            )
        
        return None
    
    def _identify_resource_contentions(
        self,
        workflow_tasks: List[Dict],
        project_data: Dict
    ) -> List[Bottleneck]:
        """Identify resource contentions."""
        bottlenecks = []
        
        # Group tasks by required skill
        by_skill = {}
        for idx, task in enumerate(workflow_tasks):
            skill = task.get('required_skill', 'General')
            if skill not in by_skill:
                by_skill[skill] = []
            by_skill[skill].append((idx, task))
        
        # Check for contention
        for skill, tasks in by_skill.items():
            if len(tasks) > 3:
                # Multiple tasks competing for same skill
                bottlenecks.append(Bottleneck(
                    bottleneck_id=f'BN_{skill.upper()}',
                    task_name=f'{skill} Resource Contention',
                    severity='Medium',
                    expected_delay_days=len(tasks),
                    root_cause=f'{len(tasks)} tasks require {skill} expertise',
                    mitigation_recommendation=f'Cross-train additional team members in {skill}',
                    parallel_task_opportunity=f'Some {skill} tasks may be parallelizable'
                ))
        
        return bottlenecks
    
    def _create_default_workflow(self, project_data: Dict) -> List[Dict]:
        """Create a default workflow based on project type."""
        phase = project_data.get('project_phase', 'Development')
        industry = project_data.get('industry', 'Technology')
        
        default_workflows = {
            'Design': [
                {'name': 'Requirements Gathering', 'duration_days': 7, 'dependencies': []},
                {'name': 'Wireframing', 'duration_days': 10, 'dependencies': ['Requirements Gathering']},
                {'name': 'Design Review', 'duration_days': 5, 'dependencies': ['Wireframing']},
            ],
            'Development': [
                {'name': 'Architecture Design', 'duration_days': 7, 'dependencies': []},
                {'name': 'Backend Development', 'duration_days': 20, 'dependencies': ['Architecture Design']},
                {'name': 'Frontend Development', 'duration_days': 20, 'dependencies': ['Architecture Design']},
                {'name': 'Integration', 'duration_days': 10, 'dependencies': ['Backend Development', 'Frontend Development']},
                {'name': 'Testing', 'duration_days': 14, 'dependencies': ['Integration']},
            ],
            'Deployment': [
                {'name': 'Environment Setup', 'duration_days': 5, 'dependencies': []},
                {'name': 'Deployment Planning', 'duration_days': 3, 'dependencies': ['Environment Setup']},
                {'name': 'Production Deployment', 'duration_days': 2, 'dependencies': ['Deployment Planning']},
            ]
        }
        
        return default_workflows.get(phase, default_workflows['Development'])
    
    def _suggest_task_mitigation(self, task: Dict, dependent_count: int) -> str:
        """Suggest mitigation for a specific task."""
        if dependent_count > 2:
            return 'Expedite this task - it blocks multiple downstream tasks'
        else:
            return 'Monitor progress closely and allocate buffer time'
    
    def _find_parallel_task(self, task: Dict, all_tasks: List[Dict]) -> Optional[str]:
        """Find a task that can be parallelized with given task."""
        task_name = task.get('name', '')
        task_deps = task.get('dependencies', [])
        
        for t in all_tasks:
            t_name = t.get('name', '')
            t_deps = t.get('dependencies', [])
            
            if t_name == task_name:
                continue
            
            # Can parallelize if no dependency relationship
            if task_name not in t_deps and t_name not in task_deps:
                return t_name
        
        return None


def create_bottleneck_detector(
    historical_projects: List[Dict],
    incidents: List[Dict]
) -> BottleneckDetectorAgent:
    """Factory function to create bottleneck detector agent."""
    return BottleneckDetectorAgent(historical_projects, incidents)


logger.info("Bottleneck Detector Agent module initialized")
