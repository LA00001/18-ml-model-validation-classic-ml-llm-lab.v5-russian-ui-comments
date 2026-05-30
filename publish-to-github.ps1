param(
    [string]$RepoName = "18-ml-model-validation-classic-ml-llm-lab"
)

git init
git add .
git commit -m "Add ML model validation classic ML LLM lab"
git branch -M main
git remote add origin "https://github.com/LA00001/$RepoName.git"
git push -u origin main
