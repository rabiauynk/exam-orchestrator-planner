# Exam Orchestrator Planner

An intelligent exam scheduling system that automatically organizes university exams based on preferences, constraints, and resource availability.

## 🚀 Features

- **Smart Exam Scheduling**: Automatic scheduling algorithm considering room capacity, computer requirements, and preferred dates
- **Department Management**: Organize exams by academic departments
- **Room & Resource Management**: Manage classrooms and computer labs
- **Excel Export**: Export exam schedules to Excel files with department-specific sheets
- **Real-time Dashboard**: Monitor exam status and scheduling progress
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🏗️ Architecture

This project consists of two main components:

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **UI Library**: shadcn/ui components with Tailwind CSS
- **State Management**: React Query for server state
- **Routing**: React Router DOM
- **Build Tool**: Vite

### Backend (Python + Flask)
- **Framework**: Flask 3.0 with SQLAlchemy ORM
- **Database**: MySQL 8.0+
- **API**: RESTful API with JSON responses
- **Export**: Excel generation with openpyxl
- **Scheduling**: Custom algorithm for optimal exam placement

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **MySQL** 5.7+ or 8.0+
- **Git**

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd exam-orchestrator-planner
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

### 3. Database Setup

```sql
-- Create MySQL database
CREATE DATABASE exam_orchestrator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'exam_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON exam_orchestrator.* TO 'exam_user'@'localhost';
FLUSH PRIVILEGES;
```

```bash
# Initialize database with tables and default data
python setup_database.py init

# Add sample data (optional)
python setup_database.py sample
```

### 4. Frontend Setup

```bash
# Navigate to project root
cd ..

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (default backend URL: http://localhost:5000)
```

## 🚀 Running the Application

### Start Backend Server

```bash
cd backend
python app.py
```

Backend will be available at `http://localhost:5000`

### Start Frontend Development Server

```bash
# In project root
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📚 API Documentation

### Core Endpoints

- **Health Check**: `GET /api/health`
- **Exams**: `GET|POST|PUT|DELETE /api/exams`
- **Schedule**: `GET /api/schedule`, `POST /api/schedule/generate`
- **Departments**: `GET|POST|PUT|DELETE /api/departments`
- **Settings**: `GET|POST /api/settings/exam-week`
- **Export**: `GET /api/export/excel`

For detailed API documentation, see [backend/README.md](backend/README.md)

## 🎯 Usage

1. **Configure Exam Week**: Set the date range for exams in Admin → Settings
2. **Add Departments**: Create academic departments if not using defaults
3. **Create Exams**: Add exam details including preferences and requirements
4. **Generate Schedule**: Use the automatic scheduling feature
5. **Export Results**: Download Excel files with exam schedules

## 🔧 Configuration

### Backend Configuration (.env)

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=exam_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=exam_orchestrator
SECRET_KEY=your-secret-key
DEBUG=True
CORS_ORIGINS=http://localhost:5173
```

### Frontend Configuration (.env)

```env
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_NAME=Exam Orchestrator
```

## 🧪 Testing

### Backend Testing

```bash
cd backend
# Test API endpoints
curl http://localhost:5000/api/health
```

### Frontend Testing

```bash
# Run development server and test in browser
npm run dev
```

## 📦 Building for Production

### Frontend Build

```bash
npm run build
```

### Backend Production

```bash
cd backend
export FLASK_ENV=production
python app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify MySQL is running
   - Check credentials in `.env`
   - Ensure database exists

2. **CORS Issues**
   - Check `CORS_ORIGINS` in backend `.env`
   - Verify frontend URL is included

3. **Import Errors**
   - Activate Python virtual environment
   - Install all requirements

For more troubleshooting tips, see [backend/README.md](backend/README.md)

## 🔗 Links

- **Frontend**: React + TypeScript + shadcn/ui
- **Backend**: Python + Flask + SQLAlchemy
- **Database**: MySQL
- **Deployment**: Can be deployed on any cloud platform
