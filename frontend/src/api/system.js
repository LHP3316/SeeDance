import request from './request'

export const getSessionId = () => request.get('/system/session')
export const updateSessionId = (sessionid) => request.put('/system/session', { sessionid })
export const getUsers = (params) => request.get('/system/users', { params })
export const createUser = (data) => request.post('/system/users', data)
export const deleteUser = (id) => request.delete(`/system/users/${id}`)
export const getSystemLogs = (params) => request.get('/system/logs', { params })
