import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Article, Sentiment } from '../sentiment';
import { ArticleService } from './article.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css',
})
export class DashboardComponent implements OnInit {
  
  onvista_sentiment_results: Sentiment[] = [];
  google_sentiment_results: Sentiment[] = [];
  onvista_articles: Article[] = [];
  google_articles: Article[] = [];
  display1: boolean = false;
  display2: boolean = false;
  display3: boolean = false;  
  display4: boolean = false;  

  constructor(private service: ArticleService) {}

  ngOnInit(): void {}

  resetDivs(): void {
    this.display1 = this.display2 = this.display3 = this.display4 = false;
  }

  getGoogleResults(): void {
    this.display1 = true;
    this.display2 = this.display3 = this.display4 = false;
    this.service.getGoogleResults().subscribe((data) => {
      this.google_sentiment_results = data;
    });
  }

  getOnvistaResults(): void {
    this.display2 = true;
    this.display1 = this.display3 = this.display4 = false;
    this.service.getOnvistaResults().subscribe((data) => {
      this.onvista_sentiment_results = data;
    });
  }

  getOnvistaArticles(): void {
    this.display3 = true;
    this.display1 = this.display2 = this.display4 = false;
    this.service.getOnvistaArticles().subscribe((data) => {
      this.onvista_articles = data;
    });
  }

  getGoogleArticles(): void {
    this.display4 = true;
    this.display1 = this.display2 = this.display3 = false;
    this.service.getGoogleArticles().subscribe((data) => {
      this.google_articles = data;
    });
  }

}
