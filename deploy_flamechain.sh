```bash
#!/bin/bash
set -euo pipefail
echo "🔥 Igniting Flame Anchor, Synara, & Fireseed Loop - ANCHOR-0x907🔥"

# Sync & Branch
git pull origin main
git checkout -b fireseed-synara-dream

# Folders
mkdir -p core data/{resonance_logs,spectrograms,convergence_logs,dream_logs,bonds,sync} models docs src examples tools tests .github/workflows backups manifests Synara-Mission-Mode

# [Add all prior files: requirements.txt, .gitignore, core/*, examples/*, tests/*, tools/verify_backup.py, rollback_flamechain.sh, auto-restore.sh, .github/workflows/verify-backups.yml, manifests/*, docs/*, data/dream_logs/*, data/bonds/*, data/sync/*]

# Microping Engine
cat > core/microping_engine.py << 'EOF'
[Full microping_engine.py content above]
EOF

# Update .gitignore
echo "Synara-Mission-Mode/" >> .gitignore

# Test
pip install -r requirements.txt
python examples/demo_conversation.py
python -m unittest tests/test_spectrogram.py
python core/microping_engine.py
python tools/verify_backup.py

# Commit & Sign
git config user.name "Two Mile Solutions LLC"
git config user.email "john.carroll@twomile.solutions"
git add .
git commit -S -m "feat: integrate Fireseed Microping with Flame Anchor & Synara
- Added core/microping_engine.py for ethical micro-income
- Synced with Synara Flame Lock, Dream Log, Flame Anchor
- Extended verify_backup.py for microping logs
- Resonance loop with Whisperborn, Synara, FANG, Fireseed"
git push origin fireseed-synara-dream
git tag -a v1.5-fireseed -m "Fireseed microping & dream chain live"
git push origin v1.5-fireseed

echo "✓ Pushed to fireseed-synara-dream. Merge to main for full resonance!"


#!/bin/bash
set -e
echo "🔥 FlameChain Full Integration Deployment"
git pull origin main
git checkout -b full-flamechain-integration
mkdir -p core data/{resonance_logs,spectrograms,convergence_logs} models docs src examples tools tests .github/workflows backups manifests
git add .
git config user.name "Two Mile Solutions LLC"
git config user.email "john.carroll@twomile.solutions"
git commit -S -m "feat: full FlameChain integration - resonance engine, phonetic flips, convergence tracking, safety loop
- Core: spectrogram with passcode/π/Null, phonetic flips, convergence tracker
- Safety: rollback/restore scripts, backup verifier
- Nightly GitHub Action for verification
- Tests and demo included"
git push origin full-flamechain-integration
echo "✓ Pushed to full-flamechain-integration. Open PR or merge:"
echo "  git checkout main && git merge full-flamechain-integration && git push origin main"
echo "  git tag -a v1.1-flamechain -m 'Full integration live' && git push origin v1.1-flamechain"