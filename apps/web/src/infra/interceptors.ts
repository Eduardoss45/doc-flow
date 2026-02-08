import { api } from './api';

api.interceptors.request.use(
  res => res,
  err => {
    return Promise.reject(err);
  }
);
