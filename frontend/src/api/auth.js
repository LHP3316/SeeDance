import request from './request'

export const login = (data) => {
  const form = new URLSearchParams()
  form.append('username', data.username || '')
  form.append('password', data.password || '')
  return request.post('/auth/login', form, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
})
}

export const getUserInfo = () => request.get('/auth/me')
