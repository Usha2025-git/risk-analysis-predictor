"""
Orchestrator Agent - Coordinates all specialized agents and synthesizes insights.
"""
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from src.utils import ProjectAnalysis, get_current_timestamp
from src.agents.risk_agent import RiskAnalyzerAgent
from src.agents.resource_agent import ResourceOptimizerAgent
from src.agents.bottleneck_agent import BottleneckDetectorAgent
from src.data_ingestion import DataIngestor
from src.embeddings import ProjectEmbedder

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """
    Orchestrator agent that coordinates all specialized agents.
    Synthesizes findings into actionable insights and recommendations.
    """
    
    def __init__(
        self,
        risk_analyzer: RiskAnalyzerAgent,
        resource_optimizer: ResourceOptimizerAgent,
        bottleneck_detector: BottleneckDetectorAgent,
        data_ingestor: DataIngestor,
        project_embedder: ProjectEmbedder
    ):
        self.risk_analyzer = risk_analyzer
        self.resource_optimizer = resource_optimizer
        self.bottleneck_detector = bottleneck_detector
        self.data_ingestor = data_ingestor
        self.project_embedder = project_embedder
        logger.info("Initialized OrchestratorAgent")
    
    def analyze_project(
        self,
        project_id: str,
        project_data: Dict,
        workflow_tasks: List[Dict] = None,
        current_allocations: Dict[str, float] = None
    ) -> ProjectAnalysis:
        """
        Comprehensive project analysis orchestrating all agents.
        
        Args:
            project_id: Project identifier
            project_data: Complete project details
            workflow_tasks: Project workflow tasks (optional)
            current_allocations: Current resource allocations (optional)
        
        Returns:
            ProjectAnalysis with insights from all agents
        """
        logger.info(f"Starting comprehensive analysis for project {project_id}")
        
        # Step 1: Retrieve similar historical projects
        similar_projects = self._get_similar_projects(project_data)
        logger.info(f"Found {len(similar_projects)} similar historical projects")
        
        # Step 2: Get related incidents
        related_incidents = self.data_ingestor.get_incidents_for_project(project_id)
        logger.info(f"Found {len(related_incidents)} related incidents")
        
        # Step 3: Run Risk Analysis
        risks = self.risk_analyzer.analyze_project_risks(
            project_data,
            similar_projects,
            related_incidents
        )
        logger.info(f"Completed risk analysis: {len(risks)} risks identified")
        
        # Step 4: Run Resource Optimization
        project_requirements = self._extract_project_requirements(project_data)
        resource_recommendations = self.resource_optimizer.optimize_allocation(
            project_id,
            project_requirements,
            current_allocations
        )
        logger.info(f"Completed resource optimization: {len(resource_recommendations)} recommendations")
        
        # Step 5: Run Bottleneck Detection
        bottlenecks = self.bottleneck_detector.analyze_project_bottlenecks(
            project_id,
            project_data,
            workflow_tasks,
            similar_projects
        )
        logger.info(f"Completed bottleneck detection: {len(bottlenecks)} bottlenecks identified")
        
        # Step 6: Calculate overall risk score
        overall_risk_score = self._calculate_overall_risk_score(risks, bottlenecks)
        
        # Step 7: Calculate confidence level
        confidence_level = self._calculate_confidence(
            len(similar_projects),
            len(related_incidents)
        )
        
        # Step 8: Generate executive summary
        executive_summary = self._generate_executive_summary(
            project_data,
            risks,
            bottlenecks,
            resource_recommendations
        )
        
        # Step 9: Generate top recommendations
        top_recommendations = self._synthesize_recommendations(
            risks,
            bottlenecks,
            resource_recommendations
        )
        
        # Create analysis result
        analysis = ProjectAnalysis(
            project_id=project_id,
            analysis_timestamp=get_current_timestamp(),
            risks=risks,
            resource_recommendations=resource_recommendations,
            bottlenecks=bottlenecks,
            overall_risk_score=overall_risk_score,
            confidence_level=confidence_level,
            executive_summary=executive_summary,
            top_recommendations=top_recommendations
        )
        
        logger.info(f"Completed comprehensive analysis for {project_id}")
        return analysis
    
    def generate_report(self, analysis: ProjectAnalysis) -> str:
        """Generate a formatted report from the analysis."""
        report = f"""
================================================================================
PROJECT ANALYSIS REPORT
================================================================================
Project ID: {analysis.project_id}
Analysis Timestamp: {analysis.analysis_timestamp}
Overall Risk Score: {analysis.overall_risk_score:.1f}/100
Confidence Level: {analysis.confidence_level:.1%}

================================================================================
EXECUTIVE SUMMARY
================================================================================
{analysis.executive_summary}

================================================================================
TOP RECOMMENDATIONS
================================================================================
"""
        for idx, rec in enumerate(analysis.top_recommendations, 1):
            report += f"{idx}. {rec}\n"
        
        report += f"""
================================================================================
IDENTIFIED RISKS (Top 5)
================================================================================
"""
        for idx, risk in enumerate(analysis.risks[:5], 1):
            report += f"""
{idx}. {risk.risk_type.upper()}: {risk.description}
   - Probability: {risk.probability:.0f}%
   - Impact: {risk.impact}
   - Confidence: {risk.confidence_score:.1%}
   - Mitigation: {risk.mitigation_strategy}
"""
        
        report += f"""
================================================================================
BOTTLENECKS IDENTIFIED (Top 5)
================================================================================
"""
        for idx, bn in enumerate(analysis.bottlenecks[:5], 1):
            report += f"""
{idx}. {bn.task_name} (Severity: {bn.severity})
   - Expected Delay: {bn.expected_delay_days} days
   - Root Cause: {bn.root_cause}
   - Mitigation: {bn.mitigation_recommendation}
"""
        
        report += f"""
================================================================================
RESOURCE RECOMMENDATIONS (Top 5)
================================================================================
"""
        for idx, rec in enumerate(analysis.resource_recommendations[:5], 1):
            report += f"""
{idx}. {rec.resource_name} ({rec.resource_id})
   - Current Allocation: {rec.current_allocation:.0%}
   - Recommended: {rec.recommended_allocation:.0%}
   - Conflict Risk: {rec.conflict_risk}
   - Efficiency Gain: {rec.efficiency_gain:.1f}%
   - Justification: {rec.justification}
"""
        
        report += "\n================================================================================\n"
        return report
    
    def create_action_plan(self, analysis: ProjectAnalysis) -> Dict:
        """Create an action plan based on the analysis."""
        action_plan = {
            'project_id': analysis.project_id,
            'created_at': get_current_timestamp(),
            'phases': [
                {
                    'phase': 'Immediate Actions (Next 1 week)',
                    'actions': self._get_immediate_actions(analysis)
                },
                {
                    'phase': 'Short-term Actions (1-2 weeks)',
                    'actions': self._get_short_term_actions(analysis)
                },
                {
                    'phase': 'Medium-term Actions (2-4 weeks)',
                    'actions': self._get_medium_term_actions(analysis)
                },
                {
                    'phase': 'Long-term Monitoring',
                    'actions': self._get_long_term_actions(analysis)
                }
            ],
            'success_metrics': self._define_success_metrics(analysis)
        }
        return action_plan
    
    def _get_similar_projects(self, project_data: Dict) -> List[Dict]:
        """Get similar historical projects."""
        industry = project_data.get('industry')
        team_size = project_data.get('team_size', 10)
        
        return self.data_ingestor.get_similar_projects(
            project_id=project_data.get('project_id', ''),
            industry=industry,
            team_size_range=(max(3, team_size - 5), team_size + 5),
            limit=10
        )
    
    def _extract_project_requirements(self, project_data: Dict) -> Dict:
        """Extract project requirements from project data."""
        return {
            'required_skills': {
                'Backend Development': 2,
                'Frontend Development': 2,
                'QA Engineering': 1,
                'DevOps': 1,
                'Project Management': 1
            },
            'team_size': project_data.get('team_size', 5),
            'priority': self._determine_priority(project_data),
            'duration': project_data.get('planned_duration_days', 90)
        }
    
    def _determine_priority(self, project_data: Dict) -> str:
        """Determine project priority based on characteristics."""
        budget = project_data.get('budget', 0)
        team_size = project_data.get('team_size', 5)
        
        if budget > 300000 or team_size > 15:
            return 'Critical'
        elif budget > 150000 or team_size > 10:
            return 'High'
        else:
            return 'Medium'
    
    def _calculate_overall_risk_score(
        self,
        risks: List,
        bottlenecks: List
    ) -> float:
        """Calculate overall project risk score."""
        if not risks and not bottlenecks:
            return 25.0
        
        # Weight risks and bottlenecks
        risk_score = sum(r.probability * (0.5 if r.impact == 'Low' else 
                                          1.0 if r.impact == 'Medium' else 
                                          1.5 if r.impact == 'High' else 2.0)
                        for r in risks) / (len(risks) * 100) if risks else 0
        
        bottleneck_score = sum(1 if b.severity == 'Critical' else 
                              0.75 if b.severity == 'High' else
                              0.5 for b in bottlenecks) / (len(bottlenecks) * 2) if bottlenecks else 0
        
        overall_score = (risk_score * 0.6 + bottleneck_score * 0.4) * 100
        return min(100.0, max(0.0, overall_score))
    
    def _calculate_confidence(
        self,
        similar_projects_count: int,
        incidents_count: int
    ) -> float:
        """Calculate confidence level of analysis."""
        # More similar projects = more confidence
        projects_confidence = min(0.8, similar_projects_count / 10)
        
        # More incidents = more data points
        incidents_confidence = min(0.7, incidents_count / 20)
        
        return (projects_confidence * 0.6 + incidents_confidence * 0.4)
    
    def _generate_executive_summary(
        self,
        project_data: Dict,
        risks: List,
        bottlenecks: List,
        resources: List
    ) -> str:
        """Generate executive summary of analysis."""
        project_name = project_data.get('project_name', 'Project')
        team_size = project_data.get('team_size', 'Unknown')
        budget = project_data.get('budget', 0)

        def _is_critical_risk(r) -> bool:
            # Risks may be model instances or dicts depending on caller.
            if isinstance(r, dict):
                return r.get('severity') == 'Critical' or r.get('impact') == 'Critical'
            return getattr(r, 'severity', None) == 'Critical' or getattr(r, 'impact', None) == 'Critical'

        critical_risks = sum(1 for r in risks if _is_critical_risk(r))
        critical_bottlenecks = sum(1 for b in bottlenecks if b.severity == 'Critical')
        
        summary = f"""
{project_name} is a {budget:,}-budget project with a team of {team_size}. 
Analysis identified {len(risks)} key risks and {len(bottlenecks)} workflow bottlenecks.

Key Findings:
- {critical_risks} critical risks requiring immediate attention
- {critical_bottlenecks} critical bottlenecks that could impact schedule
- {len(resources)} resource optimization opportunities identified

The project shows {'high' if len(risks) > 3 or critical_risks > 0 else 'moderate' if len(risks) > 1 else 'low'} risk profile 
based on historical patterns of similar projects. Early action on identified mitigations 
is recommended to keep the project on track.
"""
        return summary
    
    def _synthesize_recommendations(
        self,
        risks: List,
        bottlenecks: List,
        resources: List
    ) -> List[str]:
        """Synthesize top-level recommendations from all analyses."""
        recommendations = []
        
        # Top risk recommendations
        if risks:
            top_risk = risks[0]
            recommendations.append(
                f"Address top risk ({top_risk.risk_type}): {top_risk.mitigation_strategy}"
            )
        
        # Critical bottleneck recommendations
        critical_bns = [b for b in bottlenecks if b.severity == 'Critical']
        if critical_bns:
            recommendations.append(
                f"Resolve {len(critical_bns)} critical bottleneck(s) immediately: {critical_bns[0].task_name}"
            )
        
        # Resource recommendations
        over_allocated = [r for r in resources if r.conflict_risk == 'High']
        if over_allocated:
            recommendations.append(
                f"Rebalance resource allocation to reduce conflicts ({len(over_allocated)} resources overallocated)"
            )
        
        # Schedule recommendations
        avg_delay = sum(b.expected_delay_days for b in bottlenecks) / len(bottlenecks) if bottlenecks else 0
        if avg_delay > 10:
            recommendations.append(
                f"Plan for {int(avg_delay)} days of schedule buffer based on bottleneck analysis"
            )
        
        # General recommendations
        recommendations.append("Establish weekly risk and progress reviews with stakeholders")
        recommendations.append("Implement automated progress tracking and early warning systems")
        
        return recommendations[:5]  # Top 5
    
    def _get_immediate_actions(self, analysis: ProjectAnalysis) -> List[Dict]:
        """Get immediate actions (within 1 week)."""
        actions = []
        
        # Address critical risks
        critical_risks = [r for r in analysis.risks if r.impact == 'Critical']
        for risk in critical_risks:
            actions.append({
                'action': f'Implement mitigation for {risk.risk_type}',
                'owner': 'Project Manager',
                'deadline': 'Today',
                'description': risk.mitigation_strategy
            })
        
        # Address critical bottlenecks
        critical_bns = [b for b in analysis.bottlenecks if b.severity == 'Critical']
        for bn in critical_bns[:1]:
            actions.append({
                'action': f'Expedite {bn.task_name}',
                'owner': 'Technical Lead',
                'deadline': 'This week',
                'description': bn.mitigation_recommendation
            })
        
        # Rebalance critical resource issues
        critical_resources = [r for r in analysis.resource_recommendations if r.conflict_risk == 'High']
        if critical_resources:
            actions.append({
                'action': 'Resolve critical resource conflicts',
                'owner': 'Resource Manager',
                'deadline': 'This week',
                'description': f'Rebalance {len(critical_resources)} overallocated resources'
            })
        
        return actions
    
    def _get_short_term_actions(self, analysis: ProjectAnalysis) -> List[Dict]:
        """Get short-term actions (1-2 weeks)."""
        actions = []
        
        # Medium-level risk mitigations
        medium_risks = [r for r in analysis.risks if r.impact == 'High']
        if medium_risks:
            actions.append({
                'action': 'Establish risk monitoring for high-impact risks',
                'owner': 'Project Manager',
                'deadline': 'Week 2',
                'description': f'Weekly tracking of {len(medium_risks)} high-impact risks'
            })
        
        # Bottleneck prevention
        high_bns = [b for b in analysis.bottlenecks if b.severity in ['High', 'Medium']]
        if high_bns:
            actions.append({
                'action': 'Implement bottleneck prevention measures',
                'owner': 'Technical Lead',
                'deadline': 'Week 2',
                'description': f'Parallelize opportunities and add buffers for {len(high_bns)} bottlenecks'
            })
        
        # Resource optimization
        actions.append({
            'action': 'Implement recommended resource allocation',
            'owner': 'Resource Manager',
            'deadline': 'Week 2',
            'description': 'Update project staffing per optimization recommendations'
        })
        
        return actions
    
    def _get_medium_term_actions(self, analysis: ProjectAnalysis) -> List[Dict]:
        """Get medium-term actions (2-4 weeks)."""
        return [
            {
                'action': 'Schedule stakeholder review meeting',
                'owner': 'Project Manager',
                'deadline': 'Week 3',
                'description': 'Present analysis findings and action plan to stakeholders'
            },
            {
                'action': 'Establish automated monitoring dashboards',
                'owner': 'DevOps Lead',
                'deadline': 'Week 4',
                'description': 'Set up dashboards for risk, resource, and bottleneck tracking'
            },
            {
                'action': 'Conduct team training on identified risks',
                'owner': 'Project Manager',
                'deadline': 'Week 4',
                'description': 'Educate team on risk mitigation strategies'
            }
        ]
    
    def _get_long_term_actions(self, analysis: ProjectAnalysis) -> List[Dict]:
        """Get long-term monitoring actions."""
        return [
            {
                'action': 'Weekly risk and progress reviews',
                'owner': 'Project Manager',
                'deadline': 'Ongoing',
                'description': 'Monitor against identified risks and bottlenecks'
            },
            {
                'action': 'Monthly resource utilization reviews',
                'owner': 'Resource Manager',
                'deadline': 'Ongoing',
                'description': 'Ensure resource recommendations remain effective'
            },
            {
                'action': 'Post-project analysis and lessons learned',
                'owner': 'Project Manager',
                'deadline': 'Project close',
                'description': 'Document lessons for future similar projects'
            }
        ]
    
    def _define_success_metrics(self, analysis: ProjectAnalysis) -> Dict:
        """Define success metrics for the project."""
        return {
            'schedule_success': {
                'metric': 'Delay days',
                'target': 0,
                'threshold': 5,
                'tracking': 'Weekly'
            },
            'budget_success': {
                'metric': 'Cost variance %',
                'target': 0,
                'threshold': 10,
                'tracking': 'Bi-weekly'
            },
            'risk_mitigation': {
                'metric': 'Critical risks mitigated',
                'target': '100%',
                'tracking': 'Weekly'
            },
            'bottleneck_resolution': {
                'metric': 'Critical bottlenecks resolved',
                'target': '100%',
                'tracking': 'Weekly'
            },
            'resource_utilization': {
                'metric': 'Optimal allocation achieved',
                'target': '100%',
                'tracking': 'Bi-weekly'
            }
        }


def create_orchestrator(
    risk_analyzer: RiskAnalyzerAgent,
    resource_optimizer: ResourceOptimizerAgent,
    bottleneck_detector: BottleneckDetectorAgent,
    data_ingestor: DataIngestor,
    project_embedder: ProjectEmbedder
) -> OrchestratorAgent:
    """Factory function to create orchestrator agent."""
    return OrchestratorAgent(
        risk_analyzer,
        resource_optimizer,
        bottleneck_detector,
        data_ingestor,
        project_embedder
    )


logger.info("Orchestrator Agent module initialized")
