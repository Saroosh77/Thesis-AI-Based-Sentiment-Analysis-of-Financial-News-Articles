import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Article, Sentiment } from '../sentiment';

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

  getGoogleResults(): Observable<Sentiment[]> {
    return this.http.get<Sentiment[]>(this.url + '/api/google/results');
  }

  getGoogleArticles(): Observable<Article[]> {
    return this.http.get<Article[]>(this.url + '/api/google/articles');
  }
  
  getOnvistaArticles(): Observable<Article[]> {
    return this.http.get<Article[]>(this.url + '/api/onvista/articles');
  }

  getOnvistaResults(): Observable<Sentiment[]> {
    return this.http.get<Sentiment[]>(this.url + '/api/onvista/results');
  }

}
