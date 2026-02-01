# Enabling GitHub Pages for the UI

1. Go to your repository on GitHub: https://github.com/yskhub/Vigil
2. Settings → Pages
3. Under 'Build and deployment' choose 'GitHub Actions' (the workflow is already added at `.github/workflows/pages.yml`).
4. Save — GitHub Actions will publish the `agentic-honeypot/ui` folder to Pages after the next push to `main`.

Note: You may need to wait a minute for the first deployment to complete. The workflow is already in the repo.
