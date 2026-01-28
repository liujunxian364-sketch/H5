# 📱 移动端调试完整指南

## 🎯 方案概览

提供4种移动端调试方案，从简单到高级，按需选择。

---

## 方案1: Chrome DevTools 设备模拟（推荐⭐⭐⭐⭐⭐）

### 优点
- ✅ **无需安装任何插件**
- ✅ 功能强大，最接近真实设备
- ✅ 支持触摸事件模拟
- ✅ 可以模拟网络速度

### 使用步骤

#### 1. 启动项目
```bash
cd frontend
npm run dev:h5
```

#### 2. 打开Chrome浏览器
访问：http://localhost:3000

#### 3. 开启设备模拟
- 按 `F12` 打开开发者工具
- 按 `Ctrl + Shift + M` 切换到设备模拟模式
- 或点击工具栏的 📱 图标

#### 4. 选择设备
顶部设备下拉菜单中选择：
- **iPhone SE** (320×568) - 测试最小屏幕
- **iPhone 12 Pro** (390×844) - 标准尺寸
- **iPhone 14 Pro Max** (428×926) - 大屏测试
- **Galaxy S20** - Android设备
- **iPad** - 平板测试

#### 5. 高级功能

**旋转屏幕:**
- 点击 🔄 图标切换横竖屏

**调整缩放:**
- 顶部缩放下拉菜单：50% / 75% / 100%

**限制网络速度:**
- Network标签 → Throttling → 选择 "Slow 3G" 或 "Fast 3G"

**查看元素尺寸:**
- 鼠标悬停在元素上，会显示实际像素尺寸

**触摸模拟:**
- 鼠标点击自动模拟触摸事件

### 快捷键
- `Ctrl + Shift + M` - 切换设备模式
- `Ctrl + Shift + I` - 打开/关闭开发者工具
- `Ctrl + Shift + C` - 选择元素

---

## 方案2: vConsole 移动端调试工具（推荐⭐⭐⭐⭐）

### 优点
- ✅ 在真实手机上显示控制台
- ✅ 查看网络请求
- ✅ 查看本地存储
- ✅ 查看系统信息

### 手动安装命令

**以管理员身份运行PowerShell或CMD，执行：**

```bash
cd C:\Users\Lenovo\Desktop\YidongH5\frontend
npm install vconsole --save
```

### 使用配置

安装成功后，在 `src/main.js` 中添加：

```javascript
// 开发环境启用 vConsole
if (import.meta.env.DEV) {
  import('vconsole').then(module => {
    new module.default()
  })
}
```

### 效果
页面右下角会出现绿色的 `vConsole` 按钮，点击即可查看：
- 📋 Log - 控制台日志
- 🌐 Network - 网络请求
- 📦 Storage - 本地存储
- ℹ️ System - 系统信息

---

## 方案3: 真机调试（推荐⭐⭐⭐⭐⭐）

### 优点
- ✅ 最真实的测试效果
- ✅ 测试实际性能
- ✅ 测试触摸手势

### 使用步骤

#### 方式A: 同一WiFi网络

1. **查看电脑IP地址**
```bash
# Windows
ipconfig

# 找到 "无线局域网适配器 WLAN" 的 IPv4 地址
# 例如: 192.168.1.100
```

2. **启动项目**
```bash
cd frontend
npm run dev:h5
```

3. **手机访问**
在手机浏览器输入：
```
http://192.168.1.100:3000
```
（将IP替换为你的实际IP）

#### 方式B: 使用二维码

安装二维码生成工具（可选）：
```bash
cd frontend
npm install -D qrcode-terminal
```

然后修改 `vite.config.js`，在启动时显示二维码。

#### 方式C: 使用内网穿透

如果不在同一网络，可以使用：
- **ngrok**: https://ngrok.com/
- **花生壳**: https://hsk.oray.com/

---

## 方案4: 浏览器扩展插件

### Chrome扩展推荐

#### 1. **Responsive Viewer**
- 同时预览多个设备尺寸
- Chrome商店搜索安装

#### 2. **Mobile Simulator**
- 模拟移动设备特性
- 支持地理位置、触摸等

---

## 🛠️ 调试技巧

### 1. 查看rem适配效果
在控制台执行：
```javascript
// 查看根字体大小
console.log(getComputedStyle(document.documentElement).fontSize)

// 查看屏幕宽度
console.log(window.innerWidth + 'px')

// 计算rem值
const pxToRem = (px) => px / parseFloat(getComputedStyle(document.documentElement).fontSize)
console.log('100px = ' + pxToRem(100) + 'rem')
```

