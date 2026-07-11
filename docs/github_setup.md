# Publishing to GitHub

```bash
git init
git add .
git commit -m "Build BeautyPulse analytics MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/beautypulse.git
git push -u origin main
```

Before every push:

```bash
git status
git diff --cached
pytest -q
```

Confirm that `data/raw/`, cookies, login state, screenshots containing user
names and `.streamlit/secrets.toml` are not staged. Git history is difficult to
clean after a credential or raw dataset is committed.

Suggested repository topics:

```text
data-science, consumer-analytics, beauty, nlp, streamlit, pandas, portfolio
```
