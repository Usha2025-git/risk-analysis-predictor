"""
Risk Analyzer Agent for predicting project risks.
"""
import logging
from typing import List, Dict, Tuple
from src.utils import (
    RiskPrediction,
    estimate_risk_probability,
    estimate_impact_level,
    create_project_context
)
from src.embeddings import ProjectEmbedder

logger = logging.getLogger(__name__)


class RiskAnalyzerAgent:
    """Analyzes project risks based on historical data and similar projects."""
    
    RISK_CATEGORIES = {
        'schedule': 'Schedule Risk',
        'budget': 'Budget Risk',
        'resource': 'Resource Risk',
        'technical': 'Technical Risk',
        'compliance': 'Compliance Risk',
        'vendor': 'Vendor/Third-party Risk'
    }
    
    def __init__(
        self,
        project_embedder: ProjectEmbedder,
        historical_projects: List[Dict],
        incidents: List[Dict]
    ):
        self.project_embedder = project_embedder
        self.historical_projects = historical_projects
        self.incidents = incidents
        logger.info("Initialized RiskAnalyzerAgent")
    
    def analyze_project_risks(
        self,
        project_data: Dict,
        similar_projects: List[Dict],
        related_incidents: List[Dict]
    ) -> List[RiskPrediction]:
        """
        Analyze risks for a project based on historical data.
        Returns list of RiskPrediction objects.
        """
        risks = []
        
        # Schedule Risk
        schedule_risk = self._analyze_schedule_risk(project_data, similar_projects)
        if schedule_risk:
            risks.append(schedule_risk)
        
        # Budget Risk
        budget_risk = self._analyze_budget_risk(project_data, similar_projects)
        if budget_risk:
            risks.append(budget_risk)
        
        # Resource Risk
        resource_risk = self._analyze_resource_risk(project_data, related_incidents)
        if resource_risk:
            risks.append(resource_risk)
        
        # Technical Risk
        technical_risk = self._analyze_technical_risk(project_data, related_incidents)
        if technical_risk:
            risks.append(technical_risk)
        
        # Compliance Risk
        compliance_risk = self._analyze_compliance_risk(project_data, related_incidents)
        if compliance_risk:
            risks.append(compliance_risk)
        
        # Vendor Risk
        vendor_risk = self._analyze_vendor_risk(project_data, related_incidents)
        if vendor_risk:
            risks.append(vendor_risk)
        
        # Sort by probability
        risks.sort(key=lambda x: x.probability, reverse=True)
        
        logger.info(f"Analyzed {len(risks)} risks for project {project_data.get('project_id')}")
        return risks[:5]  # Top 5 risks
    
    def _analyze_schedule_risk(
        self,
        project_data: Dict,
        similar_projects: List[Dict]
    ) -> RiskPrediction:
        """Analyze schedule/timeline risk."""
        if not similar_projects:
            return RiskPrediction(
                risk_type='schedule',
                probability=50.0,
                impact='Medium',
                description='Insufficient historical data for schedule risk assessment',
                mitigation_strategy='Establish clear milestones and regular tracking',
                confidence_score=0.3,
                reasoning='No similar historical projects found'
            )
        
        # Calculate probability based on historical delays
        projects_with_delays = sum(
            1 for p in similar_projects if p.get('delays_days', 0) > 5
        )
        probability = estimate_risk_probability(
            projects_with_delays,
            len(similar_projects),
            confidence_adjustment=0.9
        )
        
        # Calculate average delay from similar projects
        avg_delay = sum(p.get('delays_days', 0) for p in similar_projects) / len(similar_projects)
        impact = estimate_impact_level(avg_delay, 0)
        
        planned_duration = project_data.get('planned_duration_days', 1)
        if planned_duration == 0:
            planned_duration = 1
        
        confidence_score = min(0.9, len(similar_projects) / 10)
        
        return RiskPrediction(
            risk_type='schedule',
            probability=probability,
            impact=impact,
            description=f'Based on {len(similar_projects)} similar projects, average delay is {avg_delay:.1f} days',
            mitigation_strategy='Build schedule buffers, use critical path management, establish weekly status reviews',
            confidence_score=confidence_score,
            reasoning=f'{projects_with_delays}/{len(similar_projects)} similar projects experienced delays'
        )
    
    def _analyze_budget_risk(
        self,
        project_data: Dict,
        similar_projects: List[Dict]
    ) -> RiskPrediction:
        """Analyze budget/cost risk."""
        if not similar_projects:
            return RiskPrediction(
                risk_type='budget',
                probability=50.0,
                impact='Medium',
                description='Insufficient historical data for budget risk assessment',
                mitigation_strategy='Implement detailed cost tracking and regular budget reviews',
                confidence_score=0.3,
                reasoning='No similar historical projects found'
            )
        
        # Calculate probability based on cost overruns
        projects_with_overrun = sum(
            1 for p in similar_projects
            if p.get('actual_cost', 0) > p.get('budget', 1)
        )
        probability = estimate_risk_probability(
            projects_with_overrun,
            len(similar_projects),
            confidence_adjustment=0.95
        )
        
        # Calculate average cost variance
        cost_variances = [
            ((p.get('actual_cost', 0) - p.get('budget', 0)) / p.get('budget', 1) * 100)
            for p in similar_projects
            if p.get('budget', 0) > 0
        ]
        
        avg_variance = sum(cost_variances) / len(cost_variances) if cost_variances else 10.0
        impact = estimate_impact_level(0, avg_variance)
        
        confidence_score = min(0.9, len(similar_projects) / 10)
        
        return RiskPrediction(
            risk_type='budget',
            probability=probability,
            impact=impact,
            description=f'Cost overrun averaged {avg_variance:.1f}% in similar projects',
            mitigation_strategy='Conduct detailed cost estimation, establish change control, track actuals weekly',
            confidence_score=confidence_score,
            reasoning=f'{projects_with_overrun}/{len(similar_projects)} similar projects had cost overruns'
        )
    
    def _analyze_resource_risk(
        self,
        project_data: Dict,
        related_incidents: List[Dict]
    ) -> RiskPrediction:
        """Analyze resource availability and skill risk."""
        team_size = project_data.get('team_size', 5)
        
        # Count resource-related incidents
        resource_incidents = [
            i for i in related_incidents
            if i.get('category', '').lower() in ['resource', 'training', 'staffing']
        ]
        
        # Base probability
        base_probability = 40.0 if team_size > 10 else 30.0
        probability = base_probability + (len(resource_incidents) * 15)
        probability = min(100.0, max(0.0, probability))
        
        impact = 'High' if team_size > 15 else 'Medium'
        
        return RiskPrediction(
            risk_type='resource',
            probability=probability,
            impact=impact,
            description=f'Team size of {team_size} identified with {len(resource_incidents)} historical resource incidents',
            mitigation_strategy='Cross-train team members, maintain skill matrices, plan for turnover, use contingency staff',
            confidence_score=0.75,
            reasoning=f'Historical data shows {len(resource_incidents)} resource-related incidents in similar projects'
        )
    
    def _analyze_technical_risk(
        self,
        project_data: Dict,
        related_incidents: List[Dict]
    ) -> RiskPrediction:
        """Analyze technical complexity risk."""
        # Count technical incidents
        technical_incidents = [
            i for i in related_incidents
            if i.get('category', '').lower() == 'technical'
        ]
        
        # Assess by project phase and industry
        industry = project_data.get('industry', '')
        phase = project_data.get('project_phase', '')
        
        # Estimate technical complexity
        high_complexity_industries = ['Technology', 'Finance', 'Data Science', 'Healthcare']
        high_complexity_phases = ['Development', 'Integration', 'Migration']
        
        complexity_factor = 0
        if industry in high_complexity_industries:
            complexity_factor += 20
        if phase in high_complexity_phases:
            complexity_factor += 20
        
        base_probability = 35.0 + complexity_factor
        probability = min(100.0, base_probability + (len(technical_incidents) * 10))
        
        impact = 'Critical' if complexity_factor > 30 else 'High' if complexity_factor > 15 else 'Medium'
        
        return RiskPrediction(
            risk_type='technical',
            probability=probability,
            impact=impact,
            description=f'Technical risk identified in {industry} industry {phase} phase with {len(technical_incidents)} historical incidents',
            mitigation_strategy='Conduct POC/spike for complex components, pair programming, technical review gates, vendor support agreements',
            confidence_score=0.8,
            reasoning=f'{industry} projects in {phase} phase show technical complexity, {len(technical_incidents)} past incidents'
        )
    
    def _analyze_compliance_risk(
        self,
        project_data: Dict,
        related_incidents: List[Dict]
    ) -> RiskPrediction:
        """Analyze regulatory and compliance risk."""
        # Count compliance incidents
        compliance_incidents = [
            i for i in related_incidents
            if i.get('category', '').lower() in ['compliance', 'regulatory', 'security']
        ]
        
        industry = project_data.get('industry', '')
        
        # Industries with high compliance needs
        regulated_industries = ['Finance', 'Healthcare', 'Telecommunications', 'Legal']
        
        probability = 50.0 if industry in regulated_industries else 25.0
        probability += len(compliance_incidents) * 20
        probability = min(100.0, probability)
        
        impact = 'Critical' if industry in regulated_industries else 'High' if len(compliance_incidents) > 0 else 'Medium'
        
        return RiskPrediction(
            risk_type='compliance',
            probability=probability,
            impact=impact,
            description=f'{industry} industry has {len(compliance_incidents)} historical compliance issues',
            mitigation_strategy='Engage compliance experts early, establish audit points, implement security controls, maintain documentation',
            confidence_score=0.85,
            reasoning=f'Regulated industry ({industry}) with {len(compliance_incidents)} historical compliance incidents'
        )
    
    def _analyze_vendor_risk(
        self,
        project_data: Dict,
        related_incidents: List[Dict]
    ) -> RiskPrediction:
        """Analyze third-party and vendor risk."""
        # Count vendor incidents
        vendor_incidents = [
            i for i in related_incidents
            if i.get('category', '').lower() in ['vendor', 'integration', 'coordination']
        ]
        
        base_probability = 30.0 + (len(vendor_incidents) * 15)
        probability = min(100.0, base_probability)
        
        impact = 'High' if len(vendor_incidents) > 0 else 'Medium'
        
        return RiskPrediction(
            risk_type='vendor',
            probability=probability,
            impact=impact,
            description=f'{len(vendor_incidents)} historical vendor-related incidents identified',
            mitigation_strategy='Establish SLAs with vendors, maintain relationships, have backup vendors, clear communication protocols',
            confidence_score=0.8 if len(vendor_incidents) > 0 else 0.5,
            reasoning=f'{len(vendor_incidents)} historical incidents show vendor coordination challenges'
        )


def create_risk_analyzer(
    project_embedder: ProjectEmbedder,
    historical_projects: List[Dict],
    incidents: List[Dict]
) -> RiskAnalyzerAgent:
    """Factory function to create a risk analyzer agent."""
    return RiskAnalyzerAgent(project_embedder, historical_projects, incidents)


logger.info("Risk Analyzer Agent module initialized")
