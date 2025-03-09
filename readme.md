## packaging for offline access

```sh
# run with machine that has internet access
pip download -r requirements.txt -d ./packages

# zip up bundle
zip -r deployment_bundle.zip . -x venv/*
```
