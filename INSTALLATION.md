# Installation Guide

Complete step-by-step guide to set up Sudoku Automation System on your machine.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Windows Installation](#windows-installation)
3. [macOS Installation](#macos-installation)
4. [Linux Installation](#linux-installation)
5. [Troubleshooting](#troubleshooting)
6. [Docker Setup (Optional)](#docker-setup-optional)

---

## System Requirements

### Minimum Requirements
- **Python**: 3.10 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 500MB
- **Browser**: Chrome, Firefox, Safari, or Edge (modern version)

### Recommended Setup
- **Python**: 3.11+
- **RAM**: 4GB+
- **Storage**: 1GB
- **OS**: Windows 10+, macOS 10.14+, or Ubuntu 20.04+

### Optional Requirements
- **Git**: For version control
- **Docker**: For containerized deployment

---

## Windows Installation

### Step 1: Install Python

1. Download Python 3.10+ from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **Important**: Check "Add Python to PATH"
4. Click "Install Now"

**Verify Installation:**
```powershell
python --version
pip --version
```

Both should show version information.

### Step 2: Clone Repository

```powershell
git clone https://github.com/yourusername/sudoku-automation.git
cd sudoku-automation
```

Or download as ZIP and extract.

### Step 3: Create Virtual Environment

```powershell
# Navigate to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate
```

You should see `(venv)` prefix in your terminal.

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:
- fastapi ~0.100.0
- uvicorn ~0.24.0
- opencv-python (latest)
- scikit-learn (latest)
- numpy
- Pillow
- And more...

**Installation time**: 3-5 minutes depending on internet speed

### Step 5: Verify Installation

```powershell
python -m pip list
```

Should show all packages installed without errors.

### Step 6: Start the Application

```powershell
# Make sure you're in backend folder with venv activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### Step 7: Open in Browser

Visit: `http://localhost:8000`

You should see the **SUDOKU AUTOMATION** interface with the cyberpunk theme.

---

## macOS Installation

### Step 1: Install Python

Using Homebrew (recommended):

```bash
brew install python@3.11
```

Or download from [python.org](https://www.python.org/downloads/)

**Verify:**
```bash
python3 --version
```

### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/sudoku-automation.git
cd sudoku-automation
```

### Step 3: Create Virtual Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Install OpenCV Dependencies (if needed)

```bash
brew install opencv
```

### Step 6: Start Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Open Browser

Visit: `http://localhost:8000`

---

## Linux Installation

### Ubuntu/Debian

#### Step 1: Install Python & pip

```bash
sudo apt update
sudo apt install python3.10 python3-pip python3-venv
```

**Verify:**
```bash
python3 --version
pip3 --version
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/sudoku-automation.git
cd sudoku-automation
```

#### Step 3: Install System Dependencies

```bash
sudo apt install libopencv-dev python3-opencv
```

#### Step 4: Create Virtual Environment

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### Step 6: Start Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Step 7: Access Application

Visit: `http://localhost:8000`

---

### Fedora/CentOS

```bash
sudo dnf install python3.10 python3-pip opencv-devel

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Configuration

### Create .env File

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
DEBUG=true
LOG_LEVEL=INFO
MAX_IMAGE_SIZE_MB=10
PORT=8000
```

---

## Development Setup

### Install Development Dependencies

```bash
# With virtual environment activated
pip install pytest pytest-cov black pylint

# Run tests
pytest

# Check code style
black backend/
pylint backend/app
```

---

## Docker Setup (Optional)

### Prerequisites
- Docker installed and running

### Build & Run with Docker

```bash
# Build Docker image
docker build -t sudoku-automation .

# Run container
docker run -p 8000:8000 sudoku-automation
```

Visit: `http://localhost:8000`

---

## Troubleshooting

### Issue: Python not found

**Windows:**
```powershell
# Try python3 instead
python3 --version
```

**Solution**: Reinstall Python and ensure "Add to PATH" is checked.

### Issue: pip: command not found

**Solution:**
```bash
# Use Python module
python -m pip install -r requirements.txt
```

### Issue: Virtual environment not activating

**Windows:**
- Check venv folder exists: `backend/venv/`
- Try: `.\venv\Scripts\Activate.ps1`
- If still fails: Delete venv and recreate:
  ```powershell
  rmdir venv -Force -Recurse
  python -m venv venv
  .\venv\Scripts\activate
  ```

**macOS/Linux:**
```bash
deactivate  # Exit any current environment
source venv/bin/activate  # Try again
```

### Issue: OpenCV import error

```bash
# Reinstall OpenCV
pip install --force-reinstall opencv-python
```

### Issue: Port 8000 already in use

```bash
# Use different port
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Issue: ModuleNotFoundError

```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Cannot upload image / Image processing error

- Ensure image is valid (JPG, PNG)
- Image size should be < 10MB (configurable in .env)
- Try with a clearer Sudoku image
- Check server logs for details

---

## Next Steps

1. ✅ Read [README.md](../README.md) for features overview
2. 📖 Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API endpoints
3. 🎮 Try the UI - enter a Sudoku puzzle manually and solve it
4. 📸 Upload an image to test automated recognition
5. 🧪 Run tests: `pytest`
6. 🚀 Deploy to cloud (see [DEPLOYMENT.md](DEPLOYMENT.md))

---

## Getting Help

- 📖 **Documentation**: Check [docs/](../docs/)
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/yourusername/sudoku-automation/issues)
- 💬 **Ask Questions**: [GitHub Discussions](https://github.com/yourusername/sudoku-automation/discussions)
- 🤝 **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Last Updated**: April 4, 2026
**Status**: Production Ready ✅
