# Dify API 请求格式更新说明

## 修改内容

### 1. 请求体格式调整

**原格式：**
```json
{
  "inputs": {},
  "query": "用户问题",
  "response_mode": "streaming",
  "user": "default_user",
  "conversation_id": "xxx",
  "files": [...]
}
```

**新格式：**
```json
{
  "conversation_id": "",
  "files": [],
  "inputs": {},
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "parent_message_id": null,
  "query": "用户问题",
  "response_mode": "streaming"
}
```

### 2. 主要变化

1. ✅ **新增 `token` 字段**（硬编码）
   ```python
   token = "eyJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE3Njk1NjU1MDEsImV4cCI6MTc2OTYwODcwMSwidG9QbGF0Zm9ybSI6IjEiLCJ0eXBlIjoiMiIsInVzZXJJZCI6IjE5MTE3MTgyMzE2MjkzMDc5MDQyMzE3MjgifQ.pKcX9sc31AGUDZOsJW2IQO6JMclsE1TEKH_vFZxVQ9k"
   ```

2. ✅ **新增 `parent_message_id` 字段**（固定为 `null`）

3. ✅ **`conversation_id` 格式调整**
   - 首次对话：传空字符串 `""`
   - 后续对话：传实际的会话ID

4. ✅ **`files` 格式调整**
   - 首次对话或无文件：传空数组 `[]`
   - 有文件：传文件列表

5. ✅ **移除 `user` 字段**

### 3. 响应处理调整

**从响应中提取 `conversation_id`：**

原来从 `conversation_id` 字段获取，现在改为：
1. 优先从响应的 `id` 字段获取
2. 如果没有，再从 `conversation_id` 字段获取

```python
# 在 message 事件中
if event == "message":
    response_id = chunk.get("id")
    if response_id:
        dify_conv_id = response_id
    if chunk.get("conversation_id"):
        dify_conv_id = chunk.get("conversation_id")

# 在 message_end 事件中也再次尝试提取
elif event == "message_end":
    if not dify_conv_id and chunk.get("id"):
        dify_conv_id = chunk.get("id")
    if not dify_conv_id and chunk.get("conversation_id"):
        dify_conv_id = chunk.get("conversation_id")
```

---

## 修改的文件

1. `backend/app/services/dify_service.py`
   - 修改 `chat_streaming()` 方法的请求体格式
   - 添加硬编码的 token

2. `backend/app/routes/conversation.py`
   - 修改响应处理逻辑
   - 从 `id` 字段提取 `conversation_id`

---

## 使用示例

### 首次对话请求

```bash
POST http://deepseek.zkyc-ai.cn/v1/chat-messages

{
  "conversation_id": "",
  "files": [],
  "inputs": {},
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "parent_message_id": null,
  "query": "你好",
  "response_mode": "streaming"
}
```

### 后续对话请求

```bash
POST http://deepseek.zkyc-ai.cn/v1/chat-messages

{
  "conversation_id": "从首次响应中获取的ID",
  "files": [],
  "inputs": {},
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "parent_message_id": null,
  "query": "继续问题",
  "response_mode": "streaming"
}
```

### 带图片的请求

```bash
POST http://deepseek.zkyc-ai.cn/v1/chat-messages

{
  "conversation_id": "xxx",
  "files": [
    {
      "type": "image",
      "transfer_method": "remote_url",
      "url": "http://localhost:8000/uploads/exam_qa/xxx.jpg"
    }
  ],
  "inputs": {},
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "parent_message_id": null,
  "query": "这是什么？",
  "response_mode": "streaming"
}
```

---

## 重启服务

修改完成后，需要重启后端服务：

```bash
# 在后端终端
# 按 Ctrl+C 停止当前服务
# 然后重新启动
cd backend
python main.py
```

---

## 注意事项

⚠️ **Token 过期问题**

当前 token 是硬编码的，会在以下时间过期：
- `exp`: 1769545478 (Unix时间戳)
- 转换为日期：**2026-03-27**

如果 token 过期，需要更新 `backend/app/services/dify_service.py` 中的 token 值。

建议后续改为从环境变量读取：
```python
self.token = os.getenv("DIFY_TOKEN", "默认token")
```

