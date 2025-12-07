import ky from 'ky'
const api = ky.create({ prefixUrl: '/api' })

export const fetchCity = (city, country='ZA', parameter='pm25', limit=100) =>
  api.get('openaq', { searchParams: { city, country, parameter, limit } }).json()

export const analyzeCity = (city, country='ZA', model='llama3.1:latest') =>
  api.get('analyze', { searchParams: { city, country, model } }).json()

