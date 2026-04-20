import request from './request'

export const login = (data) => request.post('/auth/login', data, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
})

export const getUserInfo = () => request.get('/auth/me')
