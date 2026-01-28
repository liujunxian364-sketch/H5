<template>
  <div class="image-crop-overlay" v-if="visible" @click.self="handleCancel">
    <div class="image-crop-container">
      <div class="crop-header">
        <button class="btn-cancel" @click="handleCancel">取消</button>
        <h3>框选错题范围</h3>
        <button class="btn-confirm" @click="handleConfirm">确认</button>
      </div>
      <div class="crop-content">
        <div class="crop-wrapper" ref="cropWrapperRef">
          <img ref="imageRef" :src="imageSrc" @load="handleImageLoad" />
          <div
            class="crop-box"
            :style="cropBoxStyle"
            @mousedown="handleMouseDown"
            @touchstart="handleTouchStart"
          >
            <div class="crop-handle" v-for="(handle, index) in handles" :key="index"
              :class="`handle-${handle}`"
              :style="getHandleStyle(handle)"
              @mousedown.stop="handleResizeStart($event, handle)"
              @touchstart.stop="handleResizeStart($event, handle)"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  imageSrc: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['confirm', 'cancel'])

const cropWrapperRef = ref(null)
const imageRef = ref(null)

const cropData = ref({
  x: 0,
  y: 0,
  width: 100,
  height: 100
})

const isDragging = ref(false)
const isResizing = ref(false)
const resizeHandle = ref(null)
const dragStart = ref({ x: 0, y: 0 })

const handles = ['nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w']

const cropBoxStyle = computed(() => {
  return {
    left: `${cropData.value.x}px`,
    top: `${cropData.value.y}px`,
    width: `${cropData.value.width}px`,
    height: `${cropData.value.height}px`
  }
})

const handleImageLoad = () => {
  if (imageRef.value && cropWrapperRef.value) {
    const img = imageRef.value
    const wrapper = cropWrapperRef.value
    
    // 初始化裁剪框为图片中央区域
    const centerX = (img.clientWidth - 200) / 2
    const centerY = (img.clientHeight - 200) / 2
    
    cropData.value = {
      x: Math.max(0, centerX),
      y: Math.max(0, centerY),
      width: Math.min(200, img.clientWidth),
      height: Math.min(200, img.clientHeight)
    }
  }
}

const getHandleStyle = (handle) => {
  const size = 8
  const offset = -size / 2
  const styles = {
    position: 'absolute',
    width: `${size}px`,
    height: `${size}px`,
    backgroundColor: '#fff',
    border: '2px solid #667eea',
    borderRadius: '50%',
    cursor: `${handle}-resize`
  }
  
  switch (handle) {
    case 'nw':
      return { ...styles, top: `${offset}px`, left: `${offset}px` }
    case 'ne':
      return { ...styles, top: `${offset}px`, right: `${offset}px` }
    case 'sw':
      return { ...styles, bottom: `${offset}px`, left: `${offset}px` }
    case 'se':
      return { ...styles, bottom: `${offset}px`, right: `${offset}px` }
    case 'n':
      return { ...styles, top: `${offset}px`, left: '50%', transform: 'translateX(-50%)' }
    case 's':
      return { ...styles, bottom: `${offset}px`, left: '50%', transform: 'translateX(-50%)' }
    case 'e':
      return { ...styles, right: `${offset}px`, top: '50%', transform: 'translateY(-50%)' }
    case 'w':
      return { ...styles, left: `${offset}px`, top: '50%', transform: 'translateY(-50%)' }
    default:
      return styles
  }
}

