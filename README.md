# Risk Analysis & Resource Management Predictor

A comprehensive, production-ready full-stack application for predictive risk analysis and resource management using AI agents, real-time WebSocket updates, and advanced analytics.

## 🎯 Features

- **AI-Powered Risk Analysis**: Automated risk identification, scoring, and prediction
- **Resource Optimization**: Intelligent resource allocation and utilization tracking
- **Real-time Updates**: WebSocket integration for live project and risk updates
- **Comprehensive Analytics**: Dashboard with trends, predictions, and insights
- **Multi-Agent Architecture**: Specialized AI agents for risk, resource, and bottleneck analysis
- **JWT Authentication**: Secure token-based authentication system
- **RESTful API**: Complete REST API with comprehensive endpoints
- **Responsive UI**: Modern React 18 frontend with TailwindCSS and Shadcn UI

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Authentication**: JWT (Python-Jose) with Bcrypt password hashing
- **Real-time**: WebSocket for live updates with custom connection manager
- **Validation**: Pydantic 2.5.0 with strict schema validation
- **AI**: LangChain ready for agent orchestration

### Frontend Stack
- **Framework**: React 18.2.0 with TypeScript
- **Build**: Vite 5.0.8 for fast development and optimized builds
- **Styling**: TailwindCSS 3.3.6 with custom Shadcn UI components
- **State Management**: Zustand for client state, React Query for server state
- **HTTP Client**: Axios with JWT interceptors
- **Charting**: Recharts for data visualization
- **UI/UX**: Framer Motion for smooth animations

### Database Models
- **User**: Authentication and authorization
- **Project**: Project management with status, risk level, and health metrics
- **Risk**: Risk identification with probability, impact, and scoring
- **Resource**: Team member management with skills and allocation

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional, for containerized deployment)

## 🚀 Quick Start

### Local Development

#### 1. Clone and Setup

```bash
git clone <repository-url>
cd risk_analysis-predictor

# Create environment files
cp .env.example .env
cp frontend/.env.example frontend/.env

# Add your secrets
# - OPENAI_API_KEY in .env (and backend/.env if you split it)
# - Keep all .env files out of git (already gitignored)
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
# Update DATABASE_URL in ../.env to use your local PostgreSQL

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API Docs: `http://localhost:8000/docs`

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### Docker Deployment

```bash
# Start all services
docker-compose up -d

# Create database and tables
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f
```

Services:
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Database: `localhost:5432`

## 📚 API Documentation

### Authentication Endpoints

```
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/auth/me
```

### Project Endpoints

```
GET /api/v1/projects - List projects
POST /api/v1/projects - Create project
GET /api/v1/projects/{id} - Get project details
PUT /api/v1/projects/{id} - Update project
DELETE /api/v1/projects/{id} - Delete project
POST /api/v1/projects/{id}/analyze - Analyze project with AI
```

### Risk Endpoints

```
GET /api/v1/risks - List risks
POST /api/v1/risks - Create risk
GET /api/v1/risks/{id} - Get risk details
PUT /api/v1/risks/{id} - Update risk
DELETE /api/v1/risks/{id} - Delete risk
```

### Resource Endpoints

```
GET /api/v1/resources - List resources
POST /api/v1/resources - Create resource
GET /api/v1/resources/{id} - Get resource details
PUT /api/v1/resources/{id} - Update resource
DELETE /api/v1/resources/{id} - Delete resource
POST /api/v1/resources/{id}/allocate - Allocate resource
```

### Analytics Endpoints

```
GET /api/v1/analytics/dashboard - Dashboard stats
GET /api/v1/analytics/trends - Risk and project trends
GET /api/v1/analytics/predictions/success-rate - Success predictions
GET /api/v1/analytics/bottlenecks - Identify bottlenecks
```

### WebSocket

