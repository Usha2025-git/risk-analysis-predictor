"""
Streamlit Dashboard for Predictive Risk & Resource Management System
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

from src.data_ingestion import create_data_ingestor
from src.embeddings import VectorStore, ProjectEmbedder
from src.agents.risk_agent import create_risk_analyzer
from src.agents.resource_agent import create_resource_optimizer
from src.agents.bottleneck_agent import create_bottleneck_detector
from src.agents.orchestrator import create_orchestrator
from src.utils import serialize_analysis


# Page configuration
st.set_page_config(
    page_title="Predictive Risk & Resource Management",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-critical { color: #ff0000; font-weight: bold; }
    .risk-high { color: #ff6600; font-weight: bold; }
    .risk-medium { color: #ffaa00; font-weight: bold; }
    .risk-low { color: #00aa00; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'system_initialized' not in st.session_state:
    st.session_state.system_initialized = False
    st.session_state.ingestor = None
    st.session_state.orchestrator = None
    st.session_state.latest_analysis = None


@st.cache_resource
def initialize_system():
    """Initialize the system (cached to run once)."""
    try:
        ingestor = create_data_ingestor("data")
        projects_df, resources_df, incidents = ingestor.load_all()
        
        vector_store = VectorStore(embedding_dim=768, persist_dir=".vector_store")
        embedder = ProjectEmbedder(vector_store)
        
        projects_df = ingestor.clean_project_data()
        projects_df = ingestor.add_calculated_fields(projects_df)
        projects_list = projects_df.to_dict('records')
        
        embedder.embed_projects(projects_list)
        embedder.embed_incidents(incidents)
        
        risk_analyzer = create_risk_analyzer(embedder, projects_list, incidents)
        resource_optimizer = create_resource_optimizer(resources_df.to_dict('records'))
        bottleneck_detector = create_bottleneck_detector(projects_list, incidents)
        orchestrator = create_orchestrator(
            risk_analyzer,
            resource_optimizer,
            bottleneck_detector,
            ingestor,
            embedder
        )
        
        return ingestor, orchestrator
    except Exception as e:
        st.error(f"Error initializing system: {str(e)}")
        return None, None


def create_risk_heatmap(analysis):
    """Create risk heatmap visualization."""
    if not analysis or not analysis.risks:
        return None
    
    risks_data = []
    for risk in analysis.risks:
        risks_data.append({
            'Risk Type': risk.risk_type.title(),
            'Probability': risk.probability,
            'Impact': risk.impact,
            'Confidence': risk.confidence_score * 100
        })
    
    df = pd.DataFrame(risks_data)
    
    impact_order = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
    df['Impact_num'] = df['Impact'].map(impact_order)
    
    fig = px.scatter(
        df,
        x='Probability',
        y='Impact_num',
        size='Confidence',
        hover_name='Risk Type',
        hover_data={'Probability': ':.0f', 'Impact': True, 'Confidence': ':.0f'},
        title='Risk Analysis Heatmap',
        labels={'Probability': 'Risk Probability (%)', 'Impact_num': 'Risk Impact'},
        color='Risk Type'
    )
    
    fig.update_yaxes(tickvals=[1, 2, 3, 4], ticktext=['Low', 'Medium', 'High', 'Critical'])
    
    return fig


def create_resource_chart(recommendations):
    """Create resource allocation chart."""
    if not recommendations:
        return None
    
    resources_data = []
    for rec in recommendations[:10]:  # Top 10
        resources_data.append({
            'Resource': rec.resource_name,
            'Current': rec.current_allocation * 100,
            'Recommended': rec.recommended_allocation * 100
        })
    
    df = pd.DataFrame(resources_data)
    
    fig = go.Figure(data=[
        go.Bar(name='Current Allocation', x=df['Resource'], y=df['Current']),
        go.Bar(name='Recommended', x=df['Resource'], y=df['Recommended'])
    ])
    
    fig.update_layout(
        title='Resource Allocation Comparison',
        xaxis_title='Resource',
        yaxis_title='Allocation %',
        barmode='group',
        hovermode='x unified'
    )
    
    return fig


def create_bottleneck_timeline(bottlenecks):
    """Create bottleneck timeline visualization."""
    if not bottlenecks:
        return None
    
    bottleneck_data = []
    for bn in bottlenecks[:8]:  # Top 8
        severity_color = {
            'Critical': '#ff0000',
            'High': '#ff6600',
            'Medium': '#ffaa00',
            'Low': '#00aa00'
        }.get(bn.severity, '#cccccc')
        
        bottleneck_data.append({
            'Task': bn.task_name,
            'Expected Delay': bn.expected_delay_days,
            'Severity': bn.severity,
            'Color': severity_color
        })
    
    df = pd.DataFrame(bottleneck_data)
    
    fig = px.bar(
        df,
        x='Expected Delay',
        y='Task',
        orientation='h',
        color='Severity',
        color_discrete_map={
            'Critical': '#ff0000',
            'High': '#ff6600',
            'Medium': '#ffaa00',
            'Low': '#00aa00'
        },
        title='Bottleneck Analysis - Expected Delays'
    )
    
    fig.update_layout(
        xaxis_title='Expected Delay (Days)',
        yaxis_title='Task/Bottleneck'
    )
    
    return fig


def create_overall_score_gauge(overall_score):
    """Create overall risk score gauge."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=overall_score,
        title={'text': "Overall Risk Score"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 25], 'color': "lightgreen"},
                {'range': [25, 50], 'color': "lightyellow"},
                {'range': [50, 75], 'color': "lightsalmon"},
                {'range': [75, 100], 'color': "lightcoral"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))
    
    fig.update_layout(height=400)
    return fig


