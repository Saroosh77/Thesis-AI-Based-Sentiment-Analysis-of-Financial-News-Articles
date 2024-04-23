import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { LoginService } from './login.service';
import { JwtService } from '../jwt.service';
import { Router } from '@angular/router';
import { FormControl, FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
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

  constructor(private router: Router, private snackbar: MatSnackBar) { 
    
  }

  // loginForm!: FormGroup;
  message!: string;

  // get formControls() { return this.loginForm.controls; }

  // ngOnInit(): void {
  //   this.initializeForm()
  //   if(localStorage.getItem('access_token') !== null) {
  //     this.router.navigate(['/user'], { state: { token: localStorage.getItem('access_token') } });
  //   }
  // }

  // initializeForm(): void {
  //   this.loginForm = this.formBuilder.group({
  //     email: new FormControl('', Validators.required),
  //     password: new FormControl('', Validators.required)
  //   });
  // }

  login(): void {
    // this.service.loginUser(this.loginForm.value).subscribe({
    //   next: res => {
    //     this.jwtservice.login(res);
    //     this.message = "Login Successful!";
    //     this.openSnackBar(this.message);
    //     this.router.navigateByUrl('/user');
    //   },
    //   error: error => {
    //     this.message = "Invalid login!";
    //     this.openSnackBar(this.message);
    //   }
    // })
    this.router.navigate(['/dashboard']);
    this.message = "Login Successful";
    this.openSnackBar(this.message);
  }

  openSnackBar(message: string) {
    this.snackbar.open(message);
  }
}
