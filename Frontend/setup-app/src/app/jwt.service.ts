import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { throwError } from 'rxjs';
// import { environment } from '../environments/environment';

import { User } from './user';

@Injectable({
  providedIn: 'root'
})
export class JwtService {

  // URL of the server
  // apiUrl = environment.SOCKET_ENDPOINT;
  // redirectUrl: string;

  constructor(private httpClient: HttpClient, public router: Router) { }

  login(data: any) {
    console.log(data)
    localStorage.setItem('access_token', data['result']['token']);
    localStorage.setItem('user', JSON.stringify(data['result']['user']));
  }

  IsUserAdmin(): boolean {
    var x = localStorage.getItem('user');
    if (x) {
      let user = JSON.parse(x);
      return user.isAdmin; 
    }
    return false;
  }

  // register(userData: User) {
  //   let un = userData.username;
  //   let em = userData.email;
  //   let pw = userData.password;
  //   console.log("jwt.service register email: " + em);
  //   console.log("jwt.service register password: " + pw);
  //   return this.httpClient.post<any>(`${this.apiUrl}/register`, { username: un, email: em, password: pw })
  //     .subscribe((res: any) => {
  //       localStorage.setItem('access_token', res.token);
  //       console.log("post register response: " + res.token);

  //     })
  // }

  handleError(error: HttpErrorResponse) {
    let msg = '';
    if (error.error instanceof ErrorEvent) {
      // client-side error
      msg = error.error.message;
    } else {
      // server-side error
      msg = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    return throwError(msg);
  }


  logout() {
    localStorage.removeItem('access_token');
  }

  public get loggedIn(): boolean {
    return localStorage.getItem('access_token') !== null;
  }

}
