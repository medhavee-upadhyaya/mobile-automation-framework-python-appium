# Mobile Automation Framework

Mobile regression automation framework for Android applications built on Appium and PyTest using the Page Object Model design.

## Purpose
- Automate Android smoke and regression test scenarios for native/hybrid apps.
- Support consistent reporting via Allure.
- Provide reusable utilities for driver lifecycle, logging, and page interactions.

## Tech Stack
- Python 3.10+
- Appium Python Client
- PyTest + PyTest-xdist
- Allure PyTest plugin
- Selenium APIs
- Page Object Model structure

## Project Structure
```
config/        # capabilities + framework configuration
pages/         # Page Object classes
tests/         # PyTest suites
utils/         # Driver, helpers, logger utilities
reports/       # Allure output directory (allure-results/screenshots)
```

## Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Update `config/capabilities.json` and `config/config.yaml` with the correct emulator/device and application details before running tests.

## Running Tests
```bash
pytest -m smoke
pytest -m regression
pytest --alluredir=reports/allure-results
```

After running tests with the `--alluredir` option, generate the HTML report with:
```bash
allure serve reports/allure-results
```
