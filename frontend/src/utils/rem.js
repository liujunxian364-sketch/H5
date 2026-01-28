// rem适配脚本 - 在App.vue中引入
(function (doc, win) {
  const docEl = doc.documentElement
  const resizeEvt = 'orientationchange' in window ? 'orientationchange' : 'resize'
  
  // 设置根字体大小
  const recalc = function () {
    const clientWidth = docEl.clientWidth
    if (!clientWidth) return
    
    // 设计稿宽度为375px，根字体大小设为37.5（375/10）
    // 这样1rem = 37.5px (设计稿), 方便计算
    // 实际设备：屏幕宽度 / 10 = 根字体大小
    const fontSize = 100 * (clientWidth / 375)
    
    // 最小字体大小限制
    const minFontSize = 50 // 最小屏幕320px时，字体大小约为85
    // 最大字体大小限制  
    const maxFontSize = 150 // 最大屏幕时不超过150
    
    if (fontSize < minFontSize) {
      docEl.style.fontSize = minFontSize + 'px'
    } else if (fontSize > maxFontSize) {
      docEl.style.fontSize = maxFontSize + 'px'
    } else {
      docEl.style.fontSize = fontSize + 'px'
    }
  }
  
  // 禁止双击缩放
  docEl.addEventListener('touchstart', function (event) {
    if (event.touches.length > 1) {
      event.preventDefault()
    }
  })
  
  let lastTouchEnd = 0
  docEl.addEventListener('touchend', function (event) {
    const now = Date.now()
    if (now - lastTouchEnd <= 300) {
      event.preventDefault()
    }
    lastTouchEnd = now
  }, false)
  
  // 页面加载和窗口大小改变时重新计算
  if (!doc.addEventListener) return
  win.addEventListener(resizeEvt, recalc, false)
  doc.addEventListener('DOMContentLoaded', recalc, false)
  recalc()
})(document, window)

