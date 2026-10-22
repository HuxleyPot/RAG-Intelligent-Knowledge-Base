# ==================================================
# 向量数据库 RAG 检索最小 Demo
# 功能：文本向量化 → 写入 Qdrant → 向量相似度检索
# ==================================================

# 导入 Qdrant 向量数据库客户端核心类
from qdrant_client import QdrantClient
# 导入 Qdrant 数据模型：
# - Distance：相似度计算方式枚举（余弦/欧氏/点积等）
# - VectorParams：集合的向量配置（维度、距离度量）
# - PointStruct：向量数据点结构（ID + 向量 + 元数据）
from qdrant_client.models import Distance, VectorParams, PointStruct
# 导入 SentenceTransformer 文本向量化工具
# 用于将自然语言文本转换为固定维度的向量（Embedding）
from sentence_transformers import SentenceTransformer


print("1. 正在加载本地 Embedding 模型到 GPU (首次运行会自动下载)...")
# 加载轻量级 Embedding 模型 all-MiniLM-L6-v2
# 参数说明：
#   './all-MiniLM-L6-v2'：本地模型路径；若路径不存在，首次运行会自动从 HuggingFace 下载
#   device='cuda'：指定使用 GPU 加速编码；无 GPU 可改为 'cpu'
# 注意：该模型输出向量维度固定为 384 维，需与后续集合配置一致
model = SentenceTransformer('./all-MiniLM-L6-v2', device='cuda')


print("2. 正在连接本地 Qdrant...")
# 初始化 Qdrant 客户端，连接本地部署的 Qdrant 服务
# Qdrant 默认 HTTP 服务端口为 6333，gRPC 端口为 6334
client = QdrantClient(url="http://localhost:6333")

# 定义集合名称（类比关系型数据库中的「表」）
collection_name = "test_collection"

# 先判断集合是否已存在，避免重复创建抛出异常
if not client.collection_exists(collection_name):
    # 创建新的向量集合
    client.create_collection(
        collection_name=collection_name,
        # 向量核心配置：
        #   size=384：向量维度，必须与 Embedding 模型输出维度完全一致
        #   distance=Distance.COSINE：使用余弦相似度计算向量距离
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )


# 准备待入库的测试文本，覆盖3个不同领域，用于验证检索的区分度
texts = [
    "RAG 是一种结合检索和生成的技术。",
    "MySQL 是一个关系型数据库。",
    "红烧肉是一道经典的中式菜肴。"
]

print("3. 正在将文本向量化并写入 Qdrant...")
# 批量将文本转换为向量，并转为 Python list 格式（Qdrant 要求输入为列表）
embeddings = model.encode(texts).tolist()

# 构造 Qdrant 的数据点（PointStruct）
# 每个点包含 3 部分：
#   id：唯一标识（int/str 类型，不可重复）
#   vector：对应文本的向量
#   payload：元数据负载（可存储原始文本、标签等业务信息，支持检索后返回）
points = [
    PointStruct(id=1, vector=embeddings[0], payload={"text": texts[0]}),
    PointStruct(id=2, vector=embeddings[1], payload={"text": texts[1]}),
    PointStruct(id=3, vector=embeddings[2], payload={"text": texts[2]}),
]

# 执行 upsert 操作：存在相同ID则更新，不存在则插入
client.upsert(collection_name=collection_name, points=points)


print("4. 正在检索测试...")
# 定义用户查询问题
query = "什么是检索增强生成？"
# 将查询文本同样转换为向量，用于和库中向量做相似度匹配
query_vector = model.encode(query).tolist()

# 执行向量检索
# 注意：新版 qdrant-client 用 query_points 替代了旧版的 search 方法
# 参数：
#   collection_name：检索的目标集合
#   query：查询向量
#   limit：返回最相关的结果数量
# 返回结果中 .points 为匹配到的点列表，按相似度从高到低排序
search_result = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=1
).points

# 打印检索结果
print(f"\n用户问题: {query}")
# 从 payload 中取出原始文本
print(f"检索到的最相关内容: {search_result[0].payload['text']}")
# 打印相似度得分：余弦相似度取值范围通常为 [0,1]，值越高代表越相似
print(f"相似度得分: {search_result[0].score:.4f}")
