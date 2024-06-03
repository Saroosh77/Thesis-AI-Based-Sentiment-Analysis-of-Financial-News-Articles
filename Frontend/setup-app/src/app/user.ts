export interface User {
  id?: number;
  email: string | null | undefined;
  password: string| null | undefined;
}

export interface CreateUser {
  name: string;
  email: string;
  password: string;
}
