#!/bin/bash
# Push THE LISTENER to GitHub
# Run this from /home/user/EEG

cd /home/user/EEG

echo "🚀 Pushing THE LISTENER to GitHub..."
echo ""

# Try to push
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to https://github.com/FriendsCoin/EEG"
    echo ""
    echo "View your repository:"
    echo "  https://github.com/FriendsCoin/EEG"
else
    echo ""
    echo "❌ Push failed - authentication needed"
    echo ""
    echo "Solutions:"
    echo ""
    echo "1. If you have GitHub CLI installed:"
    echo "   gh auth login"
    echo "   git push -u origin main"
    echo ""
    echo "2. If you have an access token:"
    echo "   git remote set-url origin https://YOUR_TOKEN@github.com/FriendsCoin/EEG.git"
    echo "   git push -u origin main"
    echo ""
    echo "3. Clone on another machine with auth:"
    echo "   git clone git@github.com:FriendsCoin/EEG.git"
    echo "   # Then copy this repo's files there"
    echo ""
fi
