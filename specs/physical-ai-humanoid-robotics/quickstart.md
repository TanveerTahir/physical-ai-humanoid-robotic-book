# Quickstart Guide for Physical AI & Humanoid Robotics Textbook Platform

## Overview
This guide provides a quick setup and deployment process for the Physical AI & Humanoid Robotics textbook platform, including both the static Docusaurus frontend and the FastAPI backend with AI features.

## Prerequisites

- Node.js 18+ (for Docusaurus)
- Python 3.11+ (for FastAPI backend)
- Docker (for Qdrant and Neon integration)
- Git
- Access to OpenAI API key
- Access to any required ROS/Isaac development environments

## Setting Up the Development Environment

### 1. Clone the Repository
```bash
git clone <repository-url>
cd physical-ai-humanoid-robotic-book
```

### 2. Backend Setup (FastAPI)
```bash
# Navigate to the API directory
cd api/

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### 3. Frontend Setup (Docusaurus)
```bash
# Navigate to the book directory
cd book/

# Install dependencies
npm install

# Start development server
npm start
```

### 4. Database Setup
```bash
# For Qdrant (vector database)
docker run -d --name qdrant-container -p 6333:6333 qdrant/qdrant

# For Neon Serverless Postgres (user data)
# Follow Neon setup instructions to create a project and connection string
```

## Running the Platform Locally

### 1. Start the Backend
```bash
cd api/
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn main:app --reload --port 8000
```

### 2. Start the Frontend
```bash
cd book/
npm start
```

### 3. Access the Platform
- Frontend (Docusaurus): http://localhost:3000
- Backend API: http://localhost:8000
- Qdrant UI: http://localhost:6333/dashboard

## Key Configuration

### Environment Variables (.env)
```env
# API Configuration
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=http://localhost:6333
NEON_DATABASE_URL=your_neon_connection_string
BETTER_AUTH_SECRET=your_auth_secret
NEXTAUTH_URL=http://localhost:3000

# Application Settings
BOOK_TITLE="Physical AI & Humanoid Robotics"
BOOK_SUBTITLE="An AI-Native Textbook"
DEPLOYMENT_TARGET=development
```

## Adding New Content

### 1. Creating a New Chapter
```bash
# Navigate to the appropriate section in book/docs/
cd book/docs/foundations/  # or other section

# Create new chapter file
touch new-chapter.md

# Add content with proper frontmatter
```

Example chapter format:
```md
---
title: Introduction to Physical AI
sidebar_position: 1
description: Understanding the fundamentals of Physical AI and embodied intelligence
gpu_notes: "Requires GPU with CUDA support for simulation examples"
jetson_notes: "Simulation examples limited on Jetson; run basic ROS nodes only"
---

# Introduction to Physical AI

## Learning Objectives
- Understand the difference between digital and physical AI
- Learn about embodied intelligence concepts
- Explore applications in humanoid robotics

## Content...

## Hands-on Lab
...

## Summary
...
```

### 2. Adding URDF Examples
Place URDF files in `book/static/urdf/` and reference them in chapters:
```md
import URDFVisualizer from '@site/src/components/URDFVisualizer';

<URDFVisualizer urdfPath="/urdf/example.urdf" />
```

## AI Features Configuration

### 1. RAG Setup
The RAG system automatically processes textbook content when:
- New chapters are added
- Existing chapters are updated
- `npm run embed` is executed in the book directory

### 2. Claude Code Subagents
Available subagents are in the `agents/` directory:
- `quiz-generator/` - Interactive quiz generation
- `personalization-agent/` - Content personalization
- `translation-agent/` - Urdu translation
- `vision-slam-explainer/` - Computer vision explanations
- `ros-debugging-agent/` - ROS debugging assistance

## Deployment

### 1. Production Build
```bash
# Build the Docusaurus site
cd book/
npm run build

# The built site is in the build/ directory
```

### 2. Backend Deployment
The FastAPI backend can be deployed using:
- Docker containers
- Cloud platforms (AWS, GCP, Azure)
- Server deployment with Gunicorn

### 3. GitHub Pages Deployment
```bash
# Use Docusaurus deployment script
GIT_USER=<Your GitHub username> \
  CURRENT_BRANCH=main \
  USE_SSH=true \
  npm run deploy
```

## Testing

### 1. Backend Tests
```bash
cd api/
python -m pytest tests/
```

### 2. Content Validation
```bash
# Validate all code examples in textbook
npm run validate-examples

# Check for broken links
npm run check-links
```

## Troubleshooting

### Common Issues:

1. **Port conflicts**: Ensure ports 3000 (frontend) and 8000 (backend) are free
2. **API keys**: Verify all required API keys are set in .env
3. **Database connections**: Check that Qdrant and Neon are accessible
4. **ROS environment**: For ROS-dependent chapters, ensure ROS environment is sourced

### Getting Help:
- Check the documentation in `book/docs/engineering-notes/`
- Review the troubleshooting guide in `book/docs/appendices/c-troubleshooting-atlas.md`
- Submit issues on the GitHub repository