import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Sentiment } from '../sentiment';

const httpOptions = {
  headers: new HttpHeaders({
    'Content-Type':  'application/json',
  })
}

@Injectable({
  providedIn: 'root'
})
export class ArticleService {

  private url = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) { }

  getArticles(): Observable<Sentiment[]> {
    return this.http.get<Sentiment[]>(this.url + '/api/sentiment');
  }

}
