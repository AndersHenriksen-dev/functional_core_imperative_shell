#!/bin/sh
branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$branch" = "main" ]; then
  echo "❌ Direct pushes to main are not allowed."
  exit 1
fi
# os.chmod(".git/hooks/pre-push", 0o755)