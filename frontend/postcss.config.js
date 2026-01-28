// PostCSS 配置 - 移动端适配
const path = require('path')

module.exports = {
  plugins: {
    // autoprefixer - 自动添加浏览器前缀
    autoprefixer: {
      overrideBrowserslist: [
        'Android >= 4.4',
        'iOS >= 9',
        'Chrome >= 51',
        'Safari >= 9'
      ]
    },
    // postcss-pxtorem - px转rem (适配不同屏幕尺寸)
    'postcss-pxtorem': {
      rootValue: 37.5, // 设计稿宽度的1/10 (375px设计稿 / 10 = 37.5)
      unitPrecision: 5, // rem精度
      propList: ['*'], // 需要转换的属性，* 表示所有
      selectorBlackList: ['.no-rem'], // 不进行rem转换的选择器
      replace: true,
      mediaQuery: false, // 允许在媒体查询中转换px
      minPixelValue: 2, // 小于2px的不转换
      exclude: /node_modules/i // 排除node_modules目录
    }
  }
}

