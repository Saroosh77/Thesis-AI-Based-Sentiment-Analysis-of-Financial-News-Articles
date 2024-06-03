import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { User } from '../user';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type':  'application/json',
  })
}

@Injectable({
  providedIn: 'root'
})

export class LoginService {

  private userUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) { }

  // GET users from the server 
  loginUser(user: User) {
    return this.http.post<User>(this.userUrl + "/api/login", user, httpOptions)
  }
}
