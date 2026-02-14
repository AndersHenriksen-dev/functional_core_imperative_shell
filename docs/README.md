Generating the docs
----------

This documentation now uses Sphinx with numpydoc and autosummary.

Build locally with:

    sphinx-build -b html source _build/html

You can open `_build/html/index.html` in your browser.

Serve locally with:

    sphinx-autobuild source _build/html

GitHub Pages setup (docs/ folder)
-------------------------------

1. Build the docs so `docs/_build/html` is up to date.
2. In GitHub Pages settings, set source to `main` and folder to `/docs`.
3. Commit `docs/index.html` and `docs/.nojekyll` so Pages serves the HTML build.

GitHub Pages setup (GitHub Actions)
---------------------------------

1. In GitHub Pages settings, set source to `GitHub Actions`.
2. Push to `main` to deploy the docs workflow.
