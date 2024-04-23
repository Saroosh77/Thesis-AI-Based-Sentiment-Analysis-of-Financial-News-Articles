export interface User {
    id: string
    name: string
    email: string
    password: string
    salt: string
    created_at: Date
    updated_at: Date
  }

  export interface CreateUser {
    name: string
    email: string
    password: string
  }
  