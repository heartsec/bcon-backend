````markdown
# PDF Processing Backend with Dify Integration

FastAPI 后端服务，提供 PDF 文件上传、RustFS 对象存储、首页图片提取、文件缓存和 Dify AI 文档分析功能。

## ✨ 核心功能

- **PDF 上传处理**: 上传 PDF 文件并自动验证
- **唯一处理 ID**: 每次上传生成唯一的文件处理 ID
- **RustFS 对象存储**: 使用 RustFS (S3 兼容) 存储 PDF 和图片
- **首页图片提取**: 自动提取 PDF 首页为 PNG 图片
- **本地文件缓存**: 自动缓存下载的文件，提升访问速度
- **Dify AI 集成**: 使用 Dify 进行智能文档分析
- **有序存储**: 文件按处理 ID 组织存储

## 📁 项目结构

```
bcon-backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic 数据模型
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── pdf.py             # PDF 上传和下载接口
│   │   └── dify.py            # Dify AI 分析接口
│   └── services/
│       ├── __init__.py
│       ├── storage.py         # RustFS 对象存储服务
│       ├── pdf_processor.py   # PDF 处理服务
│       ├── cache.py           # 本地文件缓存服务
│       └── dify_service.py    # Dify AI 服务
├── cache/                      # 本地缓存目录
├── main.py                     # 应用程序入口
├── requirements.txt            # Python 依赖
├── .env.example               # 环境变量模板
├── Dockerfile                 # Docker 构建文件
├── README.md                  # 本文档
├── API_USAGE.md               # API 使用文档
├── DIFY_SETUP.md              # Dify 配置指南
└── DIFY_API_USAGE.md          # Dify API 使用说明
```

## 🚀 快速开始

### 前置要求

- Python 3.8+
- RustFS 服务器 (S3 兼容对象存储)
- **Poppler-utils** (PDF 处理必需)

### 1. 安装系统依赖

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils
```

**CentOS/RHEL:**
```bash
sudo yum install -y poppler-utils
```

**验证安装:**
```bash
pdftoppm -v
```

### 2. 创建虚拟环境

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 到 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置 RustFS 和 Dify：

```env
# RustFS 配置
RUSTFS_ENDPOINT=http://192.168.1.100:9000
RUSTFS_ACCESS_KEY=rustfsadmin
RUSTFS_SECRET_KEY=rustfssecret
RUSTFS_BUCKET_NAME=pdf-processing
RUSTFS_REGION=us-east-1

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000

# Dify 配置 (详见 DIFY_SETUP.md)
DIFY_API_KEY=app-xxxxxxxxxxxxxxxxxxxxxx
DIFY_BASE_URL=https://api.dify.ai/v1
```

**📝 获取 Dify API Key**：查看 [DIFY_SETUP.md](./DIFY_SETUP.md) 了解详细配置步骤。

### 5. 启动服务

**开发模式:**
```bash
python main.py
```

或使用 uvicorn：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Docker 模式:**
```bash
# 构建镜像
docker build -t bcon-backend .

# 运行容器
docker run -d \
  --name bcon-backend \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/cache:/app/cache \
  bcon-backend
```

### 6. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/pdf/health

## 📖 API 接口文档

### 1️⃣ PDF 上传处理

#### `POST /api/pdf/upload`

上传 PDF 文件进行处理（不包含 AI 分析）。

**请求:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF 文件)

**响应:**
```json
{
  "file_processing_id": "123e4567-e89b-12d3-a456-426614174000",
  "pdf_path": "123e4567-e89b-12d3-a456-426614174000/original.pdf",
  "image_path": "123e4567-e89b-12d3-a456-426614174000/first_page.png",
  "original_filename": "document.pdf",
  "message": "PDF processed successfully"
}
```

**示例:**
```bash
curl -X POST "http://localhost:8000/api/pdf/upload" \
  -F "file=@document.pdf"
```

---

### 2️⃣ 下载原始 PDF

#### `GET /api/pdf/files/{processing_id}/pdf`

下载原始 PDF 文件（带缓存）。

**请求参数:**
- `processing_id`: 文件处理 ID (路径参数)
- `filename`: 可选的下载文件名 (查询参数)

**响应:** PDF 文件流

**示例:**
```bash
# 使用默认文件名
curl -O "http://localhost:8000/api/pdf/files/123e4567-e89b-12d3-a456-426614174000/pdf"

# 指定下载文件名
curl -o "my-document.pdf" \
  "http://localhost:8000/api/pdf/files/123e4567-e89b-12d3-a456-426614174000/pdf?filename=invoice.pdf"
