#!/usr/bin/env python
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.development')
    # ... (rest of the file remains the same)