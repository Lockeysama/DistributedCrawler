#!/bin/bash
echo "Start Clearing..." 
echo "->Clearing *.log"
find . -name "*.log" | xargs rm -rf
echo "->Clearing *.pyc"
find . -name "*.pyc" | xargs rm -rf
echo "->Clearing .project .pydevproject .settings .git .gitignore .DS_Store"
rm -rf .project .pydevproject .settings .git .gitignore .DS_Store
echo "Cleared..."
ls
