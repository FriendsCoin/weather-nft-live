# Migrating THE LISTENER to EEG Repository

This guide helps you move THE LISTENER project from `weather-nft-live/listener/` to the dedicated `EEG` repository.

---

## Migration Options

Choose the best option for your needs:

### **Option 1: Clean Copy (Recommended - Simplest)**
Copy all files to the EEG repo as a fresh start. Loses git history but cleanest.

### **Option 2: Preserve Git History (Advanced)**
Use git subtree/filter-branch to preserve commit history. More complex.

### **Option 3: Archive and Fresh Start**
Archive current work, start fresh in EEG repo. Good documentation trail.

---

## Option 1: Clean Copy (Recommended)

**Best for:** Most users, quickest migration

### Step 1: Clone EEG Repository

```bash
cd /home/user
git clone https://github.com/FriendsCoin/EEG.git
cd EEG
```

### Step 2: Copy THE LISTENER Files

```bash
# Copy everything from listener/ to EEG/
cp -r /home/user/weather-nft-live/listener/* .

# Verify files copied
ls -la
```

### Step 3: Clean Up Git References

```bash
# Remove old git references if any
rm -rf .git

# Initialize fresh git repo
git init
git add .
git commit -m "Initial commit: THE LISTENER - AI Meditation Witness

Complete EEG meditation analysis system with:
- EEG capture and preprocessing
- VAE neural network training
- Meditation analysis with neurofeedback research
- Multimodal generation (text, images, video, audio)
- RTX 2080 8GB optimization
- Hybrid local+cloud workflows

Migrated from weather-nft-live/listener/ on $(date +%Y-%m-%d)

Total: 7,304 lines of Python code
Documentation: 2,572 lines
Quality Score: 95/100 (Production Ready)"
```

### Step 4: Set Remote and Push

```bash
# If EEG repo already has a remote
git remote add origin https://github.com/FriendsCoin/EEG.git

# If EEG repo is empty
git branch -M main
git push -u origin main

# If EEG repo has existing content
git pull origin main --allow-unrelated-histories
# Resolve any conflicts
git push -u origin main
```

### Step 5: Verify

```bash
# Check remote
git remote -v

# Check status
git status

# Test imports
python -c "import sys; sys.path.insert(0, 'src'); from utils import MeditationAnalyzer; print('✓ Import successful')"
```

---

## Option 2: Preserve Git History (Advanced)

**Best for:** Want to keep all commit history

### Method A: Git Subtree Split

```bash
# In weather-nft-live repo
cd /home/user/weather-nft-live

# Create a new branch with only listener/ history
git subtree split --prefix=listener --branch listener-only

# Clone EEG repo
cd /home/user
git clone https://github.com/FriendsCoin/EEG.git
cd EEG

# Pull in the listener history
git pull /home/user/weather-nft-live listener-only

# Push to remote
git push origin main
```

### Method B: Git Filter-Repo (Most Powerful)

```bash
# Install git-filter-repo
pip install git-filter-repo

# Clone fresh copy of weather-nft-live
cd /home/user
git clone https://github.com/FriendsCoin/weather-nft-live.git listener-migration
cd listener-migration

# Extract only listener/ directory with full history
git filter-repo --subdirectory-filter listener

# Add EEG remote
git remote add eeg https://github.com/FriendsCoin/EEG.git

# Push
git push eeg main
```

---

## Option 3: Archive and Fresh Start

**Best for:** Want clean separation and archive

### Step 1: Archive Current Work

```bash
cd /home/user/weather-nft-live

# Create archive
tar -czf listener-backup-$(date +%Y%m%d).tar.gz listener/

# Store archive
mv listener-backup-*.tar.gz ~/backups/
```

### Step 2: Clone EEG Repo

```bash
cd /home/user
git clone https://github.com/FriendsCoin/EEG.git
cd EEG
```

### Step 3: Copy Files

```bash
cp -r /home/user/weather-nft-live/listener/* .
```

### Step 4: Create Fresh Git History

```bash
git add .
git commit -m "THE LISTENER: Complete EEG Meditation System

Initial implementation (migrated from weather-nft-live)

Features:
- EEG capture and preprocessing (Muse S)
- VAE neural network (32D latent space)
- Advanced meditation analysis (Kovacevic et al. 2015)
- Multimodal generation (text, images, video, audio)
- Local GPU optimization (RTX 2080 8GB)
- Hybrid cloud workflows (vast.ai)

Archive: listener-backup-$(date +%Y%m%d).tar.gz"

git push origin main
```

---

## Quick Migration Script

**Automated clean copy (Option 1):**

