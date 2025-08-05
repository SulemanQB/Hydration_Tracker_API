# Hydration Tracker App (FastAPI + Flask)

Use the Hydration Tracker App to monitor your level of hydration and sustain a healthy lifestyle.  This application seamlessly monitors users' hydration levels by combining the capabilities of Flask and FastAPI.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Frontend](#frontend)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- Creating and managing user profiles.
- Monitoring of hydration level in real time.
- Calculate your own daily hydration goals.
- Visualization of historical data for tracking progress.

## Getting Started

### Prerequisites

- Python 3.10 or later
- Docker 

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/hydration-tracker.git
cd hydration-tracker
```

2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Set up the MongoDB database using Docker:

```bash
docker run -d -p 27017:27017 --name hydration-db mongo:latest
```

4. Configure the app settings in config.py with MongoDB address

```bash
MONGODB_URI = __.__.__.__
```

### USAGE

Start the FastAPI & Flask directly:
```bash
uvicorn app:api
```

Or run it on a Docker Container:
```bash
docker build -t hydration_tracker_app .
docker run -d -p 8000:8000 hydration_tracker_app
```

### API Documentation
Detailed API documentation and usage instructions can be found in http://localhost:8000/docs#

### Frontend
Frontend is Flask-based providing an intuitive UI to interact with the hydration tracker. Navigate to http://localhost:8000/app after starting the app.

### License
This project is licensed under the MIT License.

### Acknowledgements

* Developed using FastAPI and Flask.
* MongoDB Docker container [MongoDB Official Image].