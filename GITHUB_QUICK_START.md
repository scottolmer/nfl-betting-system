================================================================================
GITHUB QUICK START - CHEAT SHEET
================================================================================

TL;DR - FASTEST PATH TO GITHUB
===============================

1. Go to https://github.com/new
2. Create repo named: nfl-betting-system
3. Open PowerShell and run:

```powershell
# Clone the new repo
cd Desktop
git clone https://github.com/YOUR_USERNAME/nfl-betting-system.git
cd nfl-betting-system

# Configure git (one time)
git config user.name "Your Name"
git config user.email "your@email.com"

# Copy your project files
cp -r C:\Users\scott\Desktop\nfl-betting-systemv2\* . -Force -Exclude .git

# Push to GitHub
git add .
git commit -m "Initial commit: NFL betting system"
git branch -M main
git push -u origin main
```

That's it! Your project is now on GitHub.


COMMON COMMANDS
===============

Check status:
```powershell
git status
```

Add files:
```powershell
git add .
```

Commit:
```powershell
git commit -m "Your message"
```

Push to GitHub:
```powershell
git push
```

Pull from GitHub (if working on multiple computers):
```powershell
git pull
```

See commit history:
```powershell
git log
```

View what changed:
```powershell
git diff
```


WORKFLOW (AFTER INITIAL SETUP)
==============================

Make changes → Commit → Push

```powershell
# 1. Make changes to files
# 2. Check what changed
git status

# 3. Stage files
git add .

# 4. Commit with message
git commit -m "Update: Improved injury agent performance"

# 5. Push to GitHub
git push
```


GITHUB WORKFLOW
===============

Your Local Machine ← → GitHub Server (Remote)

Pull (get latest from GitHub):
```powershell
git pull origin main
```

Push (send to GitHub):
```powershell
git push origin main
```


CREATING BRANCHES (OPTIONAL BUT RECOMMENDED)
=============================================

For big features, create a branch:

```powershell
# Create and switch to new branch
git checkout -b feature/injury-diagnostics

# Make changes
# ... edit files ...

# Commit
git add .
git commit -m "Add injury diagnostic system"

# Push branch to GitHub
git push -u origin feature/injury-diagnostics

# Go to GitHub and create Pull Request
# Click "Compare & pull request"
# Review changes
# Click "Merge pull request"
# Delete branch
```

Back to main:
```powershell
git checkout main
git pull origin main
```


IGNORING FILES (.gitignore)
============================

Critical - add to .gitignore:
```
.env
*.db
__pycache__/
.vscode/
.idea/
venv/
```

Then:
```powershell
git rm --cached .env
git commit -m "Remove .env from git tracking"
git push
```


FIXING MISTAKES
===============

Undo last commit (before push):
```powershell
git reset HEAD~1
```

Undo last push (dangerous, use only if necessary):
```powershell
git push --force-with-lease origin main
```

Undo changes to a file:
```powershell
git checkout filename.py
```

See what you're about to push:
```powershell
git log origin/main..HEAD
```


GITHUB FEATURES TO USE
======================

1. Issues - Track bugs/features
   - Click "Issues" tab
   - Click "New issue"
   - Describe problem/feature
   - Anyone can see it

2. Discussions - Ask questions
   - Click "Discussions" tab
   - Start conversations

3. Projects - Kanban board
   - Click "Projects" tab
   - Create project
   - Organize tasks

4. Wiki - Documentation
   - Click "Wiki" tab
   - Add pages
   - Link to main README

5. Releases - Version your code
   ```powershell
   git tag v1.0.0
   git push origin v1.0.0
   ```
   Then on GitHub: Releases → Draft new release


USEFUL GITHUB LINKS
===================

Your repo:
https://github.com/YOUR_USERNAME/nfl-betting-system

Your profile:
https://github.com/YOUR_USERNAME

Settings (if you need to change repo settings):
https://github.com/YOUR_USERNAME/nfl-betting-system/settings

GitHub Docs (if you need help):
https://docs.github.com

Git Cheat Sheet:
https://education.github.com/git-cheat-sheet-education.pdf


GITHUB DESKTOP APP (ALTERNATIVE TO COMMAND LINE)
================================================

If you prefer GUI instead of PowerShell:

1. Download GitHub Desktop: https://desktop.github.com
2. Sign in with your GitHub account
3. Clone your repository
4. Make changes
5. Click "Commit to main"
6. Click "Push origin"

Much easier if you're not comfortable with command line!


MULTIPLE COMPUTERS
===================

Computer A (Desktop):
```powershell
git clone https://github.com/YOUR_USERNAME/nfl-betting-system.git
# Make changes
git add .
git commit -m "Changes from desktop"
git push
```

Computer B (Laptop):
```powershell
git clone https://github.com/YOUR_USERNAME/nfl-betting-system.git
# Start with latest code
git pull
# Make changes
git add .
git commit -m "Changes from laptop"
git push
```

Back to Computer A:
```powershell
git pull  # Get changes from laptop
```


PRIVATE VS PUBLIC REPO
======================

Public (everyone can see):
- Good for portfolio
- Good for collaboration
- Sharing with world
- Default on free tier

Private (only you/collaborators):
- Keep secrets safe
- Internal projects
- Requires free GitHub account
- Good for .env files and credentials


PROTECTING MAIN BRANCH (RECOMMENDED)
====================================

Settings → Branches → Add rule:
- Branch name pattern: main
- Require pull request reviews before merging ✓
- Dismiss stale pull request approvals ✓

Forces you to create branches and review before merging!


FINAL CHECKLIST
===============

☐ Created GitHub account
☐ Created nfl-betting-system repository
☐ Cloned it to your computer
☐ Copied project files into cloned folder
☐ Created/updated .gitignore
☐ Configured git user.name and user.email
☐ Made first commit: git add . && git commit -m "Initial commit"
☐ Pushed to GitHub: git push -u origin main
☐ Verified files appear on GitHub.com
☐ Updated README.md
☐ Added topics/tags to repo
☐ Made repo public (if desired)

Done! 🎉


NEED HELP?
==========

Most common errors:

1. "Permission denied" → Token/password issue
   → Generate new token on GitHub
   
2. ".env showing in git" → .gitignore not working
   → git rm --cached .env && git commit -m "Remove .env"
   
3. "Nothing happens when I push" → Check if main branch exists
   → git branch -M main && git push -u origin main

4. "Large file" → Git is rejecting files over 100MB
   → Delete or gitignore the file

For real help:
→ https://docs.github.com/en/get-started

================================================================================
