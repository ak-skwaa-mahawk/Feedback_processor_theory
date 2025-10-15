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