```

---

### 3️⃣ 下载预览图片

#### `GET /api/pdf/files/{processing_id}/preview`

下载 PDF 首页预览图（带缓存）。

**请求参数:**
- `processing_id`: 文件处理 ID (路径参数)

**响应:** PNG 图片流

**示例:**
```bash
curl -O "http://localhost:8000/api/pdf/files/123e4567-e89b-12d3-a456-426614174000/preview"
```

---

### 4️⃣ Dify AI 文档分析

#### `POST /dify/process-document`

上传 PDF 并使用 Dify 进行智能分析（一步完成：上传 + 提取 + 分析）。

**请求:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `file`: PDF 文件 (必需)
  - `user_id`: 用户标识符 (可选，默认: "default-user")

**响应:**
```json
{
  "success": true,
  "answer": "这是一张发票，包含以下信息...",
  "confirmation_record": {
    "document_type": "invoice",
    "total_amount": 1000.00,
    "invoice_number": "INV-2024-001",
    "verified": true
  },
  "conversation_id": "conv_xxxxx",
  "message_id": "msg_xxxxx",
  "metadata": {},
  "created_at": 1699999999
}
```

**示例:**
```bash
# 基本使用
curl -X POST "http://localhost:8000/dify/process-document" \
  -F "file=@invoice.pdf"

# 指定用户 ID
curl -X POST "http://localhost:8000/dify/process-document" \
  -F "file=@invoice.pdf" \
  -F "user_id=user-123"
```

**工作流程:**
1. 验证 PDF 文件
2. 提取首页为图片
3. 上传图片到 RustFS
4. 生成预签名 URL
5. 发送到 Dify 进行分析
6. 返回分析结果和 `confirmation_record`

---

### 5️⃣ 健康检查

#### `GET /api/pdf/health`

检查服务状态。

**响应:**
```json
{
  "status": "healthy",
  "service": "PDF Processing API"
}
```

**示例:**
```bash
curl "http://localhost:8000/api/pdf/health"
```

## 💾 文件存储结构

RustFS 中的文件按以下结构组织：

```
{bucket_name}/
└── {file_processing_id}/
    ├── original.pdf          # 原始 PDF 文件
    └── first_page.png        # 首页预览图片
```

**示例:**
```
pdf-processing/
└── 123e4567-e89b-12d3-a456-426614174000/
    ├── original.pdf
    └── first_page.png
```

### 本地缓存

下载的文件会自动缓存到 `cache/` 目录：

```
cache/
└── {file_processing_id}/
    ├── original.pdf
    └── first_page.png
```

**缓存优势:**
- 首次访问从 RustFS 下载
- 后续访问直接从本地缓存读取
- 大幅提升访问速度
- 减少 RustFS 请求次数

---

## 🔧 技术栈

### 核心依赖
- **FastAPI**: Web 框架
- **Uvicorn**: ASGI 服务器
- **pdf2image**: PDF 转图片 (需要 poppler-utils)
- **Pillow**: 图片处理
- **Boto3**: AWS S3 SDK (RustFS 兼容)
- **Pydantic**: 数据验证
- **dify-client**: Dify AI SDK (AsyncChatClient)

### 系统依赖
- **poppler-utils**: pdf2image 所需的 PDF 渲染库

---

## 🧪 测试

### 安装测试依赖
```bash
pip install pytest pytest-asyncio httpx
```

### 运行测试
```bash
# 所有测试
pytest

# 详细输出
pytest -v

# 特定测试文件
pytest test_dify_client.py
```

### 测试脚本
```bash
# 简单测试
python test_simple.py

# Dify 客户端测试
python test_dify_client.py

# 日志测试
python test_logging.py
```

---

## 📝 完整使用流程示例

### 场景 1: 上传并获取文件

```bash
# 1. 上传 PDF
RESPONSE=$(curl -X POST "http://localhost:8000/api/pdf/upload" \
  -F "file=@invoice.pdf")

# 2. 提取 processing_id
PROCESSING_ID=$(echo $RESPONSE | jq -r '.file_processing_id')

# 3. 下载原始 PDF
curl -o "downloaded.pdf" \
  "http://localhost:8000/api/pdf/files/${PROCESSING_ID}/pdf"

# 4. 下载预览图
curl -o "preview.png" \
  "http://localhost:8000/api/pdf/files/${PROCESSING_ID}/preview"
```

### 场景 2: 一步完成 AI 分析

```bash
# 上传 PDF 并进行 Dify 分析
curl -X POST "http://localhost:8000/dify/process-document" \
  -F "file=@invoice.pdf" \
  -F "user_id=user-123" | jq .
