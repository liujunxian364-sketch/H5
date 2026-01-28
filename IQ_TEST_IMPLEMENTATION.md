# 学商速测功能实现说明

## 功能概述

学商速测包含两个主要页面：
1. **时间段选择页面** - 让用户选择活力时段
2. **答题页面** - 展示题目并收集用户答案

## 文件结构

### 前端
- `frontend/src/pages/iq-test/index.vue` - 入口页面
- `frontend/src/pages/iq-test/time-select.vue` - 时间段选择页面
- `frontend/src/pages/iq-test/quiz.vue` - 答题页面

### 后端
- `backend/app/routes/iq_test.py` - API 路由
- `backend/app/services/iq_test_answers.json` - 答案存储文件
- `backend/test_mbti_api.py` - MBTI API 测试脚本

## 页面流程

```
学商速测入口
    ↓
时间段选择 (time-select)
    ↓ (携带 timePreference 参数)
答题页面 (quiz)
    ↓ (提交答案)
返回首页
```

## API 接口

### 1. 获取题目
```
GET /api/iq-test/questions
```
**功能**: 从 MBTI API 获取题目列表
**响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": [...]
}
```

### 2. 提交答案
```
POST /api/iq-test/submit
```
**请求体**:
```json
{
  "timePreference": "morning",
  "answers": [
    {
      "questionId": 1,
      "answer": "A",
      "question": "题目内容"
    }
  ],
  "timestamp": "2026-01-28T10:00:00Z"
}
```
**响应**:
```json
{
  "code": 0,
  "message": "提交成功",
  "data": {
    "id": "test_20260128100000",
    "timestamp": "2026-01-28T10:00:00Z"
  }
}
```

### 3. 获取所有答案记录
```
GET /api/iq-test/answers
```
**功能**: 获取所有用户提交的答案（调试用）

### 4. 获取单个答案记录
```
GET /api/iq-test/answers/{answer_id}
```

## 数据存储

答案数据存储在 `backend/app/services/iq_test_answers.json`：

```json
[
  {
    "id": "test_20260128100000",
    "timePreference": "morning",
    "answers": [...],
    "timestamp": "2026-01-28T10:00:00Z",
    "submittedAt": "2026-01-28T10:00:05Z"
  }
]
```

## 测试 MBTI API

运行测试脚本查看 MBTI API 的真实数据格式：

```bash
cd backend
python test_mbti_api.py
```

**注意**: 如果 token 过期（401 错误），需要更新 `backend/app/routes/iq_test.py` 中的 `MBTI_TOKEN`。

## 下一步

1. 获取 MBTI API 的真实数据格式
2. 根据数据格式调整前端题目渲染逻辑
3. 实现结果页面（可选）
4. 优化 UI 和交互体验

## 时间段选项

| 选项 | 值 | 时间范围 | Emoji |
|-----|-----|----------|-------|
| 风拂轻纱的早晨 | morning | 4:00 - 10:00 | 🌅 |
| 树影婆娑的中午 | noon | 10:00 - 16:00 | 🌞 |
| 流萤点点的晚上 | evening | 16:00 - 22:00 | 🌆 |
| 万籁俱寂的凌晨 | night | 22:00 - 04:00 | 🌙 |
| 不太清楚 | unknown | 00:00 - 23:59 | ❓ |