const handleMouseDown = (e) => {
  if (e.target.classList.contains('crop-handle')) return
  isDragging.value = true
  dragStart.value = {
    x: e.clientX - cropData.value.x,
    y: e.clientY - cropData.value.y
  }
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleTouchStart = (e) => {
  if (e.target.classList.contains('crop-handle')) return
  isDragging.value = true
  const touch = e.touches[0]
  dragStart.value = {
    x: touch.clientX - cropData.value.x,
    y: touch.clientY - cropData.value.y
  }
  document.addEventListener('touchmove', handleTouchMove)
  document.addEventListener('touchend', handleTouchEnd)
}

const handleMouseMove = (e) => {
  if (!isDragging.value || isResizing.value) return
  if (!imageRef.value) return
  
  const newX = e.clientX - dragStart.value.x
  const newY = e.clientY - dragStart.value.y
  
  const maxX = imageRef.value.clientWidth - cropData.value.width
  const maxY = imageRef.value.clientHeight - cropData.value.height
  
  cropData.value.x = Math.max(0, Math.min(newX, maxX))
  cropData.value.y = Math.max(0, Math.min(newY, maxY))
}

const handleTouchMove = (e) => {
  e.preventDefault()
  if (!isDragging.value || isResizing.value) return
  if (!imageRef.value || !cropWrapperRef.value) return
  
  const touch = e.touches[0]
  const rect = cropWrapperRef.value.getBoundingClientRect()
  const newX = touch.clientX - rect.left - dragStart.value.x
  const newY = touch.clientY - rect.top - dragStart.value.y
  
  const maxX = imageRef.value.clientWidth - cropData.value.width
  const maxY = imageRef.value.clientHeight - cropData.value.height
  
  cropData.value.x = Math.max(0, Math.min(newX, maxX))
  cropData.value.y = Math.max(0, Math.min(newY, maxY))
}

const handleMouseUp = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

const handleTouchEnd = () => {
  isDragging.value = false
  document.removeEventListener('touchmove', handleTouchMove)
  document.removeEventListener('touchend', handleTouchEnd)
}

const handleResizeStart = (e, handle) => {
  e.preventDefault()
  e.stopPropagation()
  isResizing.value = true
  resizeHandle.value = handle
  const clientX = e.touches ? e.touches[0].clientX : e.clientX
  const clientY = e.touches ? e.touches[0].clientY : e.clientY
  
  dragStart.value = {
    x: clientX,
    y: clientY,
    width: cropData.value.width,
    height: cropData.value.height,
    left: cropData.value.x,
    top: cropData.value.y
  }
  
  const moveHandler = (e) => {
    e.preventDefault()
    if (!imageRef.value) return
    const currentX = e.touches ? e.touches[0].clientX : e.clientX
    const currentY = e.touches ? e.touches[0].clientY : e.clientY
    
    const deltaX = currentX - dragStart.value.x
    const deltaY = currentY - dragStart.value.y
    
    let newData = { ...cropData.value }
    
    // 简化版：只支持右下角拖拽调整大小
    if (handle === 'se') {
      newData.width = Math.max(50, dragStart.value.width + deltaX)
      newData.height = Math.max(50, dragStart.value.height + deltaY)
      
      if (newData.x + newData.width > imageRef.value.clientWidth) {
        newData.width = imageRef.value.clientWidth - newData.x
      }
      if (newData.y + newData.height > imageRef.value.clientHeight) {
        newData.height = imageRef.value.clientHeight - newData.y
      }
    }
    
    cropData.value = newData
  }
  
  const endHandler = (e) => {
    e.preventDefault()
    isResizing.value = false
    resizeHandle.value = null
    document.removeEventListener('mousemove', moveHandler)
    document.removeEventListener('mouseup', endHandler)
    document.removeEventListener('touchmove', moveHandler)
    document.removeEventListener('touchend', endHandler)
  }
  
  document.addEventListener('mousemove', moveHandler, { passive: false })
  document.addEventListener('mouseup', endHandler)
  document.addEventListener('touchmove', moveHandler, { passive: false })
  document.addEventListener('touchend', endHandler)
}

const handleConfirm = () => {
  emit('confirm', {
    x: cropData.value.x,
    y: cropData.value.y,
    width: cropData.value.width,
    height: cropData.value.height
  })
}

const handleCancel = () => {
  emit('cancel')
}

watch(() => props.visible, (newVal) => {
  if (newVal && imageRef.value) {
    handleImageLoad()
  }
})
</script>

<style scoped>
.image-crop-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-crop-container {
  width: 90%;
  max-width: 500px;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.crop-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.crop-header h3 {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
}

.btn-cancel,
.btn-confirm {
  padding: 8px 16px;
  font-size: 14px;
  border: none;
  background: transparent;
  cursor: pointer;
}

.btn-cancel {
  color: #999;
}

.btn-confirm {
  color: #667eea;
  font-weight: 500;
}

.crop-content {
  padding: 16px;
}

.crop-wrapper {
  position: relative;
  width: 100%;
  max-height: 60vh;
  overflow: hidden;
  border-radius: 8px;
}

.crop-wrapper img {
  width: 100%;
  height: auto;
  display: block;
}

.crop-box {
  position: absolute;
  border: 2px dashed #667eea;
  background: rgba(102, 126, 234, 0.1);
  cursor: move;
}

.crop-handle {
  position: absolute;
  background: #fff;
  border: 2px solid #667eea;
  border-radius: 50%;
  width: 12px;
  height: 12px;
  z-index: 10;
  touch-action: none;
}

.crop-box {
  touch-action: none;
}
</style>