```

**响应示例:**
```json
{
  "success": true,
  "answer": "该文档是一张发票，包含以下关键信息：\n- 发票号码：INV-2024-001\n- 总金额：¥1,000.00\n- 开票日期：2024-01-15",
  "confirmation_record": {
    "document_type": "invoice",
    "invoice_number": "INV-2024-001",
    "total_amount": 1000.00,
    "date": "2024-01-15",
    "verified": true
  },
  "conversation_id": "conv_abc123",
  "message_id": "msg_def456"
}
```

---

## 🔒 生产环境注意事项

1. **CORS 配置**: 在 `main.py` 中更新 CORS 设置
2. **环境变量**: 使用安全的 `.env` 文件，不要提交到版本控制
3. **RustFS 配置**: 使用生产环境的 RustFS 凭证
4. **Dify API Key**: 妥善保管 API Key，设置合理的速率限制
5. **HTTPS**: 为 RustFS 端点启用 SSL/TLS
6. **身份验证**: 添加 API 认证中间件
7. **日志管理**: 配置日志轮转和监控
8. **缓存清理**: 定期清理 `cache/` 目录
9. **错误处理**: 实现完善的错误追踪和报告
10. **性能监控**: 使用 APM 工具监控服务性能

---

## 📚 相关文档

### 内部文档
- [API_USAGE.md](./API_USAGE.md) - 完整 API 使用文档和示例
- [DIFY_SETUP.md](./DIFY_SETUP.md) - Dify 云版本配置完整指南
- [DIFY_API_USAGE.md](./DIFY_API_USAGE.md) - Dify API 详细使用说明
- [QUICKSTART.md](./QUICKSTART.md) - 快速开始指南

### 外部资源
- [RustFS 文档](https://docs.rustfs.com/zh/)
- [RustFS Python SDK](https://docs.rustfs.com/zh/developer/sdk/python.html)
- [Dify 文档](https://docs.dify.ai/)
- [Dify Cloud](https://cloud.dify.ai/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)

---

## 🐛 故障排查

### PDF 处理失败

**错误:** `Failed to extract first page`

**解决方案:**
```bash
# 检查 poppler 是否安装
pdftoppm -v

# macOS 安装
brew install poppler

# Ubuntu/Debian 安装
sudo apt-get install poppler-utils
```

### RustFS 连接失败

**错误:** `Failed to upload to storage`

**检查清单:**
1. RustFS 服务是否运行
2. `.env` 中的 `RUSTFS_ENDPOINT` 是否正确
3. 访问密钥是否正确
4. 存储桶是否已创建

```bash
# 测试连接
curl http://your-rustfs-endpoint:9000/minio/health/live
```

### Dify API 错误

**错误:** `Invalid Dify API key`

**解决方案:**
1. 检查 `.env` 中的 `DIFY_API_KEY`
2. 确认 API Key 格式：`app-xxxxxx`
3. 查看 [DIFY_SETUP.md](./DIFY_SETUP.md) 获取新的 API Key

### 缓存问题

**清理缓存:**
```bash
# 删除所有缓存文件
rm -rf cache/*

# 或使用 Python 脚本
python cleanup_conversations.py
```

---

## 📄 许可证

本项目仅供内部使用。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📮 联系方式

如有问题，请联系项目维护者。

````

## Error Handling

The API includes comprehensive error handling:
- Invalid file type validation
- PDF validation
- Storage upload failures
- Image extraction errors

All errors return appropriate HTTP status codes with descriptive messages.

## Production Considerations

1. **CORS**: Update CORS settings in `main.py` for production
2. **Environment**: Use proper `.env` file with secure credentials
3. **Storage**: Configure production RustFS credentials
4. **Dify API Key**: 保护好你的 Dify API Key，不要提交到版本控制
5. **HTTPS**: Enable SSL/TLS for RustFS endpoints
6. **Authentication**: Add authentication middleware for production use
7. **Rate Limiting**: 考虑添加 API 速率限制
8. **RustFS Features**: Consider using RustFS advanced features like versioning, encryption, lifecycle management

## Additional Resources

### 📚 Documentation
- [DIFY_SETUP.md](./DIFY_SETUP.md) - Dify 云版本配置完整指南
- [DIFY_API_USAGE.md](./DIFY_API_USAGE.md) - Dify API 使用说明和示例
- [API_USAGE.md](./API_USAGE.md) - 完整 API 使用文档

### 🔗 External Links
- [RustFS Documentation](https://docs.rustfs.com/zh/)
- [RustFS Python SDK Guide](https://docs.rustfs.com/zh/developer/sdk/python.html)
- [Dify Documentation](https://docs.dify.ai/)
- [Dify Cloud](https://cloud.dify.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

This project is for internal use.
