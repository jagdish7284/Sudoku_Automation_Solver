#!/usr/bin/env python3
"""
verify_installation.py

Comprehensive system health check for Sudoku automation system.
Verifies all dependencies, imports, and system readiness.

Usage:
    python verify_installation.py

Exit codes:
    0 = All checks passed ✓
    1 = One or more checks failed ✗
"""

import sys
import subprocess
from typing import List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


class HealthChecker:
    """Verify system health and dependencies."""

    def __init__(self):
        self.checks: List[Tuple[str, bool, str]] = []
        self.critical_failures = 0

    def print_header(self):
        """Print test header."""
        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}🔧 SUDOKU AUTOMATION SYSTEM - INSTALLATION VERIFICATION{RESET}")
        print(f"{BLUE}{'='*70}{RESET}\n")

    def record(self, name: str, passed: bool, message: str = ""):
        """Record a check result."""
        icon = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
        status = f"{GREEN}PASS{RESET}" if passed else f"{RED}FAIL{RESET}"
        print(f"{icon} {status:10} | {name:<40} {message}")
        self.checks.append((name, passed, message))
        if not passed:
            self.critical_failures += 1

    def print_summary(self):
        """Print test summary."""
        total = len(self.checks)
        passed = sum(1 for _, p, _ in self.checks if p)
        failed = total - passed

        print(f"\n{BLUE}{'='*70}{RESET}")
        print(f"{BLUE}SUMMARY{RESET}")
        print(f"{BLUE}{'='*70}{RESET}")
        print(f"Total checks:     {total}")
        print(f"{GREEN}Passed:        {passed}{RESET}")
        if failed > 0:
            print(f"{RED}Failed:        {failed}{RESET}")

        if self.critical_failures == 0:
            print(f"\n{GREEN}{'✓ All checks passed! System is ready.':^70}{RESET}")
            return True
        else:
            print(f"\n{RED}{'✗ Some checks failed. See details above.':^70}{RESET}")
            return False

    def check_python_version(self):
        """Check Python version."""
        version = sys.version_info
        required = (3, 9)
        passed = version >= required
        self.record(
            "Python Version",
            passed,
            f"{version.major}.{version.minor}.{version.micro} {'(OK)' if passed else f'(Need {required[0]}.{required[1]}+)'}"
        )

    def check_pip(self):
        """Check pip availability."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            passed = result.returncode == 0
            self.record("pip", passed, result.stdout.strip().split('\n')[0] if passed else result.stderr)
        except Exception as e:
            self.record("pip", False, str(e))

    def check_package(self, package_name: str, import_name: str = None):
        """Check if a package is installed and importable."""
        if import_name is None:
            import_name = package_name.replace("-", "_")

        # Check pip list
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            installed = result.returncode == 0
            version = ""
            if installed:
                for line in result.stdout.split('\n'):
                    if line.startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        break
        except Exception as e:
            installed = False
            version = f"(Error: {e})"

        # Check import
        try:
            __import__(import_name)
            importable = True
        except ImportError:
            importable = False

        passed = installed and importable
        message = f"v{version}" if version else "(version unknown)"
        if not installed:
            message = "NOT INSTALLED"
        elif not importable:
            message = f"v{version} (import failed)"

        self.record(f"Package: {package_name}", passed, message)
        return passed

    def check_core_imports(self):
        """Check critical imports."""
        core_imports = [
            ("cv2", "opencv"),
            ("numpy", "NumPy"),
            ("sklearn", "scikit-learn"),
            ("fastapi", "FastAPI"),
            ("uvicorn", "Uvicorn"),
        ]

        print(f"\n{BLUE}Core Dependencies:{RESET}")
        for module, name in core_imports:
            try:
                __import__(module)
                self.record(f"Import: {name}", True)
            except ImportError as e:
                self.record(f"Import: {name}", False, str(e))

    def check_sklearn_components(self):
        """Check scikit-learn specific components."""
        print(f"\n{BLUE}scikit-learn Components:{RESET}")

        checks = [
            ("sklearn.datasets.fetch_openml", "MNIST download capability"),
            ("sklearn.neural_network.MLPClassifier", "Neural network classifier"),
            ("sklearn.preprocessing", "Data preprocessing"),
        ]

        for import_path, description in checks:
            module_name, attr = import_path.rsplit(".", 1)
            try:
                module = __import__(module_name, fromlist=[attr])
                getattr(module, attr)
                self.record(f"Component: {attr}", True, description)
            except (ImportError, AttributeError) as e:
                self.record(f"Component: {attr}", False, description)

    def check_opencv_features(self):
        """Check OpenCV features needed."""
        print(f"\n{BLUE}OpenCV Features:{RESET}")

        features = [
            ("cv2.perspectiveTransform", "Perspective transformation"),
            ("cv2.adaptiveThreshold", "Adaptive thresholding"),
            ("cv2.findContours", "Contour detection"),
            ("cv2.cornerSubPix", "Sub-pixel corner refinement"),
        ]

        try:
            import cv2
            for attr, description in features:
                parts = attr.split(".")
                obj = cv2
                try:
                    for part in parts[1:]:
                        obj = getattr(obj, part)
                    self.record(f"Function: {parts[-1]}", True, description)
                except AttributeError:
                    self.record(f"Function: {parts[-1]}", False, description)
        except ImportError:
            self.record("OpenCV", False, "Not installed")

    def check_file_structure(self):
        """Check required file structure."""
        import os
        print(f"\n{BLUE}File Structure:{RESET}")

        files = [
            ("server/main.py", "FastAPI main"),
            ("server/image_processing.py", "Vision pipeline"),
            ("server/digit_recognition.py", "CNN model"),
            ("server/board_validator.py", "Validation"),
            ("server/sudoku_solver.py", "Solver"),
            ("server/requirements.txt", "Dependencies"),
        ]

        for filepath, description in files:
            exists = os.path.exists(filepath)
            self.record(f"File: {filepath}", exists, description)

    def check_model_cache(self):
        """Check if model cache exists."""
        import os
        print(f"\n{BLUE}Model Cache:{RESET}")

        model_path = "server/models/sudoku_digit_mlp.joblib"
        exists = os.path.exists(model_path)
        status = "CACHED (will load instantly)" if exists else "Not cached yet (will train on first run)"
        self.record("Model Cache", exists, status + " (OK if missing)" if not exists else status)

    def check_network(self):
        """Check internet connectivity (needed for first-run MNIST download)."""
        print(f"\n{BLUE}Network:{RESET}")

        try:
            import socket
            socket.create_connection(("www.google.com", 80), timeout=3)
            self.record("Internet Connectivity", True, "Required for first-run MNIST download")
        except (socket.timeout, socket.error):
            self.record("Internet Connectivity", False, "First-run MNIST download may fail")

    def render_recommendations(self):
        """Render helpful recommendations based on failures."""
        failures = [(name, msg) for name, passed, msg in self.checks if not passed]

        if not failures:
            return

        print(f"\n{YELLOW}{'='*70}{RESET}")
        print(f"{YELLOW}RECOMMENDATIONS{RESET}")
        print(f"{YELLOW}{'='*70}{RESET}\n")

        for failed_check, message in failures:
            if "Package" in failed_check:
                package = failed_check.replace("Package: ", "")
                print(f"{YELLOW}→{RESET} {failed_check}")
                print(f"  Solution: pip install {package}")
            elif "File" in failed_check:
                print(f"{YELLOW}→{RESET} {failed_check}")
                print(f"  Solution: Ensure you're in the correct directory")
            elif "Internet" in failed_check:
                print(f"{YELLOW}→{RESET} {failed_check}")
                print(f"  Solution: Connect to internet for first-run MNIST download")
            else:
                print(f"{YELLOW}→{RESET} {failed_check}")

        print()

    def run_all_checks(self) -> int:
        """Run all checks and return exit code."""
        self.print_header()

        print(f"{BLUE}System Information:{RESET}")
        self.check_python_version()
        self.check_pip()

        print(f"\n{BLUE}Required Packages:{RESET}")
        packages = [
            ("opencv-python", "cv2"),
            ("numpy", "numpy"),
            ("scikit-learn", "sklearn"),
            ("fastapi", "fastapi"),
            ("uvicorn", "uvicorn"),
            ("pandas", "pandas"),
            ("joblib", "joblib"),
        ]
        for pkg, import_name in packages:
            self.check_package(pkg, import_name)

        self.check_core_imports()
        self.check_sklearn_components()
        self.check_opencv_features()
        self.check_file_structure()
        self.check_model_cache()
        self.check_network()

        print()
        all_passed = self.print_summary()
        self.render_recommendations()

        return 0 if all_passed else 1


def main():
    """Main entry point."""
    checker = HealthChecker()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
