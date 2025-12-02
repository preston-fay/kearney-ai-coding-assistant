#!/bin/bash

echo ''
echo '========================================'
echo '  KEARNEY AI CODING ASSISTANT'
echo '  Environment Setup for macOS/Linux'
echo '========================================'
echo ''

# 1. Check Python
echo '[1/4] Checking Python installation...'
if ! command -v python3 &> /dev/null; then
    echo '[ERROR] Python 3 is not installed.'
    echo 'Please install Python 3.10+ via Homebrew: brew install python3'
    exit 1
fi
echo '        Python found.'

# 2. Create virtual environment
echo '[2/4] Creating virtual environment...'
if [ ! -d '.venv' ]; then
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo '[ERROR] Failed to create virtual environment.'
        exit 1
    fi
else
    echo '        Virtual environment already exists.'
fi

# 3. Install dependencies
echo '[3/4] Installing KDS tools...'
.venv/bin/pip install -q -r bootstrap/requirements.txt
if [ $? -ne 0 ]; then
    echo '[ERROR] Failed to install dependencies.'
    exit 1
fi

# 4. Verify installation
echo '[4/4] Verifying installation...'
.venv/bin/python -c 'import pandas, matplotlib, pptx, yaml, PIL; print("All modules OK")'
if [ $? -ne 0 ]; then
    echo '[ERROR] Module verification failed.'
    exit 1
fi

echo ''
echo '========================================'
echo '  SUCCESS! Environment Ready.'
echo '========================================'
echo ''
echo 'Next steps:'
echo '  1. Open Claude Desktop'
echo '  2. File > Open Folder > Select this directory'
echo '  3. Type: /project:help'
echo ''
