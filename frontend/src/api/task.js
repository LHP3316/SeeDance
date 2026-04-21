import request from './request'

export const getTasks = (params) => request.get('/tasks/', { params })
export const createTask = (data) => request.post('/tasks/', data)
export const updateTask = (id, data) => request.put(`/tasks/${id}`, data)
export const deleteTask = (id) => request.delete(`/tasks/${id}`)
export const runTask = (id) => request.post(`/tasks/${id}/run`)
