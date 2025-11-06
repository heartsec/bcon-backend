# API 使用说明

## 修复说明

已修复上传和下载路径不匹配的问题：

### 之前的问题：
- **上传时**：PDF 存储为 `{processing_id}/{原始文件名.pdf}`
- **下载时**：尝试下载 `{processing_id}/original.pdf`
- 结果：路径不匹配，下载失败 ❌

### 修复后：
- **上传时**：PDF 统一存储为 `{processing_id}/original.pdf` ✅
- **下载时**：下载 `{processing_id}/original.pdf` ✅
- **响应中**：返回 `original_filename` 字段保存原始文件名

## API 端点

### 1. 上传 PDF

**请求：**
```http
POST /api/pdf/upload
Content-Type: multipart/form-data

file: [PDF文件]
```

**响应：**
```json
{
  "file_processing_id": "uuid-string",
  "pdf_path": "uuid/original.pdf",
  "image_path": "uuid/first_page.png",
  "original_filename": "your-file.pdf",
  "message": "PDF processed successfully"
}
```

### 2. 上传 PDF（PUT 方式）

**请求：**
```http
PUT /api/pdf/upload
Content-Type: multipart/form-data

file: [PDF文件]
```

**响应：**
```json
{
  "file_processing_id": "uuid-string",
  "pdf_path": "uuid/original.pdf",
  "image_path": "uuid/first_page.png",
  "original_filename": "your-file.pdf",
  "message": "PDF processed successfully"
}
```

**说明：**
- 功能与 POST 完全相同，但使用 PUT 方法（符合 RESTful 幂等性）
- 每次调用都会生成新的 processing_id
- 可根据前端需求选择使用 POST 或 PUT

### 3. 下载原始 PDF

**方式1：使用默认文件名（processing_id.pdf）**
```http
GET /api/pdf/files/{processing_id}/pdf
```

**方式2：使用原始文件名**
```http
GET /api/pdf/files/{processing_id}/pdf?filename=原始文件名.pdf
```

**示例：**
```bash
# 默认文件名
curl -O http://localhost:8000/api/pdf/files/abc123/pdf

# 指定原始文件名
curl -O "http://localhost:8000/api/pdf/files/abc123/pdf?filename=report.pdf"
```

### 4. 下载预览图

```http
GET /api/pdf/files/{processing_id}/preview
```

返回首页预览图（PNG格式）

## 前端集成示例

### JavaScript/TypeScript

```javascript
// 1. 上传 PDF
async function uploadPDF(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/pdf/upload', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  console.log('Processing ID:', result.file_processing_id);
  console.log('Original filename:', result.original_filename);
  
  return result;
}

// 2. 上传 PDF（使用 PUT 方法）
async function uploadPDFWithPut(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/pdf/upload', {
    method: 'PUT',
    body: formData
  });
  
  const result = await response.json();
  console.log('Processing ID:', result.file_processing_id);
  
  return result;
}

// 3. 下载 PDF（使用原始文件名）
async function downloadPDF(processingId, originalFilename) {
  const url = `http://localhost:8000/api/pdf/files/${processingId}/pdf?filename=${encodeURIComponent(originalFilename)}`;
  window.open(url, '_blank');
}

// 4. 显示预览图
function showPreview(processingId) {
  const imgUrl = `http://localhost:8000/api/pdf/files/${processingId}/preview`;
  document.getElementById('preview').src = imgUrl;
}

// 完整流程
async function handleFileUpload(fileInput) {
  const file = fileInput.files[0];
  
  // 上传
  const result = await uploadPDF(file);
  
  // 显示预览
  showPreview(result.file_processing_id);
  
  // 提供下载按钮
  const downloadBtn = document.getElementById('downloadBtn');
  downloadBtn.onclick = () => downloadPDF(
    result.file_processing_id, 
    result.original_filename
  );
}
```

### Python 客户端

```python
import requests

# 上传
def upload_pdf(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            'http://localhost:8000/api/pdf/upload',
            files=files
        )
    return response.json()

# 上传（使用 PUT 方法）
def upload_pdf_put(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.put(
            'http://localhost:8000/api/pdf/upload',
            files=files
        )
    return response.json()

# 下载（保持原始文件名）
def download_pdf(processing_id, original_filename):
    params = {'filename': original_filename}
    response = requests.get(
        f'http://localhost:8000/api/pdf/files/{processing_id}/pdf',
        params=params
    )
    
    with open(original_filename, 'wb') as f:
        f.write(response.content)

# 使用示例
result = upload_pdf('document.pdf')
download_pdf(result['file_processing_id'], result['original_filename'])

# 或使用 PUT 方法上传
result_put = upload_pdf_put('another_document.pdf')
```

## 测试

启动服务器后访问：
- API 文档：http://localhost:8000/docs
- 交互式测试界面：http://localhost:8000/redoc
