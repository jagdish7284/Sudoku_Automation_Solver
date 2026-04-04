# 🧩 Sudoku Automation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-brightgreen)](https://fastapi.tiangolo.com/)
[![Build Status](https://img.shields.io/badge/status-production-brightgreen)]()

> **AI-Powered Sudoku Solver** | Automated puzzle recognition & intelligent solving with a cyberpunk gaming interface

<div align="center">

![Sudoku Automation](https://via.placeholder.com/800x400?text=Sudoku+Automation+System)

**[Live Demo](https://sudoku-demo.vercel.app)** • **[Documentation](#-documentation)** • **[Report Bug](https://github.com/yourusername/sudoku-automation/issues)**

</div>

---

## ✨ Features

### 🤖 Automation Engine
- **Image-Based Solving**: Upload Sudoku puzzle photos for automatic OCR recognition
- **Multi-Strategy Detection**: 3-attempt grid detection with intelligent preprocessing
- **CNN Digit Recognition**: Trained MLP model with confidence voting across 3 variants
- **Board Validation**: Constraint checking, duplicate detection, minimum clue validation
- **Smart Retry Logic**: Automatic retry with varying padding strategies

### 🎮 Gaming Interface
- **Cyberpunk/Hacker Theme**: Matrix rain background, scanline overlays, CRT effects
- **Strict Input Control**: 1 digit per cell, keyboard-only input, no mouse entry
- **Real-Time Status**: Live cell tracking (0/81), validation feedback
- **Dual Mode**: Manual input & automation mode toggle
- **Execution Metrics**: Solve time reporting with visual feedback

### ⚙️ Backend Capabilities
- **Production-Grade API**: FastAPI with comprehensive error handling
- **CORS Enabled**: Seamless frontend-backend communication
- **Detailed Logging**: Debug-friendly error messages and parameter logging
- **Static File Serving**: Integrated frontend delivery from backend
- **RESTful Design**: Clean, documented API endpoints

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | 0.100+ |
| **Server** | Uvicorn | 0.24.0 |
| **Image Processing** | OpenCV | Latest |
| **ML Model** | Scikit-Learn | Latest |
| **Serialization** | Joblib | Latest |
| **Frontend Framework** | Vanilla JavaScript | ES6+ |
| **Styling** | CSS3 | Advanced (animations, grid) |
| **Language** | Python | 3.10+ |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager
- Modern web browser

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sudoku-automation.git
cd sudoku-automation
```

#### 2. Backend Setup
```bash
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
```

#### 3. Frontend Setup
No build process required! The frontend is served directly by the backend.

#### 4. Start the Application
```bash
# Make sure you're in the backend directory
cd backend

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` in your browser to see the application running.

---

## 📖 Usage

### Manual Solving
1. Click on cells in the **GRID_INTERFACE** panel
2. Enter digits (1-9) using keyboard only
3. Click **EXECUTE_SOLVE** to solve the puzzle
4. Execution time and solution displayed in real-time

### Automated Solving (Image Recognition)
1. Toggle **AUTOMATION** switch to enable image processing mode
2. Upload a photo of a Sudoku puzzle using the **IMAGE_PROCESSOR** panel
3. Wait for automatic grid detection and digit recognition
4. Solver processes the board and returns the solution
5. View confidence scores and execution metrics

### API Endpoints

#### Manual Solve
```
POST /api/solve/manual
Content-Type: application/json

{
  "board": [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    ...
  ]
}

Response: { "solution": [[...]], "time_ms": 45, "status": "success" }
```

#### Image-Based Solve
```
POST /api/solve/image
Content-Type: multipart/form-data

[Upload image file as 'file']

Response: {
  "detected_board": [[...]],
  "solution": [[...]],
  "confidence": 0.95,
  "time_ms": 1200,
  "status": "success"
}
```

#### Health Check
```
GET /health

Response: { "status": "healthy", "version": "1.0.0" }
```

---

## 📁 Project Structure

```
sudoku-automation/
├── backend/
│   ├── app/
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── utils/             # Helpers & validators
│   │   └── models/            # ML models & schemas
│   ├── tests/                 # Unit tests
│   ├── main.py                # FastAPI entry point
│   └── requirements.txt        # Python dependencies
│
├── frontend/
│   ├── index.html             # Main UI
│   ├── script.js              # Game logic & API calls
│   ├── style.css              # Cyberpunk styling
│   └── assets/                # Images, fonts, icons
│
├── docs/                      # Documentation
│   ├── INSTALLATION.md
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
│
└── README.md                  # This file
```

---

## 🔧 Configuration

Create a `.env` file in the `backend/` directory:

```env
# FastAPI Configuration
DEBUG=true
LOG_LEVEL=INFO

# API Configuration
API_VERSION=1.0.0
CORS_ORIGINS=["http://localhost:3000", "https://yourfrontend.com"]

# Image Processing
MAX_IMAGE_SIZE_MB=10
IMAGE_TIMEOUT_SECONDS=30

# Model Configuration
MODEL_PATH=./app/models/sudoku_digit_mlp.joblib
CONFIDENCE_THRESHOLD=0.70
```

See `.env.example` for all available options.

---

## 🧪 Testing

Run the test suite:

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_solver.py -v
```

---

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete endpoint reference
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design & components
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment strategies
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project

---

## 🚀 Deployment

### Frontend Deployment

#### Vercel (Recommended)
```bash
# Use Vercel CLI
vercel deploy

# Or connect directly on vercel.com
# Point to your GitHub repo, select "frontend/" as root
```

#### Netlify
```bash
# Drag & drop frontend folder to Netlify
# Or use Netlify CLI:
netlify deploy --prod --dir=frontend
```

### Backend Deployment

#### Railway.app (Recommended)
1. Connect your GitHub repository
2. Select Python as the language
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy automatically on push

#### Heroku
```bash
heroku create sudoku-automation
git push heroku main
```

#### AWS EC2
See [Deployment Guide](docs/DEPLOYMENT.md) for detailed AWS setup.

---

## 📊 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Manual Solve (9x9 grid) | 10-50ms | Backtracking algorithm |
| Image Detection | 800-1500ms | Multi-strategy with retries |
| Digit Recognition | 300-600ms | CNN voting across 3 variants |
| API Response | <2000ms | Full pipeline end-to-end |

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Areas for Contribution
- 🐛 Bug fixes and issue resolution
- ✨ New solving algorithms
- 🎨 UI/UX improvements
- 📱 Mobile responsiveness
- 🌍 Translation support
- 📖 Documentation improvements

---

## 📝 Commit Strategy

This project follows conventional commit messages:

```
feat(solver): add beam search algorithm
fix(api): handle empty board validation
docs(readme): update installation steps
refactor(services): optimize digit recognition
test(image-processing): add edge case tests
```

See our [Commit Guidelines](CONTRIBUTING.md#commit-guidelines) for examples.

---

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced solving techniques (constraint propagation)
- [ ] Difficulty rating system
- [ ] Leaderboard with multiplayer support
- [ ] Puzzle generation from scratch
- [ ] Dark/Light theme toggle
- [ ] Internationalization (i18n)
- [ ] Browser extension version

---

## 🐛 Known Issues

- Large images (>5MB) may timeout during processing
- Handwritten digits have lower recognition accuracy
- Grid detection fails on heavily rotated images

See [Issues](https://github.com/yourusername/sudoku-automation/issues) for more details.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Your Name** - [@yourhandle](https://github.com/yourhandle)

- 💼 Portfolio: [yourportfolio.com](https://yourportfolio.com)
- 📧 Email: your.email@example.com
- 🔗 LinkedIn: [Your Profile](https://linkedin.com/in/yourprofile)

---

## 🙏 Acknowledgments

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenCV](https://opencv.org/) - Computer vision library
- [Scikit-Learn](https://scikit-learn.org/) - ML toolkit
- Inspired by cyberpunk gaming interfaces
- Community feedback and contributions

---

## 📞 Support

- 📖 **Documentation**: Check the [docs](docs/) folder
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/yourusername/sudoku-automation/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/sudoku-automation/discussions)
- 🎯 **Feature Requests**: [GitHub Discussions - Ideas](https://github.com/yourusername/sudoku-automation/discussions/categories/ideas)

---

<div align="center">

Made with ❤️ by [Your Name](https://github.com/yourhandle)

⭐ If you found this project helpful, please consider giving it a star!

</div>

---

**Last Updated**: April 2026 | **Version**: 1.0.0
