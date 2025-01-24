
build_path="dist"

# Generate requirements
poetry export --no-interaction --without-hashes --format=requirements.txt > requirements.txt

# Build wheel
poetry build --no-interaction --format=wheel
wheel=`ls $build_path/*.whl`

# Create zip
zip $wheel requirements.txt --out $ZIP_FILE

echo "Zip created: $ZIP_FILE"

