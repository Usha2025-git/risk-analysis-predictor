"""
Data Ingestion Module for loading and preprocessing project data.
"""
import pandas as pd
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DataIngestor:
    """Handles loading and preprocessing of project data."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.projects_df: Optional[pd.DataFrame] = None
        self.resources_df: Optional[pd.DataFrame] = None
        self.incidents: List[Dict] = []
        # Precomputed indexes for faster lookups during analysis
        self._incidents_by_project_id: Dict[str, List[Dict]] = {}
        self._incidents_by_category: Dict[str, List[Dict]] = {}
    
    def load_projects_csv(self, filename: str = "sample_projects.csv") -> pd.DataFrame:
        """Load projects from CSV file."""
        filepath = self.data_dir / filename
        logger.info(f"Loading projects from {filepath}")
        
        self.projects_df = pd.read_csv(filepath)
        
        # Convert date columns
        date_columns = ['start_date', 'planned_end_date', 'actual_end_date']
        for col in date_columns:
            if col in self.projects_df.columns:
                self.projects_df[col] = pd.to_datetime(self.projects_df[col])
        
        logger.info(f"Loaded {len(self.projects_df)} projects")
        return self.projects_df
    
    def load_resources_csv(self, filename: str = "resource_data.csv") -> pd.DataFrame:
        """Load resources from CSV file."""
        filepath = self.data_dir / filename
        logger.info(f"Loading resources from {filepath}")
        
        self.resources_df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(self.resources_df)} resources")
        return self.resources_df
    
    def load_incidents_json(self, filename: str = "historical_incidents.json") -> List[Dict]:
        """Load historical incidents from JSON file."""
        filepath = self.data_dir / filename
        logger.info(f"Loading incidents from {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.incidents = data.get('incidents', [])
        self._rebuild_incident_indexes()
        logger.info(f"Loaded {len(self.incidents)} incidents")
        return self.incidents

    def _rebuild_incident_indexes(self) -> None:
        """Build in-memory indexes for incident lookup speed."""
        by_project: Dict[str, List[Dict]] = {}
        by_category: Dict[str, List[Dict]] = {}

        for inc in self.incidents:
            pid = str(inc.get('project_id', '') or '')
            cat = str(inc.get('category', '') or '')

            if pid:
                by_project.setdefault(pid, []).append(inc)
            if cat:
                by_category.setdefault(cat, []).append(inc)

        self._incidents_by_project_id = by_project
        self._incidents_by_category = by_category
    
    def load_all(self) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict]]:
        """Load all data sources."""
        self.load_projects_csv()
        self.load_resources_csv()
        self.load_incidents_json()
        return self.projects_df, self.resources_df, self.incidents
    
    def clean_project_data(self) -> pd.DataFrame:
        """Clean and normalize project data."""
        if self.projects_df is None:
            raise ValueError("Projects data not loaded. Call load_projects_csv() first.")
        
        df = self.projects_df.copy()
        
        # Handle missing values
        numeric_columns = ['budget', 'actual_cost', 'team_size', 'delays_days']
        for col in numeric_columns:
            if col in df.columns:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Ensure numeric types
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove duplicates
        df.drop_duplicates(subset=['project_id'], inplace=True)
        
        logger.info(f"Cleaned data: {len(df)} rows remaining")
        return df
    
    def add_calculated_fields(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """Add calculated fields to project data."""
        if df is None:
            if self.projects_df is None:
                raise ValueError("No project data available")
            df = self.projects_df.copy()
        
        # Calculate duration in days
        if 'start_date' in df.columns and 'actual_end_date' in df.columns:
            df['actual_duration_days'] = (df['actual_end_date'] - df['start_date']).dt.days
        
        if 'start_date' in df.columns and 'planned_end_date' in df.columns:
            df['planned_duration_days'] = (df['planned_end_date'] - df['start_date']).dt.days
        
        # Calculate cost variance
        if 'budget' in df.columns and 'actual_cost' in df.columns:
            df['cost_variance'] = ((df['actual_cost'] - df['budget']) / df['budget'] * 100).fillna(0)
            df['cost_variance_amount'] = df['actual_cost'] - df['budget']
        
        # Calculate schedule variance (delay ratio)
        if 'planned_duration_days' in df.columns and 'delays_days' in df.columns:
            df['schedule_variance'] = (df['delays_days'] / df['planned_duration_days'] * 100).fillna(0)
        
        # Categorize risk level based on delays and cost
        def risk_level(row):
            delay_pct = row.get('schedule_variance', 0)
            cost_pct = row.get('cost_variance', 0)
            
            if delay_pct > 30 or cost_pct > 30:
                return 'Critical'
            elif delay_pct > 20 or cost_pct > 20:
                return 'High'
            elif delay_pct > 10 or cost_pct > 10:
                return 'Medium'
            else:
                return 'Low'
        
        df['risk_level'] = df.apply(risk_level, axis=1)
        
        logger.info("Added calculated fields")
        return df
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """Get single project details."""
        if self.projects_df is None:
            return None
        
        project = self.projects_df[self.projects_df['project_id'] == project_id]
        if project.empty:
            return None
        
        return project.iloc[0].to_dict()
    
    def get_similar_projects(
        self,
        project_id: str,
        industry: Optional[str] = None,
        team_size_range: Tuple[int, int] = (5, 20),
        limit: int = 5
    ) -> List[Dict]:
        """Get similar historical projects."""
        if self.projects_df is None:
            return []
        
        current_project = self.get_project_by_id(project_id)
        if not current_project:
            return []
        
        df = self.projects_df.copy()
        
        # Filter by industry if specified
        if industry and 'industry' in df.columns:
            df = df[df['industry'] == industry]
        
        # Filter by team size range
        if 'team_size' in df.columns:
            df = df[
                (df['team_size'] >= team_size_range[0]) &
                (df['team_size'] <= team_size_range[1])
            ]
        
        # Exclude current project
        df = df[df['project_id'] != project_id]
        
        # Return top projects (sorted by similarity)
        return df.head(limit).to_dict('records')
    
    def get_incidents_for_project(self, project_id: str) -> List[Dict]:
        """Get incidents related to a specific project."""
        if self._incidents_by_project_id:
            return list(self._incidents_by_project_id.get(str(project_id), []))
        return [inc for inc in self.incidents if inc.get('project_id') == project_id]
    
    def get_incidents_by_category(self, category: str) -> List[Dict]:
        """Get incidents by category."""
        if self._incidents_by_category:
            return list(self._incidents_by_category.get(str(category), []))
        return [inc for inc in self.incidents if inc.get('category') == category]
    
    def get_statistics(self) -> Dict:
        """Get overall statistics about the data."""
        if self.projects_df is None:
            return {}
        
        df = self.clean_project_data()
        df = self.add_calculated_fields(df)
        
        return {
            'total_projects': len(df),
            'avg_budget': float(df['budget'].mean()),
            'avg_cost_overrun': float(df['cost_variance'].mean()),
            'avg_delay_days': float(df['delays_days'].mean()),
            'avg_team_size': float(df['team_size'].mean()),
            'projects_by_risk_level': df['risk_level'].value_counts().to_dict(),
            'industries': df['industry'].unique().tolist() if 'industry' in df.columns else [],
            'total_incidents': len(self.incidents),
            'incidents_by_severity': self._count_incidents_by_severity(),
        }
    
    def _count_incidents_by_severity(self) -> Dict:
        """Count incidents by severity level."""
        severity_count = {}
        for incident in self.incidents:
            severity = incident.get('severity', 'Unknown')
            severity_count[severity] = severity_count.get(severity, 0) + 1
        return severity_count
    
    def export_processed_data(self, output_dir: str = "data") -> None:
        """Export processed data to CSV files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        if self.projects_df is not None:
            df = self.clean_project_data()
            df = self.add_calculated_fields(df)
            df.to_csv(output_path / "processed_projects.csv", index=False)
            logger.info("Exported processed projects")
        
        if self.resources_df is not None:
            self.resources_df.to_csv(output_path / "processed_resources.csv", index=False)
            logger.info("Exported processed resources")


def create_data_ingestor(data_dir: str = "data") -> DataIngestor:
    """Factory function to create a data ingestor."""
    return DataIngestor(data_dir)


logger.info("Data Ingestion module initialized")
