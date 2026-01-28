# 移动学习平台 - FastApp H5版本

基于 FastApp (uni-app + Vue 3) 构建的移动学习平台H5应用。
页面路由在 `pages.json` 中配置，无需使用 vue-router。
## 项目结构

```
frontend/
├── src/
│   ├── pages/          # 页面目录（uni-app规范）
│   │   ├── home/       # 首页
│   │   ├── error-memory/  # 错题记忆
│   │   ├── word-memory/   # 单词速记
│   │   ├── exam-qa/       # 考点答疑
│   │   ├── iq-test/       # 学商速测
│   │   └── news/          # 资讯
│   ├── components/     # 组件
│   ├── api/           # API接口
│   ├── App.vue        # 应用入口
│   └── main.js        # 主入口文件
├── manifest.json      # uni-app配置文件
├── pages.json        # 页面路由配置
└── vite.config.js    # Vite配置

backend/
├── app/
│   ├── routes/        # API路由
│   └── models/        # 数据模型
└── main.py           # FastAPI入口
```

## 快速开始

### 环境要求

**前端:**
- Node.js 16.0+ 
- npm 或 yarn

**后端:**
- Python 3.13+
- pip

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端服务运行在 `http://localhost:8000`

### 前端启动

```bash
cd frontend
npm install
npm run dev:h5
```

前端开发服务器运行在 `http://localhost:3000`

### 构建H5

```bash
cd frontend
npm run build:h5
```

构建产物在 `dist/build/h5` 目录

## 功能模块

### 1. 错题记忆
- 拍照上传错题
- 科目分类管理
- 知识点自动识别（OCR）
- 错题报告生成

### 2. 单词速记
- 选择要学习的单词书（支持初中、高中、四级、六级、考研、托福、SAT）
- 制定学习计划（设置每日学习单词数）
- 学习流程：学习（学习单词详情）->练习（根据单词选择正确的中文释义）->拼写（根据单词音节拆分单词卡片，选择单词卡片进行拼写）->默写（根据中文释义进行默写）
- 单词背诵完成后进入复习阶段，复习推送机制遵循SM-2算法，复习推送时间会由学习情况动态调整

### 3. 考点答疑
- 接入Dify工作流，对话形式界面；
- 工作流返回的内容需可以流式展现，支持上下文长记忆；
- 支持查看历史会话；

### 4. 学商速测
- 用户输入学习成绩（包含各科详细成绩），个人信息（出生年月日），选择测试类型（MBTI/MMPI等性格测试）后进行答题测试；
- 输入的成绩，信息，以及测试后的成绩和分析，接入工作流进行汇总以及分析后，生成解析内容；

## 技术栈

### 前端
- **Vue 3** (Composition API)
- **uni-app** (跨平台框架，H5端)
- **Vite** (构建工具)
- **Sass** (CSS预处理器)
- **vconsole** (移动端调试工具)
- **postcss-pxtorem** (移动端适配)
- **autoprefixer** (CSS兼容性)

### 后端
- **FastAPI** (Python Web框架)
- **Python 3.13+**
- **SQLite** (当前使用内存存储)
- **Uvicorn** (ASGI服务器)
- **Pydantic** (数据验证)
- **SQLAlchemy** (ORM)

## 注意事项

1. **图片上传**: 目前图片存储在本地 `backend/uploads/` 目录，生产环境建议使用OSS或CDN
2. **OCR识别**: 当前使用模拟数据，需要接入真实的大模型API
3. **跨域**: 开发环境已配置CORS，生产环境需要配置正确的跨域策略
4. **路由**: uni-app 项目使用 `pages.json` 管理页面路由，不使用 vue-router
5. **移动端适配**: 已配置动态 rem 适配方案，基于 375px 设计稿宽度
6. **调试**: 开发环境已集成 vConsole 移动端调试工具

## 项目依赖说明

### 前端核心依赖
- `@dcloudio/uni-app`: uni-app 核心包
- `@dcloudio/uni-components`: uni-app 组件库
- `@dcloudio/uni-h5`: uni-app H5 端支持
- `@dcloudio/uni-i18n`: uni-app 国际化支持
- `vue`: Vue 3 框架

### 前端开发依赖
- `@dcloudio/vite-plugin-uni`: uni-app Vite 插件
- `@vitejs/plugin-vue`: Vue 3 Vite 插件
- `sass`: Sass 样式预处理器
- `vconsole`: 移动端调试工具（仅开发环境）
- `postcss-pxtorem`: px 转 rem 插件
- `autoprefixer`: CSS 自动添加浏览器前缀

### 后端依赖
- `fastapi`: Web 框架
- `uvicorn`: ASGI 服务器
- `pydantic`: 数据验证
- `python-multipart`: 文件上传支持
- `sqlalchemy`: ORM
- `aiosqlite`: 异步 SQLite 支持

## 开发说明

本项目使用 uni-app 框架，支持：
- H5 开发（当前主要平台）
- 微信小程序（可扩展）
- App（可扩展）

页面路由在 `pages.json` 中配置，无需使用 vue-router。