def main():
    """Main Streamlit application."""
    st.title("🚀 Predictive Risk & Resource Management System")
    st.markdown("---")
    
    # Initialize system
    if not st.session_state.system_initialized:
        with st.spinner("Initializing system..."):
            ingestor, orchestrator = initialize_system()
            if ingestor and orchestrator:
                st.session_state.ingestor = ingestor
                st.session_state.orchestrator = orchestrator
                st.session_state.system_initialized = True
            else:
                st.error("Failed to initialize system")
                return
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Navigation")
        page = st.radio(
            "Select Page",
            ["Dashboard", "Project Analysis", "Resource Management", "Bottleneck Analysis", "Historical Data"]
        )
    
    # Dashboard Page
    if page == "Dashboard":
        st.header("System Overview")
        
        # Get statistics
        stats = st.session_state.ingestor.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Projects", stats.get('total_projects', 0))
        with col2:
            st.metric("Average Budget", f"${stats.get('avg_budget', 0):,.0f}")
        with col3:
            st.metric("Avg Delay", f"{stats.get('avg_delay_days', 0):.1f} days")
        with col4:
            st.metric("Total Incidents", stats.get('total_incidents', 0))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Projects by Risk Level")
            risk_distribution = stats.get('projects_by_risk_level', {})
            if risk_distribution:
                fig = px.pie(
                    values=list(risk_distribution.values()),
                    names=list(risk_distribution.keys()),
                    title="Risk Level Distribution",
                    color_discrete_map={
                        'Critical': '#ff0000',
                        'High': '#ff6600',
                        'Medium': '#ffaa00',
                        'Low': '#00aa00'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Industries")
            industries = stats.get('industries', [])
            if industries:
                industry_counts = {ind: 1 for ind in industries}
                for ind in industries:
                    industry_counts[ind] = sum(1 for p in st.session_state.ingestor.projects_df.to_dict('records')
                                              if p.get('industry') == ind)
                
                fig = px.bar(
                    x=list(industry_counts.keys()),
                    y=list(industry_counts.values()),
                    title="Projects by Industry",
                    labels={'x': 'Industry', 'y': 'Count'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Project Analysis Page
    elif page == "Project Analysis":
        st.header("Project Risk Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            project_id = st.selectbox(
                "Select Project",
                options=st.session_state.ingestor.projects_df['project_id'].tolist()
            )
        
        with col2:
            if st.button("🔍 Analyze", key="analyze_btn"):
                with st.spinner("Analyzing project..."):
                    project = st.session_state.ingestor.get_project_by_id(project_id)
                    if project:
                        analysis = st.session_state.orchestrator.analyze_project(
                            project_id=project_id,
                            project_data=project
                        )
                        st.session_state.latest_analysis = analysis
        
        st.markdown("---")
        
        if st.session_state.latest_analysis:
            analysis = st.session_state.latest_analysis
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Overall Risk Score", f"{analysis.overall_risk_score:.1f}/100")
            with col2:
                st.metric("Confidence", f"{analysis.confidence_level:.1%}")
            with col3:
                st.metric("Risks Identified", len(analysis.risks))
            with col4:
                st.metric("Bottlenecks", len(analysis.bottlenecks))
            
            st.markdown("---")
            
            # Risk Heatmap
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = create_risk_heatmap(analysis)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = create_overall_score_gauge(analysis.overall_risk_score)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Executive Summary
            st.subheader("Executive Summary")
            st.info(analysis.executive_summary)
            
            st.markdown("---")
            
            # Top Recommendations
            st.subheader("Top Recommendations")
            for idx, rec in enumerate(analysis.top_recommendations, 1):
                st.write(f"{idx}. {rec}")
            
            st.markdown("---")
            
            # Detailed Risks
            st.subheader("Identified Risks")
            for risk in analysis.risks:
                with st.expander(f"⚠️ {risk.risk_type.upper()} - {risk.probability:.0f}%"):
                    st.write(f"**Impact:** {risk.impact}")
                    st.write(f"**Description:** {risk.description}")
                    st.write(f"**Mitigation:** {risk.mitigation_strategy}")
                    st.write(f"**Confidence:** {risk.confidence_score:.1%}")
            
            # Download Report
            st.markdown("---")
            report = st.session_state.orchestrator.generate_report(analysis)
            st.download_button(
                label="📥 Download Full Report",
                data=report,
                file_name=f"analysis_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Resource Management Page
    elif page == "Resource Management":
        st.header("Resource Management & Optimization")
        
        utilization = st.session_state.ingestor.resources_df.copy()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Resources", len(utilization))
        with col2:
            avg_alloc = utilization['current_allocation'].mean() * 100
            st.metric("Avg Allocation", f"{avg_alloc:.1f}%")
        with col3:
            overallocated = len(utilization[utilization['current_allocation'] > 1.0])
            st.metric("Overallocated", overallocated)
        
        st.markdown("---")
        
        # Resource allocation chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                utilization.head(15),
                x='current_allocation',
                y='resource_name',
                orientation='h',
                title='Top 15 Resource Allocations',
                labels={'current_allocation': 'Allocation %', 'resource_name': 'Resource'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            skill_util = utilization.groupby('skill_category')['current_allocation'].mean()
            fig = px.bar(
                x=skill_util.index,
                y=skill_util.values * 100,
                title='Avg Allocation by Skill',
                labels={'x': 'Skill', 'y': 'Avg Allocation %'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("Resource Details")
        st.dataframe(
            utilization[['resource_name', 'skill_category', 'current_allocation', 'max_allocation', 'availability']],
            use_container_width=True
        )
    
    # Bottleneck Analysis Page
    elif page == "Bottleneck Analysis":
        st.header("Bottleneck Analysis")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            project_id = st.selectbox(
                "Select Project",
                options=st.session_state.ingestor.projects_df['project_id'].tolist(),
                key="bottleneck_project"
            )
        
        with col2:
            if st.button("🔍 Analyze Bottlenecks", key="analyze_bn_btn"):
                with st.spinner("Analyzing bottlenecks..."):
                    project = st.session_state.ingestor.get_project_by_id(project_id)
                    if project:
                        similar = st.session_state.ingestor.get_similar_projects(project_id, limit=5)
                        # Store in session state
                        st.session_state.bottleneck_analysis = (project, similar)
        
        st.markdown("---")
        
        if 'bottleneck_analysis' in st.session_state:
            project, similar = st.session_state.bottleneck_analysis
            
            bottleneck_detector = st.session_state.orchestrator.bottleneck_detector
            bottlenecks = bottleneck_detector.analyze_project_bottlenecks(
                project_id, project, similar_projects=similar
            )
            
            fig = create_bottleneck_timeline(bottlenecks)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            st.subheader("Bottleneck Details")
            for bn in bottlenecks:
                with st.expander(f"🚧 {bn.task_name} - {bn.severity}"):
                    st.write(f"**Expected Delay:** {bn.expected_delay_days} days")
                    st.write(f"**Root Cause:** {bn.root_cause}")
                    st.write(f"**Mitigation:** {bn.mitigation_recommendation}")
                    if bn.parallel_task_opportunity:
                        st.write(f"**Parallelization Opportunity:** {bn.parallel_task_opportunity}")
    
    # Historical Data Page
    elif page == "Historical Data":
        st.header("Historical Project Data")
        
        tab1, tab2, tab3 = st.tabs(["Projects", "Resources", "Incidents"])
        
        with tab1:
            st.subheader("Historical Projects")
            st.dataframe(
                st.session_state.ingestor.projects_df,
                use_container_width=True
            )
        
        with tab2:
            st.subheader("Resources")
            st.dataframe(
                st.session_state.ingestor.resources_df,
                use_container_width=True
            )
        
        with tab3:
            st.subheader("Historical Incidents")
            incidents_df = pd.DataFrame(st.session_state.ingestor.incidents)
            st.dataframe(
                incidents_df,
                use_container_width=True
            )


if __name__ == "__main__":
    main()
