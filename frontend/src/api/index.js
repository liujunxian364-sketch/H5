// uni-app 网络请求封装
// 开发环境使用代理，生产环境需要配置完整URL
// #ifdef H5
const baseURL = '/api'
// #endif
// #ifndef H5
const baseURL = 'http://localhost:8000/api'
// #endif

const request = (options) => {
  return new Promise((resolve, reject) => {
    uni.request({
      url: baseURL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': options.contentType || 'application/json',
        ...options.headers
      },
      timeout: 10000,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          console.error('请求失败:', res)
          reject(new Error(`请求失败: ${res.statusCode}`))
        }
      },
      fail: (err) => {
        console.error('请求错误:', err)
        reject(err)
      }
    })
  })
}

// 上传文件
const uploadFile = (options) => {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: baseURL + options.url,
      filePath: options.filePath,
      name: options.name || 'file',
      formData: options.formData || {},
      success: (res) => {
        try {
          const data = JSON.parse(res.data)
          resolve(data)
        } catch (e) {
          console.error('解析上传响应失败:', e, res.data)
          resolve(res.data)
        }
      },
      fail: (err) => {
        console.error('上传失败:', err)
        reject(err)
      }
    })
  })
}

// 资讯相关API
export const newsApi = {
  getList: (params) => {
    const query = new URLSearchParams(params).toString()
    return request({ url: `/news?${query}` })
  },
  getDetail: (id) => request({ url: `/news/${id}` })
}

// 错题记忆API
export const errorMemoryApi = {
  getSubjects: () => request({ url: '/error-memory/subjects' }),
  getList: (params) => {
    const query = new URLSearchParams(params).toString()
    return request({ url: `/error-memory?${query}` })
  },
  getDetail: (id) => request({ url: `/error-memory/${id}` }),
  upload: (filePath, subject, cropData) => {
    const formData = { subject }
    if (cropData) {
      formData.crop_data = JSON.stringify(cropData)
    }
    return uploadFile({
      url: '/error-memory/upload',
      filePath: filePath,
      name: 'file',
      formData: formData
    })
  },
  delete: (id) => request({ url: `/error-memory/${id}`, method: 'DELETE' }),
  getReport: (subject) => request({ url: `/error-memory/report/${encodeURIComponent(subject)}` })
}

// 单词速记API
export const wordMemoryApi = {
  getList: (params) => {
    const query = new URLSearchParams(params).toString()
    return request({ url: `/word-memory?${query}` })
  },
  getDetail: (id) => request({ url: `/word-memory/${id}` })
}

// 考点答疑API
export const examQAApi = {
  getList: (params) => {
    const query = new URLSearchParams(params).toString()
    return request({ url: `/exam-qa?${query}` })
  },
  getDetail: (id) => request({ url: `/exam-qa/${id}` })
}

// 学商速测API
export const iqTestApi = {
  getQuestions: () => request({ url: '/iq-test/questions' }),
  submitAnswer: (data) => request({ url: '/iq-test/submit', method: 'POST', data })
}

// 考点答疑 - 对话管理API
export const conversationApi = {
  // 获取对话列表
  getList: () => request({ url: '/exam-qa/conversations' }),
  
  // 创建新对话
  create: (data) => request({ url: '/exam-qa/conversations', method: 'POST', data }),
  
  // 获取对话详情
  getDetail: (id) => request({ url: `/exam-qa/conversations/${id}` }),
  
  // 删除对话
  delete: (id) => request({ url: `/exam-qa/conversations/${id}`, method: 'DELETE' }),
  
  // 获取对话消息列表
  getMessages: (conversationId, limit) => {
    let url = `/exam-qa/conversations/${conversationId}/messages`
    if (limit) {
      url += `?limit=${limit}`
    }
    return request({ url })
  },
  
  // 上传图片
  uploadImage: (filePath) => {
    return uploadFile({
      url: '/exam-qa/upload',
      filePath: filePath,
      name: 'file'
    })
  }
}

export default request
