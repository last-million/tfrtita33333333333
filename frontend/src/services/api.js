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
  },

  // Call API methods (Added)
  calls: {
    initiateSingle: (toNumber, fromNumber) => axiosInstance.post('/calls/initiate', { to_number: toNumber, from_number: fromNumber }),
    initiateBulk: (phoneNumbers) => axiosInstance.post('/calls/bulk', { phone_numbers: phoneNumbers }),
    getHistory: (page = 1, limit = 50, status = null, direction = null) => {
      const params = { page, limit };
      if (status) params.status = status;
      if (direction) params.direction = direction;
      return axiosInstance.get('/calls/history', { params });
    }
    // Add other call-related API calls here if needed
  }
}

// Export named functions for easier import in components
export const initiateSingleCall = api.calls.initiateSingle;
export const initiateBulkCall = api.calls.initiateBulk;
export const getCallHistory = api.calls.getHistory;
// Add other exports as needed

export default api; // Keep default export if other parts rely on it
