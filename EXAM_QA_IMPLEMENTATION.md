# 考点答疑功能 - 使用说明

## ✅ 已完成功能

### 后端部分
1. ✅ **数据模型**：`backend/app/models/conversation.py`
   - Conversation（对话会话）
   - Message（消息记录）

2. ✅ **Dify API 集成**：`backend/app/services/dify_service.py`
   - 流式对话接口
   - 获取对话历史
   - 文件上传

3. ✅ **内存数据存储**：`backend/app/services/memory_store.py`
   - 对话CRUD操作
   - 消息存储和查询

4. ✅ **API 路由**：`backend/app/routes/conversation.py`
   - GET `/api/exam-qa/conversations` - 获取对话列表
   - POST `/api/exam-qa/conversations` - 创建新对话
   - DELETE `/api/exam-qa/conversations/{id}` - 删除对话
   - GET `/api/exam-qa/conversations/{id}/messages` - 获取消息历史
   - POST `/api/exam-qa/conversations/{id}/messages` - 发送消息（流式）
   - POST `/api/exam-qa/upload` - 上传图片

### 前端部分
1. ✅ **对话列表页**：`frontend/src/pages/exam-qa/index.vue`
   - 显示所有对话
   - 创建新对话
   - 删除对话
   - 时间格式化

2. ✅ **对话详情页**：`frontend/src/pages/exam-qa/chat.vue`
   - 消息列表展示
   - 流式消息接收（实时显示）
   - Markdown 渲染（代码块、列表等）
   - 图片上传和预览
   - 自动滚动到底部

3. ✅ **API 调用函数**：`frontend/src/api/index.js`
   - conversationApi.getList()
   - conversationApi.create()
   - conversationApi.delete()
   - conversationApi.getMessages()
   - conversationApi.uploadImage()

---

## 🚀 如何使用

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

新增的依赖：
- `httpx` - HTTP客户端，用于调用Dify API
- `python-dotenv` - 环境变量管理

### 2. 配置环境变量

在 `backend/` 目录创建 `.env` 文件：

```env
DIFY_API_KEY=app-DoAn63W9Wck3bvEveCnwJZW1
DIFY_API_BASE_URL=http://deepseek.zkyc-ai.cn/v1
DIFY_APP_ID=e93105f7-fe7d-4563-afe1-4e17c380d87f
```

### 3. 启动后端服务

```bash
cd backend
python main.py
```

后端运行在 `http://localhost:8000`

### 4. 安装前端依赖

```bash
cd frontend
npm install
```

新增的依赖：
- `marked` - Markdown 解析和渲染库

### 5. 启动前端服务

```bash
cd frontend
npm run dev:h5
```

前端运行在 `http://localhost:3000`

### 6. 使用功能

1. **访问考点答疑**
   - 在首页点击"考点答疑"按钮
   - 进入对话列表页

2. **创建新对话**
   - 点击右上角"➕新对话"按钮
   - 自动跳转到聊天页面

3. **发送消息**
   - 输入问题文本
   - 可选：点击📷按钮上传图片
   - 点击📤发送
   - AI会流式返回答案（逐字显示）

4. **查看历史对话**
   - 返回对话列表
   - 点击任意对话进入历史记录
   - 继续对话

5. **删除对话**
   - 在对话列表点击🗑️图标
   - 确认删除

---

## 📱 功能特性

### 1. 流式响应
- 使用 SSE（Server-Sent Events）实现
- AI回复逐字显示，体验流畅
- 打字指示器动画

### 2. Markdown 渲染
- 支持代码块语法高亮
- 支持列表、引用、链接等
- 代码块深色主题

### 3. 图片支持
- 拍照或从相册选择
- 图片预览
- 点击放大查看
- 随消息一起发送给AI

### 4. 对话管理
- 自动生成对话标题（取第一条消息前20字）
- 保存对话历史
- 多会话切换
- 会话删除

### 5. 移动端优化
- 响应式布局
- 键盘自适应
- 自动滚动到底部
- 触摸反馈动画

---

## 🔧 技术细节

### Dify API 调用流程

1. **发起对话**
   ```
   POST http://deepseek.zkyc-ai.cn/v1/chat-messages
   Headers:
     Authorization: Bearer app-DoAn63W9Wck3bvEveCnwJZW1
   Body:
     {
       "query": "用户问题",
       "conversation_id": "dify_conv_id", // 可选
       "response_mode": "streaming",
       "files": [...] // 可选
     }
   ```

2. **接收流式响应**
   ```
   data: {"event": "message", "conversation_id": "xxx", "message_id": "yyy"}
   data: {"event": "message_chunk", "delta": {"answer": "内容块"}}
   data: {"event": "message_end", ...}
   ```

3. **保存会话ID**
   - 首次对话后，Dify返回 `conversation_id`
   - 后续对话带上这个ID，保持上下文

### 数据流程

```
用户输入 
  → 前端chat.vue 
  → API: POST /exam-qa/conversations/{id}/messages
  → 后端保存用户消息
  → 调用Dify API（流式）
  → SSE流式返回给前端
  → 前端逐字渲染
  → 后端保存AI回复
```

---

## 🐛 调试技巧

### 1. 查看后端日志
```bash
# 后端终端会输出详细日志
# 包括Dify API调用、错误信息等
```

### 2. 查看前端日志
- 打开浏览器开发者工具
- Console 标签查看日志
- 或使用 vConsole（移动端调试）

### 3. 测试 API
访问 `http://localhost:8000/docs` 查看 Swagger API 文档

---

## ⚠️ 注意事项

1. **Dify API 配置**
   - 确保 `.env` 文件中的API Key正确
   - 确保网络可以访问 Dify 服务

2. **流式响应兼容性**
   - H5平台：使用 SSE
   - 小程序：需要使用 WebSocket（待实现）

3. **图片上传**
   - 图片会先上传到本地服务器
   - 然后将URL发送给Dify
   - Dify会获取图片并分析

4. **会话持久化**
   - 当前使用内存存储
   - 重启后端会丢失数据
   - 生产环境应使用数据库

---

## 📝 TODO（可选优化）

- [ ] 使用 SQLite 持久化数据
- [ ] 添加消息重发功能
- [ ] 添加语音输入
- [ ] 小程序端适配（WebSocket）
- [ ] 添加消息复制功能
- [ ] 添加会话导出功能
- [ ] 优化 Markdown 样式
- [ ] 添加加载更多历史消息

---

## 📞 技术支持

如有问题，请检查：
1. 后端服务是否正常运行
2. Dify API配置是否正确
3. 网络连接是否正常
4. 浏览器Console是否有错误信息

