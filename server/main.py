import uvicorn
from fastapi import FastAPI, HTTPException, Body, UploadFile, File
from fastapi.staticfiles import StaticFiles

__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from models.api import (
    QueryRequest,
    QueryResponse,
    QueryResult,
)

import services.asr as asr
import services.rag as rag
from services.retriever import get_retriever
from services.embedding import embed_text_files, embed_text_files_with_meta
import uuid
import os


app = FastAPI(
    title="RAG-App API",
    description="LLM-based RAG application. Ask your own document without hallucination.",
    version="1.0.0",
    servers=[{"url": "http://localhost:8080"}],
)
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")

# init global doc retriever
retriever = get_retriever('lawcases')
# embed_text_files(retriever, './docs/lawcases')
# embed_text_files_with_meta(retriever, './docs/lawcases')


def start():
    uvicorn.run("server.main:app", host="0.0.0.0", port=8080, reload=True)


@app.get(
    "/hello"
)
def hello():
    return "hello world"


@app.post(
    "/query",
)
def query(
    request: QueryRequest = Body(...),
):
    try:
        q = request.query.query
        result = rag.query_doc(retriever, q)
        query_result = QueryResult(query=q, result=result)
        response = QueryResponse(result=query_result)
        return response
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error - rag")


@app.post(
    "/search",
)
def search(
        request: QueryRequest = Body(...),
):
    try:
        q = request.query.query
        result = rag.search_doc(retriever, q)
        query_result = QueryResult(query=q, result=result)
        response = QueryResponse(result=query_result)
        return response
    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error - rag")


@app.post(
    "/asr-query"
)
async def asr_query(
        file: UploadFile = File(...)
):
    # get the file body from the upload file object
    mimetype = file.content_type
    print(f"mimetype: {mimetype}")
    print(f"file.file: {file.file}")
    print("file: ", file)

    query_input = asr_transcript(file)

    try:
        result = rag.query_doc(retriever, query_input)
        query_result = QueryResult(query=query_input, result=result)
        response = QueryResponse(result=query_result)
        return response
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=501, detail="Internal Service Error - (rag)")


@app.post(
    "/asr-search"
)
async def asr_search(
        file: UploadFile = File(...)
):
    # get the file body from the upload file object
    mimetype = file.content_type
    print(f"mimetype: {mimetype}")
    print(f"file.file: {file.file}")
    print("file: ", file)

    query_input = asr_transcript(file)

    try:
        result = rag.search_doc(retriever, query_input)
        query_result = QueryResult(query=query_input, result=result)
        response = QueryResponse(result=query_result)
        return response
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=501, detail="Internal Service Error - (rag)")


async def asr_transcript(audio_file):

    file_stream = await audio_file.read()

    cur_dir = os.path.abspath(os.curdir)
    temp_file_dir = os.path.join(cur_dir, 'tmp_file')
    temp_file_name = str(uuid.uuid4())
    temp_file_path = os.path.join(temp_file_dir, f'{temp_file_name}.mp3')

    # write the file to a temporary location
    with open(temp_file_path, "wb") as f:
        f.write(file_stream)

    try:
        query_input = asr.asr_file(temp_file_path).text
        print(query_input)
        os.remove(temp_file_path)
        return query_input
    except Exception as e:
        print(f"Error: {e}")
        # os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail="Internal Service Error - (asr)")
