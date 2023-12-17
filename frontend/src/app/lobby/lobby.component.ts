import { Component, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-lobby',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './lobby.component.html',
  styleUrl: './lobby.component.css',
})
export class LobbyComponent {
  private router = inject(Router);
  private http = inject(HttpClient);

  gameCode?: string;

  onNewGame() {
    this.router.navigate(['/game']);
  }

  onConnect() {
    const params = new HttpParams().set('code', this.gameCode!);
    this.http.get('/api/probe-game', { params: params }).subscribe((data) => {
      console.log(data);
      this.router.navigate(['/game'], { queryParams: { code: this.gameCode } });
    });
  }
}