```bash
#!/bin/bash
# migrate_listener.sh

set -e

echo "═══════════════════════════════════════════════"
echo "  THE LISTENER Migration to EEG Repository"
echo "═══════════════════════════════════════════════"
echo ""

# Configuration
SOURCE_DIR="/home/user/weather-nft-live/listener"
TARGET_DIR="/home/user/EEG"
REPO_URL="https://github.com/FriendsCoin/EEG.git"

# Check source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Clone EEG repo
echo "→ Cloning EEG repository..."
cd /home/user
if [ -d "EEG" ]; then
    echo "⚠️  EEG directory already exists. Please remove or rename it."
    exit 1
fi
git clone $REPO_URL

# Copy files
echo "→ Copying THE LISTENER files..."
cd EEG
cp -r $SOURCE_DIR/* .

# Clean up
echo "→ Cleaning up..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Git setup
echo "→ Setting up git..."
git add .
git commit -m "THE LISTENER: Complete EEG Meditation System

Migrated from weather-nft-live/listener/ on $(date +%Y-%m-%d)

Complete implementation:
- 7,304 lines of Python code
- 2,572 lines of documentation
- Quality Score: 95/100
- Production ready

Features:
- EEG capture and preprocessing
- VAE neural network training
- Advanced meditation analysis
- Multimodal generation
- GPU optimization
- Cloud workflows"

# Push
echo "→ Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Migration complete!"
echo ""
echo "THE LISTENER is now in: $TARGET_DIR"
echo "Repository: $REPO_URL"
echo ""
echo "Next steps:"
echo "  1. cd $TARGET_DIR"
echo "  2. pip install -r requirements.txt"
echo "  3. python scripts/test_gpu_setup.py"
echo ""
```

**Save as:** `migrate_listener.sh`

**Run:**
```bash
chmod +x migrate_listener.sh
./migrate_listener.sh
```

---

## Post-Migration Checklist

After migrating, verify these:

### Essential Tests

- [ ] Files copied correctly: `ls -la`
- [ ] Git remote set: `git remote -v`
- [ ] Git status clean: `git status`
- [ ] Dependencies install: `pip install -r requirements.txt`
- [ ] Imports work: `python -c "from src.utils import MeditationAnalyzer"`
- [ ] Scripts executable: `python scripts/test_gpu_setup.py`

### Optional Cleanup

- [ ] Update README with new repo URL
- [ ] Update documentation references
- [ ] Add .github/ workflows if desired
- [ ] Create GitHub issues/projects
- [ ] Set up GitHub Pages for docs

---

## Updating References

If you had any external references to the old location, update them:

### In Code

```python
# Old
from weather_nft_live.listener.src.utils import MeditationAnalyzer

# New
from src.utils import MeditationAnalyzer
```

### In Documentation

```markdown
<!-- Old -->
Repository: https://github.com/FriendsCoin/weather-nft-live/tree/main/listener

<!-- New -->
Repository: https://github.com/FriendsCoin/EEG
```

### SSH Config (if using cloud)

```
# ~/.ssh/config - Update project path
Host vast-listener
    RemoteCommand cd ~/EEG && exec $SHELL  # Updated path
```

---

## Preserving Weather-NFT-Live Branch

If you want to keep the listener branch in weather-nft-live for reference:

```bash
cd /home/user/weather-nft-live

# Create archive branch
git checkout -b listener-archived
git add listener/
git commit -m "Archive: THE LISTENER moved to EEG repository

See: https://github.com/FriendsCoin/EEG"

# Push archive branch
git push origin listener-archived

# Return to main and remove listener/
git checkout main
git rm -rf listener/
git commit -m "Remove listener/ (moved to EEG repository)"
git push origin main
```

---

## Troubleshooting

### Issue: EEG Repo Not Empty

**Solution:**
```bash
cd /home/user/EEG

# Pull existing content first
git pull origin main

# Then copy and commit listener files
cp -r /home/user/weather-nft-live/listener/* .
git add .
git commit -m "Add THE LISTENER project"
git push origin main
```

### Issue: Permission Denied

**Solution:**
```bash
# Check GitHub authentication
gh auth status

# Or use HTTPS with token
git remote set-url origin https://<token>@github.com/FriendsCoin/EEG.git
```

### Issue: Merge Conflicts

**Solution:**
```bash
# If pulling into non-empty repo causes conflicts
git pull origin main --strategy-option theirs  # Keep remote version
# Or manually resolve in editor
```

---

## Recommended Approach

**For most users, I recommend Option 1 (Clean Copy):**

1. Simple and fast (5 minutes)
2. No git history complexity
3. Fresh start in dedicated repo
4. Easy to understand and maintain

**Run this:**

```bash
cd /home/user
git clone https://github.com/FriendsCoin/EEG.git
cd EEG
cp -r /home/user/weather-nft-live/listener/* .
git add .
git commit -m "THE LISTENER: Complete EEG Meditation System"
git push origin main
```

Done! 🎉

---

## Verification

After migration, run this to verify everything works:

```bash
cd /home/user/EEG

# Test structure
ls -la src/ docs/ scripts/

# Test Python
python -c "import sys; sys.path.insert(0, 'src'); from utils import MeditationAnalyzer; print('✓')"

# Test git
git remote -v
git log --oneline -5

# Test dependencies
pip install -r requirements.txt

# Full test
python scripts/test_gpu_setup.py
```

---

## Need Help?

If you encounter issues:

1. **Check git status:** `git status`
2. **Check remotes:** `git remote -v`
3. **Check logs:** `git log --oneline`
4. **Check files:** `ls -la`
5. **Ask in this chat!**

---

**Ready to migrate?** Choose your option and follow the steps!