```
WS /api/v1/ws/{client_id}

Message format:
{
  "type": "subscribe|unsubscribe",
  "event_type": "project_created|risk_identified|resource_allocated",
  "client_id": "unique-client-id"
}
```

## 🔐 Security

- **Password Security**: Bcrypt hashing with configurable work factor
- **JWT Tokens**: Secure token generation with expiration
- **CORS Protection**: Configurable allowed origins
- **Input Validation**: Strict Pydantic schema validation
- **Environment Variables**: Sensitive data in .env files

## 📊 Sample Data

The system includes sample data for testing:
- 100 sample projects in CSV format
- 35 team resources with varied skills
- 20 historical incidents for analysis

Access via: `data/sample_projects.csv`, `data/resource_data.csv`, `data/historical_incidents.json`

## 🔄 Real-time Features

WebSocket connection enables:
- Live project creation notifications
- Real-time risk updates
- Resource allocation changes
- Instant bottleneck alerts
- Live analytics dashboard updates

## 📈 Analytics Features

- **Dashboard**: Overview of projects, risks, resources, and health metrics
- **Trends**: Historical trends of project success and risk identification
- **Predictions**: AI-powered success probability forecasting
- **Bottleneck Detection**: Automatic identification of constraints and resource issues

## 🛠️ Development

### Project Structure

```
risk_analysis-predictor/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── projects.py
│   │   │   │   ├── risks.py
│   │   │   │   ├── resources.py
│   │   │   │   └── analytics.py
│   │   │   └── dependencies.py
│   │   ├── core/
│   │   │   ├── security.py
│   │   │   └── websocket.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── risk.py
│   │   │   └── resource.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   ├── layout/
│   │   │   ├── dashboard/
│   │   │   ├── projects/
│   │   │   └── ui/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   ├── types/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── data/
│   ├── sample_projects.csv
│   ├── resource_data.csv
│   └── historical_incidents.json
├── docker-compose.yml
├── .env.example
└── README.md
```

### Coding Standards

- **Backend**: PEP 8 compliant Python
- **Frontend**: TypeScript with strict mode
- **Imports**: Absolute path imports with @ alias
- **Error Handling**: Comprehensive with user-friendly messages
- **Type Safety**: Full type annotations throughout

## 🧪 Testing

### Backend Testing

```bash
cd backend
pytest
```

### Frontend Testing

```bash
cd frontend
npm run test
```

## 📦 Deployment

### Production Build

```bash
# Backend
cd backend
pip install gunicorn
gunicorn app.main:app -w 4 -b 0.0.0.0:8000

# Frontend
cd frontend
npm run build
```

### Docker Production

```bash
docker-compose -f docker-compose.yml up -d --build
```

### Environment Variables

Update `.env` for production:
```
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:password@prod-db:5432/risk_analysis_predictor
CORS_ORIGINS=https://yourdomain.com
```

## 🔗 Integration Points

### AI Agent Integration

The system is ready for LangChain agent integration:

```python
from langchain import OpenAI, Agent
from app.services.risk_agent import RiskAnalysisAgent

# In your project analyze endpoint:
agent = RiskAnalysisAgent(llm=OpenAI())
analysis = agent.analyze(project_id)
```

### External APIs

- **Authentication**: Extend with OAuth/OpenID Connect
- **Email**: Add notification service (SendGrid, Mailgun)
- **Analytics**: Integrate with data warehouses
- **LLM**: Connect to Anthropic, OpenAI, or local models

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
1. Check existing issues
2. Create a detailed bug report
3. Include environment and reproduction steps

## 🗺️ Roadmap

- [ ] Advanced AI agents with streaming
- [ ] Real-time collaboration features
- [ ] Mobile app (React Native)
- [ ] Advanced reporting and exports
- [ ] Custom workflows and automation
- [ ] Integration marketplace
- [ ] Multi-tenant support
- [ ] Enterprise SSO

---

**Built with ❤️ using FastAPI, React, and modern web technologies**
