import os
import uuid
import sys
import requests
from fastapi import FastAPI, Form
import uvicorn
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
app = FastAPI(title="RAG AI Service")

print("正在加载 Embedding 模型到 GPU...")
model = SentenceTransformer('./all-MiniLM-L6-v2', device='cuda')
client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "document_chunks"

if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
print("✅ 模型加载完毕，Qdrant 连接成功！")

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI Service is running"}

@app.post("/api/v1/documents/process")
async def process_document(file_path: str = Form(...), kb_id: int = Form(...), doc_id: int = Form(...)):
    print(f"\n[收到处理请求] 文档ID={doc_id}, 知识库ID={kb_id}")
    if not os.path.exists(file_path):
        return {"code": 500, "message": "文件不存在"}
    
    # 👇 终极容错读取：遍历所有常见编码
    content = ""
    encodings = ['utf-8', 'gbk', 'gb18030', 'big5', 'utf-16', 'utf-16le', 'utf-16be']
    
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read()
            print(f"✅ 成功使用 {enc} 编码读取文件")
            break
        except UnicodeDecodeError:
            continue
            
    # 如果所有已知编码都失败了，强行读取（忽略错误，防止崩溃）
    if not content:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            print("⚠️ 遇到未知编码，已使用兜底模式强行读取（部分乱码可能被丢弃）")
        except Exception as e:
            print(f"❌ 读取文件彻底失败: {e}")
            return {"code": 500, "message": "文件编码无法识别"}
    # 👆 容错结束
        
    chunk_size, overlap = 500, 100
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size - overlap) if len(content[i:i+chunk_size].strip()) > 0]
            
    print(f"✅ 成功分块，共 {len(chunks)} 块，开始 GPU 向量化...")
    embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False).tolist()

    points = [PointStruct(id=str(uuid.uuid4()), vector=emb, payload={"doc_id": doc_id, "kb_id": kb_id, "chunk_index": idx, "text": text}) for idx, (text, emb) in enumerate(zip(chunks, embeddings))]

    client.delete(collection_name=COLLECTION_NAME, points_selector=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]))
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"🎉 成功将 {len(points)} 个向量写入 Qdrant！")

    # 通知 Java 后端更新状态
    try:
        java_url = f"http://localhost:18080/api/documents/{doc_id}/status"
        res = requests.post(java_url, params={"status": "AVAILABLE"})
        if res.status_code == 200:
            print("✅ 成功通知 Java 更新状态为 AVAILABLE")
    except Exception as e:
        print(f"❌ 调用 Java 接口出错: {e}")

    return {"code": 200, "message": "处理完成", "data": {"status": "AVAILABLE", "chunks": len(chunks)}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18000)