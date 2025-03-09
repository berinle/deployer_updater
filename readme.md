## packaging for offline access

```sh
# run with machine that has internet access
pip download -r requirements.txt -d ./packages

# pip download --python-version 37 --no-deps -r requirements.txt -d ./packages
# pip download -r requirements.txt -d ./packages --python-version 37 --only-binary :all:
# zip up bundle
zip -r deployment_bundle.zip . -x venv/*

# install dependencies on machine without internet access
pip install --no-index --find-links=./packages -r requirements.txt
```
