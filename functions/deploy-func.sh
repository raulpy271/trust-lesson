
mkdir -p dist
rm -fr dist/*
cp -r function_app.py host.json local.settings.json requirements.txt .funcignore functions dist
cp -r ../api/api dist/api
cd dist
func azure functionapp publish $1
