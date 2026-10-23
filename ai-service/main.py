import os
import uuid
import sys
import requests
from fastapi import FastAPI, Form
import uvicorn
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from openai import OpenAI # 👈 新增导入

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
app = FastAPI(title="RAG AI Service")

print("正在加载 Embedding 模型到 GPU...")
model = SentenceTransformer('BAAI/bge-small-zh-v1.5', device='cuda')
client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "document_chunks"

# 👇 初始化硅基流动客户端
# ⚠️ 请把下面引号里的内容换成你自己的硅基流动 API Key！
SILICONFLOW_API_KEY = "sk-你的硅基流动KEY填在这里"
llm_client = OpenAI(
    api_key="",
    base_url="https://api.siliconflow.cn/v1"
)

if not client.collection_exists(COLLECTION_NAME):
    # 动态获取当前模型的向量维度（bge-small-zh-v1.5 是 512）
    test_emb = model.encode("测试").tolist()
    vector_size = len(test_emb)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    print(f"✅ 已自动创建 Collection，维度为: {vector_size}")
print("✅ 模型加载完毕，Qdrant 连接成功！")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI Service is running"}

# 原有的文档处理接口保持不变
@app.post("/api/v1/documents/process")
async def process_document(file_path: str = Form(...), kb_id: int = Form(...), doc_id: int = Form(...)):
    print(f"\n[收到处理请求] 文档ID={doc_id}, 知识库ID={kb_id}")
    if not os.path.exists(file_path):
        return {"code": 500, "message": "文件不存在"}
    

    content = ""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_ext == '.pdf':
            import pypdf
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"
            print(f"✅ 成功使用 pypdf 解析 PDF 文件")
            
        elif file_ext == '.docx':
            import docx
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                if para.text.strip():
                    content += para.text + "\n"
            print(f"✅ 成功使用 python-docx 解析 Word 文件")
            
        else: # 默认按照 TXT 处理，兼容各种编码
            encodings = ['utf-8', 'gbk', 'gb18030', 'big5', 'utf-16', 'utf-16le', 'utf-16be']
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        content = f.read()
                    print(f"✅ 成功使用 {enc} 编码读取 TXT 文件")
                    break
                except UnicodeDecodeError:
                    continue
                    
            if not content:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                print("⚠️ 遇到未知编码，已使用兜底模式强行读取")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return {"code": 500, "message": "文件解析失败"}
        
    if not content.strip():
        return {"code": 500, "message": "未能从文件中提取到有效文字"}

    chunk_size, overlap = 500, 100
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size - overlap) if len(content[i:i+chunk_size].strip()) > 0]
            
    print(f"✅ 成功分块，共 {len(chunks)} 块，开始 GPU 向量化...")
    embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False).tolist()

    points = [PointStruct(id=str(uuid.uuid4()), vector=emb, payload={"doc_id": doc_id, "kb_id": kb_id, "chunk_index": idx, "text": text}) for idx, (text, emb) in enumerate(zip(chunks, embeddings))]

    client.delete(collection_name=COLLECTION_NAME, points_selector=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"🎉 成功将 {len(points)} 个向量写入 Qdrant！")

    try:
        java_url = f"http://localhost:18080/api/documents/{doc_id}/status"
        res = requests.post(java_url, params={"status": "AVAILABLE"})
        if res.status_code == 200:
            print("✅ 成功通知 Java 更新状态为 AVAILABLE")
    except Exception as e:
        print(f"❌ 调用 Java 接口出错: {e}")

    return {"code": 200, "message": "处理完成", "data": {"status": "AVAILABLE", "chunks": len(chunks)}}

# 👇 新增：RAG 问答接口
@app.post("/api/v1/rag/answer")
async def rag_answer(question: str = Form(...), kb_id: int = Form(...)):
    print(f"\n[收到问答请求] 知识库ID={kb_id}, 问题: {question}")
    
    # 1. 问题向量化
    question_vector = model.encode(f"为这个句子生成表示以用于检索相关文章：{question}").tolist()
    
    # 2. 去 Qdrant 检索 (只检索当前 kb_id 的文本块)
    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=question_vector,
        query_filter=Filter(must=[FieldCondition(key="kb_id", match=MatchValue(value=kb_id))]),
        limit=5 # 取最相关的 5 个块
    ).points
    
    if not search_result:
        return {"code": 200, "message": "未找到相关文档", "data": {"answer": "抱歉，当前知识库没有相关内容。", "references": []}}
        
    # 3. 组装上下文和引用
    context_text = "\n\n---\n\n".join([point.payload["text"] for point in search_result])
    references = [{"doc_id": p.payload["doc_id"], "chunk_index": p.payload["chunk_index"], "text": p.payload["text"]} for p in search_result]
    
    # 4. 构建 Prompt
    prompt = f"""你是一个智能知识库助手，正在帮助用户解答关于文档的问题。
请综合以下提供的参考片段来回答用户的问题。
如果用户的提问是要求“总结”或“概括”，请根据片段内容进行合理的归纳和提炼。
如果参考片段确实与问题完全无关，再回答“根据现有资料，无法回答该问题”。

参考信息：
{context_text}

用户问题：{question}

请给出你的回答："""
    
    print("正在请求大模型生成答案...")
    try:
        # 5. 调用大模型
        response = llm_client.chat.completions.create(
            model="Qwen/Qwen2.5-72B-Instruct", # 这里用的是 72B 模型，也可以用 Qwen/Qwen3-8B 免费
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
        print("✅ 大模型回答完毕！")
        
        return {"code": 200, "message": "处理成功", "data": {"answer": answer, "references": references}}
    except Exception as e:
        print(f"❌ 大模型调用失败: {e}")
        return {"code": 500, "message": f"调用大模型失败: {e}"}

@app.delete("/api/v1/documents/{doc_id}")
async def delete_document_vectors(doc_id: int):
    print(f"\n[收到删除请求] 准备删除文档 ID={doc_id} 的向量")
    try:
        # 从 Qdrant 中按 doc_id 过滤并删除所有关联的向量块
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
            )
        )
        print(f"✅ 已成功从 Qdrant 删除文档 {doc_id} 的所有向量")
        return {"code": 200, "message": "向量删除成功"}
    except Exception as e:
        print(f"❌ 删除向量失败: {e}")
        return {"code": 500, "message": f"删除向量失败: {e}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18000)

