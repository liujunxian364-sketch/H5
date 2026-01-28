# 考点答疑功能设计文档

## 功能概述

实现一个基于 Dify AI 的智能对话问答系统，支持多轮对话、图片上传、历史会话管理等功能。

## 核心功能

### 1. 多轮对话 这个位置调取dify的日志接口 每轮对话对其conversationid 作为历史的对话记录 当用户关闭再次打开时就可以调到前端重新渲染对话记录了
url：http://deepseek.zkyc-ai.cn/v1
密钥：app-DoAn63W9Wck3bvEveCnwJZW1
对话接口是这样的：
https://deepseek.zkyc-ai.cn/app/e93105f7-fe7d-4563-afe1-4e17c380d87f/logs?conversation_id=e5b9dd45-a79e-4ac2-aebe-a994454f57a4&_rsc=44v9r
发起对话时记得保存conversation
conversation中的图片是存在dify里面的 所以直接用链接就可以了
- 支持连续对话，保持上下文
- 消息实时渲染（支持流式输出）
- 消息类型：文本、图片、系统提示

### 2. Dify API 集成
- 使用 Dify Workflow API 进行对话
- 支持流式响应（SSE）
- 传递对话历史作为上下文

### 3. 对话管理
- 创建新对话
开新的conversation  对话id是由dify定的
- 切换历史对话
- 删除对话
- 对话列表展示（标题、时间、最后一条消息）
前端对话框内要支持markdown渲染


### 4. 图片上传
- 拍照/从相册选择图片
- 图片随消息发送
- 图片预览

### 5. 数据持久化
- 对话会话存储
- 消息历史存储
- 图片文件存储

---

## 技术方案

### 前端（uni-app + Vue 3）

#### 页面结构
```
pages/exam-qa/
├── index.vue          # 对话列表页
├── chat.vue           # 对话详情页
└── components/
    ├── MessageItem.vue    # 消息项组件
    ├── InputBar.vue       # 输入栏组件
    └── ImageUploader.vue  # 图片上传组件
```

#### 关键组件设计

**1. 对话列表页 (index.vue)**
```vue
- 对话列表（标题、最后消息、时间）
- 新建对话按钮
- 删除对话（左滑删除）
- 点击进入对话详情
```

**2. 对话详情页 (chat.vue)**
```vue
- 顶部导航（对话标题、返回按钮）
- 消息列表（滚动到底部）
- 底部输入栏（文本输入、图片上传、发送按钮）
- 流式消息渲染
- 加载状态提示
```

**3. 消息项组件 (MessageItem.vue)**
```vue
- 用户消息（右侧，蓝色气泡）
- AI消息（左侧，白色气泡）
- 图片消息（点击放大）
- 时间戳
- 加载动画（AI回复中）
```

### 后端（FastAPI + Python）

#### API 接口设计

**1. 对话会话管理**
```python
# 获取对话列表
GET /api/exam-qa/conversations
Response: {
  "code": 0,
  "data": [
    {
      "id": "conv_123",
      "title": "数学问题求解",
      "last_message": "好的，我明白了",
      "updated_at": "2024-01-27T10:30:00"
    }
  ]
}

# 创建新对话
POST /api/exam-qa/conversations
Request: { "title": "新对话" }
Response: { "code": 0, "data": { "id": "conv_123", ... } }

# 删除对话
DELETE /api/exam-qa/conversations/{conversation_id}
Response: { "code": 0, "message": "删除成功" }
```

**2. 消息管理**
```python
# 获取对话历史
GET /api/exam-qa/conversations/{conversation_id}/messages
Response: {
  "code": 0,
  "data": [
    {
      "id": "msg_123",
      "role": "user",  # user | assistant | system
      "content": "这道题怎么做？",
      "image_url": null,
      "created_at": "2024-01-27T10:30:00"
    }
  ]
}

# 发送消息（支持流式响应）
POST /api/exam-qa/conversations/{conversation_id}/messages
Request: {
  "content": "这道题怎么做？",
  "image_url": "/uploads/questions/xxx.jpg"  # 可选
}
Response (SSE流式): 
data: {"type": "chunk", "content": "这道"}
data: {"type": "chunk", "content": "题可以"}
data: {"type": "done", "message_id": "msg_456"}
```

**3. 图片上传**
```python
# 上传图片
POST /api/exam-qa/upload
Request: multipart/form-data { file: <image> }
Response: {
  "code": 0,
  "data": {
    "url": "/uploads/questions/xxx.jpg",
    "filename": "xxx.jpg"
  }
}
```

**4. Dify API 调用**
```python
# 内部服务，不对外暴露
POST https://api.dify.ai/v1/workflows/run
Headers: {
  "Authorization": "Bearer {DIFY_API_KEY}",
  "Content-Type": "application/json"
}
Request: {
  "inputs": {
    "question": "用户问题",
    "image_url": "图片URL（可选）"
  },
  "conversation_id": "dify_conv_id",  # Dify侧的会话ID
  "user": "user_123",
  "response_mode": "streaming"  # streaming | blocking
}
```

#### 数据库设计

