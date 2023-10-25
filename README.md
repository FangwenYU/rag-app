# rag-app

## How to run on GCP

1. Clone the repository: 
```git clone https://github.com/FangwenYU/rag-app.git```
2. Create a new env (using conda)
```
cd rag-app
conda create --name rag-app python=3.8.17
conda activate rag-app
```
3. Install poetry
```
conda install poetry
```
4. Install packages using poetry
```
poetry install
```


Note:
if running into the following errors: 
```'HTTPResponse' object has no attribute 'strict'?```
Could be fixed by installing the older version of requests, refer to https://stackoverflow.com/questions/76423515/how-to-fix-poetry-error-httpresponse-object-has-no-attribute-strict

```pip install requests==2.29.0```