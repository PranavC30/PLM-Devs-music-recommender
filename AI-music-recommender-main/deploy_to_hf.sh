#!/bin/bash
# Deploy to Hugging Face Spaces

HF_DIR="PLM-Devs-Music-Recommender"

echo "Copying files to HF Space..."

# Copy all Python files
cp app.py agent.py env.py recommend.py nlp_engine.py dashboard.py "$HF_DIR/"
cp auth.py gamification.py social.py chatbot.py weekly_report.py pomodoro.py "$HF_DIR/"

# Copy requirements
cp requirements.txt "$HF_DIR/"

# Copy README
cp README.md "$HF_DIR/"

# Create data folder and copy songs
mkdir -p "$HF_DIR/data"
cp data/songs.csv "$HF_DIR/data/"

# Create .streamlit folder and copy config
mkdir -p "$HF_DIR/.streamlit"
cp .streamlit/config.toml "$HF_DIR/.streamlit/"

# Copy .gitignore
cp .gitignore "$HF_DIR/"

echo "Files copied. Now pushing to HF..."

cd "$HF_DIR"
git add .
git commit -m "Deploy PLM Devs Music Recommender to Hugging Face Spaces"
git push

echo "Done! Check your HF Space in 1-2 minutes."
