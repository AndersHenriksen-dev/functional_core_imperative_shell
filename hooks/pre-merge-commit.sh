#!/bin/sh
branch="$(git rev-parse --abbrev-ref HEAD)"

if [ "$branch" = "main" ]; then
  echo "✅ Merging into main is allowed."
else
  echo "❌ You must rebase your branch before merging into main."
  echo "Try: git pull --rebase origin main"
  exit 1
fi
# os.chmod(".git/hooks/pre-merge-commit", 0o755)