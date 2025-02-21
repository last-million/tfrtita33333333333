import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add response interceptor for error handling
axiosInstance.interceptors.response.use(
  response => response,
  error => {
    // Convert axios error to simple object
    const simpleError = {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data
    }
    return Promise.reject(simpleError)
  }
)

// Export the API methods
export const api = {
  // Drive API methods
  drive: {
    connect: () => axiosInstance.get('/drive/connect'),
    getStatus: () => axiosInstance.get('/drive/status'),
    listFiles: () => axiosInstance.get('/drive/files')
  },

  // File API methods
  files: {
    upload: (file) => {
      const formData = new FormData()
      formData.append('file', file)
      return axiosInstance.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
    }
  },

  // Supabase API methods
  supabase: {
    listTables: () => axiosInstance.get('/supabase/tables'),
    vectorize: (files, table) => axiosInstance.post('/vectorize', { files, table })
  }
}

export default api
