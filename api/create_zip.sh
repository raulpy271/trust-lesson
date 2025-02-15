
poetry export -n --without-hashes --format=requirements.txt > requirements.txt

poetry build -n --format=wheel

ZIP_FILE=`ls dist/*`

zip $ZIP_FILE requirements.txt host.json function.json


