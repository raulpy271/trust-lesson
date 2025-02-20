
poetry export -n --without-hashes --format=requirements.txt > requirements.txt

cat function-requirements.txt >> requirements.txt

poetry build -n --format=wheel

ZIP_FILE=`ls dist/*`

zip $ZIP_FILE requirements.txt host.json function_app.py

# Create a ZIP with md5 hash in his name
md5s=( $(md5sum $ZIP_FILE) )
declare -p md5s
cp $ZIP_FILE "dist/out_${md5s[0]}.zip"