**conversations 表（对话会话）**
```sql
CREATE TABLE conversations (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),           # 用户ID（预留）
    title VARCHAR(200),            # 对话标题
    dify_conversation_id VARCHAR(100),  # Dify侧的会话ID
    last_message TEXT,             # 最后一条消息内容
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**messages 表（消息记录）**
```sql
CREATE TABLE messages (
    id VARCHAR(50) PRIMARY KEY,
    conversation_id VARCHAR(50),   # 外键关联 conversations
    role VARCHAR(20),              # user | assistant | system
    content TEXT,                  # 消息内容
    image_url VARCHAR(500),        # 图片URL（可选）
    dify_message_id VARCHAR(100),  # Dify侧的消息ID
    created_at TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

---

## 实现流程

### 1. 发送消息流程
```
1. 用户输入文本/上传图片
2. 前端：调用 POST /api/exam-qa/conversations/{id}/messages
3. 后端：
   a. 保存用户消息到数据库
   b. 获取对话历史（最近10条）
   c. 调用 Dify API（流式模式）
   d. 通过 SSE 返回流式响应给前端
   e. 保存 AI 回复到数据库
4. 前端：实时渲染 AI 回复（逐字显示）
```

### 2. 图片上传流程
```
1. 用户选择图片（拍照/相册）
2. 前端：压缩图片（最大1MB）
3. 前端：调用 POST /api/exam-qa/upload
4. 后端：保存图片，返回 URL
5. 前端：将图片 URL 随消息一起发送
6. 前端：在消息中显示图片预览
```

### 3. 对话切换流程
```
1. 用户在列表页点击对话
2. 前端：跳转到 chat.vue?id={conversation_id}
3. 前端：调用 GET /api/exam-qa/conversations/{id}/messages
4. 前端：渲染历史消息
5. 用户可以继续对话
```

---

## Dify 配置说明

### Workflow 输入变量
```yaml
inputs:
  - question: string      # 用户问题（必填）
  - image_url: string     # 图片URL（可选）
  - history: array        # 对话历史（可选，格式：[{role, content}]）
```

### Workflow 输出
```yaml
outputs:
  - answer: string        # AI回答
  - confidence: float     # 置信度（可选）
  - related_topics: array # 相关知识点（可选）
```

### API Key 配置
```python
# backend/.env
DIFY_API_KEY=app-xxxxxxxxxxxxx
DIFY_WORKFLOW_ID=workflow-xxxxxxxxxxxxx
DIFY_API_BASE_URL=https://api.dify.ai/v1
```

---

## 前端状态管理

### 使用 Composition API 管理状态
```javascript
// composables/useChat.js
export function useChat(conversationId) {
  const messages = ref([])
  const loading = ref(false)
  const inputText = ref('')
  
  // 加载历史消息
  const loadMessages = async () => { ... }
  
  // 发送消息（流式）
  const sendMessage = async (content, imageUrl) => {
    // 使用 EventSource 接收流式响应
    const eventSource = new EventSource(`/api/exam-qa/conversations/${conversationId}/messages`)
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'chunk') {
        // 逐字追加到最后一条消息
      }
    }
  }
  
  return { messages, loading, sendMessage, loadMessages }
}
```

---

## UI 设计要点

### 消息气泡样式
- 用户消息：右对齐，蓝色背景（#667eea）
- AI消息：左对齐，白色背景，带阴影
- 图片消息：圆角卡片，最大宽度60%

### 输入栏
- 多行文本输入框（自动调整高度）
- 图片按钮（相机图标）
- 发送按钮（输入内容时高亮）

### 加载状态
- AI思考中：显示"正在思考..."动画
- 流式输出：光标闪烁效果

### 移动端优化
- 虚拟滚动（消息过多时）
- 下拉加载更多历史消息
- 键盘弹出时自动滚动到底部

---

## 开发优先级

### Phase 1 - 基础对话（MVP）
1. ✅ 创建对话会话
2. ✅ 发送文本消息
3. ✅ 调用 Dify API（blocking 模式）
4. ✅ 显示消息列表

### Phase 2 - 流式响应
5. ✅ 实现 SSE 流式响应
6. ✅ 前端流式渲染

### Phase 3 - 增强功能
7. ✅ 图片上传
8. ✅ 对话历史管理
9. ✅ 对话标题自动生成

### Phase 4 - 优化体验
10. ✅ 消息加载优化
11. ✅ 错误处理和重试
12. ✅ 离线消息缓存

---

## 注意事项

1. **流式响应**: 使用 SSE（Server-Sent Events）而非 WebSocket，更轻量级
2. **图片处理**: 前端压缩后再上传，避免大文件占用带宽
3. **对话上下文**: 每次调用 Dify 时传递最近 N 条消息（如10条），避免 token 过多
4. **错误处理**: Dify API 调用失败时，保存用户消息，返回友好错误提示
5. **对话标题**: 自动从第一条消息生成标题（取前15个字符）
6. **性能优化**: 消息列表使用虚拟滚动，避免大量 DOM 节点

---

## 参考资源

- [Dify API 文档](https://docs.dify.ai/v/zh-hans/guides/application-publishing/developing-with-apis)
- [uni-app 网络请求](https://uniapp.dcloud.net.cn/api/request/request.html)
- [SSE（Server-Sent Events）](https://developer.mozilla.org/zh-CN/docs/Web/API/Server-sent_events)

