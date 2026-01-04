# Quick Start Guide

## 5-Minute Setup

### Option 1: Docker (Easiest)

```bash
# 1. Clone and navigate
cd risk_analysis-predictor

# 2. Copy environment files
cp .env.example .env
cp frontend/.env.example frontend/.env

# 3. Start services
docker-compose up -d

# 4. Wait for services to start (30 seconds)
# Check status: docker-compose ps

# 5. Open in browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Update .env with your PostgreSQL database URL
# Then start backend
uvicorn app.main:app --reload

# Frontend Setup (in new terminal)
cd frontend
npm install
npm run dev
```

## Demo Credentials

```
Email: demo@example.com
Password: password123
```

## Key URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 (dev) or :3000 (docker) |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Database | localhost:5432 |

## First Steps in the App

1. **Login** - Use demo credentials above
2. **Create a Project** - Go to Projects, click "New Project"
3. **Add Risks** - Create risks for your project
4. **View Dashboard** - See analytics and metrics
5. **Manage Resources** - Add team members

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- For Docker: `docker-compose logs db`

### Frontend Won't Load
- Check backend is running at `:8000`
- Clear browser cache
- Check console for CORS errors

### Port Already in Use
```bash
# Change ports in docker-compose.yml or
# Kill process using port
lsof -ti :8000  # macOS/Linux
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess  # Windows
```

### WebSocket Connection Error
- Backend must be running
- Check firewall settings
- Verify CORS origins in `.env`

## API Testing

### Using curl

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"password123"}'

# Create Project (replace TOKEN)
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"My Project",
    "start_date":"2024-01-01",
    "planned_end_date":"2024-06-01",
    "team_size":5,
    "manager":"John Doe",
    "budget":100000,
    "risk_level":"medium"
  }'
```

### Using Swagger UI
Visit: http://localhost:8000/docs

## Development Commands

### Backend
```bash
cd backend

# Run tests
pytest

# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

### Frontend
```bash
cd frontend

# Run tests
npm test

# Format code
npm run format

# Check linting
npm run lint

# Build for production
npm run build
```

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Execute command in container
docker-compose exec backend bash

# Rebuild images
docker-compose up -d --build

# Remove everything
docker-compose down -v
```

## Environment Variables

### Backend (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/risk_analysis_predictor
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (frontend/.env)
```
VITE_API_URL=http://localhost:8000/api/v1
```

## Common Tasks

### Reset Database
```bash
# Docker
docker-compose down -v
docker-compose up -d

# Local
# Drop and recreate your PostgreSQL database
```

### Load Sample Data
Sample data files are in `data/` directory:
- `sample_projects.csv`
- `resource_data.csv`
- `historical_incidents.json`

### Change Secret Key
1. Open `.env`
2. Generate new key: `python -c "import secrets; print(secrets.token_hex(32))"`
3. Update `SECRET_KEY` value
4. Restart backend

### Add HTTPS (Production)
1. Obtain SSL certificate (Let's Encrypt, AWS Certificate Manager, etc.)
2. Configure Nginx reverse proxy
3. Update CORS_ORIGINS to use https://

## Performance Tips

- Use pagination for large datasets (built-in with limit/skip)
- Implement caching headers for analytics data
- Use database indexes for frequent queries
- Monitor WebSocket connections
- Cache compiled frontend assets

## Monitoring & Logs

### Backend Logs
```bash
docker-compose logs -f backend
# or
tail -f logs/backend.log
```

### Frontend Console
Open browser DevTools → Console tab for errors

### Database Logs
```bash
docker-compose logs -f db
```

## Next Steps

1. ✅ **Explore the UI** - Familiarize yourself with all features
2. ✅ **Review Code** - Check `IMPLEMENTATION_SUMMARY.md` for architecture
3. ✅ **Customize** - Update colors, text, and branding in config files
4. ✅ **Add Features** - Extend with your own business logic
5. ✅ **Deploy** - Push to production when ready

## Getting Help

- Check `README.md` for comprehensive documentation
- Review `IMPLEMENTATION_SUMMARY.md` for architecture details
- Check API docs at `/docs` endpoint
- Review code comments for implementation details

---

**Ready to go! Happy coding! 🚀**
