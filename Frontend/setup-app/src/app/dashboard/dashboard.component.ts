import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Article, Sentiment } from '../sentiment';
import { ArticleService } from './article.service';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatTableModule],
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
  displayedResults = [
    'id',
    'company',
    'published_date',
    'article_title',
    'article_url',
    'sentiment',
  ];
  displayedColumns = ['id', 'company', 'published_date', 'article_url'];

  constructor(private service: ArticleService) {}

  ngOnInit(): void {
    this.getGoogleArticles();
    this.getGoogleResults();
    this.getOnvistaArticles();
    this.getOnvistaResults();
  }

  resetDivs(): void {
    this.display1 = this.display2 = this.display3 = this.display4 = false;
  }

  showGoogleArticles(): void {
    this.display4 = true;
    this.display1 = this.display2 = this.display3 = false;
  }

  getGoogleArticles(): void {
    this.service.getGoogleArticles().subscribe((data) => {
      this.google_articles = data;
    });
  }

  showGoogleResults(): void {
    this.display1 = true;
    this.display2 = this.display3 = this.display4 = false;
  }

  getGoogleResults(): void {
    this.service.getGoogleResults().subscribe((data) => {
      this.google_sentiment_results = data;
    });
  }

  showOnvistaResults(): void {
    this.display2 = true;
    this.display1 = this.display3 = this.display4 = false;
  }

  getOnvistaResults(): void {
    this.service.getOnvistaResults().subscribe((data) => {
      this.onvista_sentiment_results = data;
    });
  }

  showOnvistaArticles(): void {
    this.display3 = true;
    this.display1 = this.display2 = this.display4 = false;
  }

  getOnvistaArticles(): void {
    this.service.getOnvistaArticles().subscribe((data) => {
      this.onvista_articles = data;
    });
  }
}
