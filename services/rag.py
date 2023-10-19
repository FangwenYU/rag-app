from langchain.chains import StuffDocumentsChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import services.const as const


PROMPT_TEMPLATE_QA = '''根据以下给定的内容回答问题：
-----
{context}
-----
根据上面给定的材料尝试回答问题，并注意以下几个要求：
1. 答案内容要来自给定的材料，不要杜撰和随意发挥
2. 回答要自然连贯，具有专业性
3. 如果没有找到合适的答案，请直接回答 "抱歉，根据提供的材料无法回答您的问题，请尝试其他问题。"
4. 直接回答问题，不要以"根据给定的材料"为开始

以下是问题：
-----
{query}
-----

再次注意，不要以"根据给定的材料"为开始
'''


def generate_answer(query, docs):
    # Override prompts
    document_prompt = PromptTemplate(
        input_variables=["page_content"], template="{page_content}"
    )
    document_variable_name = "context"

    llm = ChatOpenAI(model=const.LLM_GPT_35_16K, streaming=True, temperature=0.0, request_timeout=120)

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE_QA, input_variables=["context", "query"]
    )

    # Instantiate the chain
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_prompt=document_prompt,
        document_variable_name=document_variable_name,
    )
    generated_answer = chain.run(input_documents=docs, query=query)
    return generated_answer


def query_doc(retriever, q):

    retrieved_docs = retriever.get_relevant_documents_ordered(q)
    # for retrieved_doc in retrieved_docs:
    #     print('^'*20)
    #     print(retrieved_doc.metadata)
    #     print(retrieved_doc.page_content)

    answer = generate_answer(q, retrieved_docs)

    print(f'问题：{q}')
    print('-' * 10)
    print(answer)

    docs_metadata = distinct([doc.metadata for doc in retrieved_docs])

    result = {'summary': answer,
              'detail': docs_metadata}

    return result


def search_doc(retriever, q):
    retrieved_docs = retriever.get_relevant_documents(q, top_k=10)
    docs_metadata = distinct([doc.metadata for doc in retrieved_docs])

    total_amount = 0
    lose_case_cnt = 0
    case_cnt = len(docs_metadata)
    for meta in docs_metadata:
        total_amount += meta['amount']
        lose_case_cnt += 1 if meta['result'] == 'lose' else 0

    result = {'summary': f'一共有{case_cnt}个相似案件, 涉案金额{total_amount}, 判输案件数{lose_case_cnt}',
              'detail': docs_metadata}
    print(result)

    return result


def distinct(meta_list):
    distinct_list = []
    distinct_key = set()
    for meta in meta_list:
        case = meta['case']
        if case not in distinct_key:
            distinct_key.add(case)
            distinct_list.append(meta)
    return distinct_list


if __name__ == '__main__':
    from services.retriever import get_retriever

    doc_retriever = get_retriever()
    # query_doc(doc_retriever, '什么情况下可以减刑？')
    # print('\n')
    # query_doc(doc_retriever, '什么是RAG？')
    # print('\n')
    # query_doc(doc_retriever, '张扣扣犯的是什么罪？')
    search_doc(doc_retriever, '赌博案件')
    print('\n')
    # query_doc(doc_retriever, '介绍下杭州保姆纵火案')
