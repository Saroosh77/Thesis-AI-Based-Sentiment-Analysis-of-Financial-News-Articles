export interface Sentiment {
  id: number;
  company: string;
  published_date: Date;
  article_title: string;
  article_url: string;
  sentiment: string;
}

export interface Article {
    id: number;
    company: string;
    published_date: Date;
    article_title?: string;
    article_url: string;
}
