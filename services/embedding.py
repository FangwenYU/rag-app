from services.retriever import get_retriever
from langchain.document_loaders import TextLoader
import os
import json


def load_text(text_file):
    return TextLoader(text_file).load()


def load_text_with_meta(text_file, case_meta):
    doc_list = []
    for doc in TextLoader(text_file).load():
        doc.metadata.update(case_meta)
        doc_list.append(doc)
    # print(doc_list)
    return doc_list


def load_text_files(files):
    docs = []
    for file in files:
        docs.extend(TextLoader(file).load())
    return docs


def embed_text_file(retriever, filepath):
    retriever.add_documents(load_text(filepath))


def embed_text_files(retriever, dir_name):
    cur_dir = os.path.abspath(os.curdir)
    doc_dir = os.path.join(cur_dir, dir_name)
    for f in os.listdir(doc_dir):
        text_file = os.path.join(doc_dir, f)
        retriever.add_documents(load_text(text_file))


def embed_text_files_with_meta(retriever, dir_name):
    cur_dir = os.path.abspath(os.curdir)
    doc_dir = os.path.join(cur_dir, dir_name)

    meta_data = load_metadata(doc_dir)
    for f in os.listdir(doc_dir):
        if f == 'metadata.json':
            continue
        text_file = os.path.join(doc_dir, f)
        case_name = f.split('.')[0]
        # print(case_name)
        retriever.add_documents(load_text_with_meta(text_file, meta_data[case_name]))


def load_metadata(dir_name):
    meta = {}
    for case_meta in json.load(open(os.path.join(dir_name, 'metadata.json'))):
        key = case_meta['case']
        meta[key] = case_meta
    return meta


if __name__ == '__main__':
    # embed_text_files(get_retriever(), '../docs/lawcases')
    # load_metadata('../docs/lawcases')
    retriever = get_retriever()
    embed_text_files_with_meta(retriever, '../docs/lawcases')
    docs = retriever.get_relevant_documents('郭美美案件')
    for doc in docs:
        print(doc.metadata)
