import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { LoginService } from './login.service';
import { JwtService } from '../jwt.service';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, MatFormFieldModule, MatCardModule, ReactiveFormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {

  loginForm!: FormGroup;  // Declare a form group
  message!: string;
  
  constructor(private router: Router, private service: LoginService , private formBuilder: FormBuilder, private snackbar: MatSnackBar) { 
    // Initialize the form group with form controls
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]], // Email field with required and email validators
      password: ['', Validators.required], // Password field with required validators
    });
  }

  login(): void {
    this.service.loginUser(this.loginForm.value).subscribe({
      next: response => {
        // this.jwtservice.login(res);
        console.log(response)
        this.message = "Login Successful!";
        this.openSnackBar(this.message);
        this.router.navigateByUrl('/dashboard');
      },
      error: error => {
        this.message = "Invalid login!";
        this.openSnackBar(this.message);
      }
    })
  }

  openSnackBar(message: string) {
    this.snackbar.open(message, 'Undo', {
      duration: 3000
    });
  }
}
