# Dify 变量提取重构总结

## 重构内容

已完成对 `app/services/dify_service.py` 的变量提取逻辑重构,使其更加通用和可复用。

## 新增功能

### 1. 通用变量提取方法 `extract_variable()`

```python
async def extract_variable(
    self,
    client: AsyncChatClient,
    conversation_id: str,
    variable_name: str,
    user_id: str,
    result: Optional[Dict[str, Any]] = None
) -> Optional[Any]:
```

**功能**: 从 Dify chatflow 响应中提取指定的变量

**提取优先级**:
1. Conversation Variables API (推荐)
2. Response.conversation_variables
3. Response.outputs
4. Response.metadata

**自动处理**:
- JSON 字符串自动解析为 Python 对象
- 支持 string、number、json、array 等类型
- 完整的日志追踪

### 2. 批量变量提取方法 `extract_multiple_variables()`

```python
async def extract_multiple_variables(
    self,
    client: AsyncChatClient,
    conversation_id: str,
    variable_names: list[str],
    user_id: str,
    result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
```

**功能**: 一次提取多个变量,返回字典

**返回格式**: `{variable_name: value, ...}`

### 3. 配置文件变量管理

在 `app/config.py` 中添加:

```python
dify_output_variables: list[str] = [
    "confirmation_record",    # 确认记录
    # 添加其他变量...
]
```

**优点**: 集中管理所有 workflow 输出变量,方便维护

## 使用示例

### 提取单个变量

```python
confirmation_record = await dify_service.extract_variable(
    client=client,
    conversation_id=conversation_id,
    variable_name='confirmation_record',
    user_id='user_123',
    result=result
)
```

### 提取多个变量

```python
variables = await dify_service.extract_multiple_variables(
    client=client,
    conversation_id=conversation_id,
    variable_names=['confirmation_record', 'document_type', 'confidence_score'],
    user_id='user_123',
    result=result
)
```

### 使用配置文件的变量列表

```python
from app.config import settings

variables = await dify_service.extract_multiple_variables(
    client=client,
    conversation_id=conversation_id,
    variable_names=settings.dify_output_variables,
    user_id='user_123',
    result=result
)
```

## 重构优势

### ✅ 可复用性
- 单一职责的提取方法
- 支持任意变量名
- 无需修改核心代码

### ✅ 可维护性
- 变量列表集中在配置文件
- 清晰的代码结构
- 完善的文档注释

### ✅ 可靠性
- 多级 fallback 机制
- 自动类型解析
- 详细的错误日志

### ✅ 可扩展性
- 添加新变量只需修改配置
- 批量提取方法避免重复代码
- 易于添加新的提取逻辑

## 文件变更

### 修改的文件
- `app/services/dify_service.py` - 添加通用提取方法
- `app/config.py` - 添加变量配置

### 新增的文件
- `API_USAGE_VARIABLES.md` - 详细使用文档
- `example_variable_extraction.py` - 5个实用示例
- `VARIABLE_EXTRACTION_SUMMARY.md` - 本总结文档

## 迁移指南

如果您有其他使用旧方法的代码,可以这样迁移:

### 旧代码
```python
# 硬编码的变量提取
confirmation_record = result.get('outputs', {}).get('confirmation_record')
```

### 新代码
```python
# 使用通用方法
confirmation_record = await dify_service.extract_variable(
    client=client,
    conversation_id=conversation_id,
    variable_name='confirmation_record',
    user_id=user_id,
    result=result
)
```

## 后续建议

### 1. 更新 .env 配置
添加您的 workflow 输出变量:

```env
# 在 .env 中不需要配置,直接在 app/config.py 中维护
```

### 2. 更新 config.py
在 `dify_output_variables` 中添加所有您的 workflow 输出变量:

```python
dify_output_variables: list[str] = [
    "confirmation_record",
    "document_type",        # 添加新变量
    "extracted_data",       # 添加新变量
    "validation_result",    # 添加新变量
]
```

### 3. 更新路由层
在 `app/routers/dify.py` 中使用批量提取:

```python
@router.post("/process")
async def process_document(preview_url: str):
    result = await dify_service.process_document(preview_url)
    
    # 提取额外的变量
    if result['success']:
        # 已经包含 confirmation_record
        # 可以添加更多变量处理逻辑
        pass
    
    return result
```

## 测试建议

运行示例脚本测试功能:

```bash
python example_variable_extraction.py
```

## 相关文档

- **详细用法**: 查看 `API_USAGE_VARIABLES.md`
- **代码示例**: 查看 `example_variable_extraction.py`
- **Dify 官方文档**: https://docs.dify.ai/

## 问题排查

### 变量提取失败
1. 检查 conversation_id 是否正确
2. 查看日志了解提取流程
3. 确认变量名拼写正确
4. 确认 Dify workflow 确实输出了该变量

### JSON 解析失败
- 检查 Dify workflow 中变量的 value_type 设置
- 确认 JSON 格式正确
- 查看 warning 日志了解解析错误

---

**重构完成日期**: 2025-11-07
**重构人员**: GitHub Copilot
