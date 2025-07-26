
mkdir -p dist
rm -fr dist/*
cp -r function_app.py host.json local.settings.json requirements.txt functions dist
cp -r ../api/api dist/api
