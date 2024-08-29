import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { User } from '../user';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type': 'application/json',
  }),
};

@Injectable({
  providedIn: 'root',
})
export class LoginService {
  private url = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  // GET users from the server
  loginUser(user: User) {
    return this.http.post<User>(this.url + '/api/login', user, httpOptions);
  }
}
