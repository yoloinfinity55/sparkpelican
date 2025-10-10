"""
FastAPI Backend for SparkPelican

A modern FastAPI application that provides AI-powered blog post generation
from YouTube videos with automated content creation and Pelican integration.
"""

# Import FastAPI components for easy access
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

__version__ = "1.0.0"
__author__ = "SparkPelican Team"
__description__ = "AI-powered blog post generation API for Pelican static sites"
