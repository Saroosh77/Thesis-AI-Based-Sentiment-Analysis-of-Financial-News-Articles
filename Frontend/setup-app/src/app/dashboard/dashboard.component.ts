import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'
import { Sentiment } from '../sentiment';
import { ArticleService } from './article.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {

  sentiment_results: Sentiment[] = [];

  constructor(private service: ArticleService) {}

  ngOnInit(): void {
    this.service.getArticles().subscribe(data => {
      this.sentiment_results = data;
    });
  }


}