### 2. 查看元素实际尺寸
```javascript
// 选择元素
const el = document.querySelector('.module-item')
console.log(el.getBoundingClientRect())
```

### 3. 测试触摸事件
在DevTools的Console中：
```javascript
// 监听触摸事件
document.addEventListener('touchstart', (e) => {
  console.log('触摸开始', e.touches[0])
})
```

### 4. 查看网络请求
- Network 标签
- 查看接口响应时间
- 查看请求参数

### 5. 性能分析
- Performance 标签
- 录制页面加载过程
- 查看FPS、内存使用

---

## 📊 调试检查清单

### 布局检查
- [ ] 在320px (iPhone SE) 显示正常
- [ ] 在375px (iPhone 8) 显示正常
- [ ] 在390px (iPhone 12 Pro) 显示正常
- [ ] 在428px (iPhone 14 Pro Max) 显示正常
- [ ] 横屏模式显示正常
- [ ] 不同缩放比例显示正常

### 交互检查
- [ ] 按钮可点击，大小合适（≥44px）
- [ ] 触摸反馈明显（颜色/缩放）
- [ ] 滚动流畅
- [ ] 长按不会选中文字（除输入框）
- [ ] 双击不会缩放

### 性能检查
- [ ] 首屏加载时间 < 3秒
- [ ] 页面滚动FPS ≥ 50
- [ ] 图片懒加载生效
- [ ] 无内存泄漏

### 兼容性检查
- [ ] iOS Safari
- [ ] Android Chrome
- [ ] 微信内置浏览器
- [ ] 各品牌手机的WebView

---

## 🎯 推荐调试流程

### 开发阶段
1. **Chrome DevTools** - 快速开发和调试
2. **切换不同设备** - 测试响应式
3. **Network限速** - 测试弱网环境

### 测试阶段  
1. **真机测试** - iPhone + Android各一台
2. **vConsole** - 查看真机日志
3. **记录问题** - 截图或录屏

### 上线前
1. **多设备测试** - 至少3种不同尺寸
2. **性能测试** - Lighthouse评分
3. **兼容性测试** - 主流浏览器

---

## 💡 常见问题

### Q1: Chrome设备模拟看不到触摸效果？
**A:** DevTools设置中勾选 "Show user agent shadow DOM"

### Q2: 真机访问不了电脑的localhost？
**A:** 
- 检查是否在同一WiFi
- 关闭电脑防火墙
- 使用IP地址而不是localhost

### Q3: vConsole安装失败？
**A:** 
- 以管理员身份运行CMD
- 或使用方案1（Chrome DevTools），无需安装插件

### Q4: 如何在微信中调试？
**A:** 
- 使用vConsole
- 或使用微信开发者工具的调试功能

### Q5: rem适配不生效？
**A:** 
- F12查看html根元素的font-size
- 确保index.html中的rem脚本已加载
- 检查是否有CSS覆盖了根字体大小

---

## 📝 手动安装命令汇总

### 以管理员身份运行，执行以下命令：

```bash
# 进入项目目录
cd C:\Users\Lenovo\Desktop\YidongH5\frontend

# 安装 vConsole（移动端控制台）
npm install vconsole --save

# 安装 PostCSS插件（可选）
npm install -D postcss-pxtorem autoprefixer

# 安装二维码工具（可选）
npm install -D qrcode-terminal
```

### 如果权限问题无法解决

**方案A: 清理npm缓存**
```bash
npm cache clean --force
npm install vconsole --save
```

**方案B: 使用yarn**
```bash
yarn add vconsole
```

**方案C: 手动下载**
直接在项目中引入CDN：
```html
<!-- 在 index.html 中添加 -->
<script src="https://cdn.jsdelivr.net/npm/vconsole@latest/dist/vconsole.min.js"></script>
<script>
  if (location.hostname !== 'localhost') {
    new window.VConsole();
  }
</script>
```

---

## 🚀 快速开始

### 最简单的方式（无需安装）

1. **启动项目**
```bash
cd frontend
npm run dev:h5
```

2. **打开Chrome浏览器**
访问: http://localhost:3000

3. **按 Ctrl+Shift+M**
立即进入移动设备模拟模式

4. **选择 iPhone 12 Pro**
开始调试！

---

**现在就可以开始移动端调试了！** 🎉

推荐优先使用 **Chrome DevTools**，无需安装任何插件，功能已经非常强大。

如需真机调试或更高级功能，再按需安装其他工具。

