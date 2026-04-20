import request from './request'

export const getMaterials = (params) => request.get('/materials/', { params })
export const uploadMaterial = (formData) => request.post('/materials/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const deleteMaterial = (id) => request.delete(`/materials/${id}`)
