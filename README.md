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
5. Start the application
```
poetry run start
```
and can find the API doc via ```localhost:8080/docs```



Note:
if running into the following error: 
```'HTTPResponse' object has no attribute 'strict'?```
Could be fixed by installing the older version of requests, refer to https://stackoverflow.com/questions/76423515/how-to-fix-poetry-error-httpresponse-object-has-no-attribute-strict

```pip install requests==2.29.0```


Note:
export poetry package depencies to requirements.txt

```poetry export --without-hashes --format=requirements.txt > requirements.txt``

