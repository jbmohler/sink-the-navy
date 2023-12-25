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
    this.http.post('/api/create-game', {}).subscribe((data: any) => {
      this.router.navigate(['/game'], { queryParams: { code: data.code } });
    });
  }

  onConnect() {
    const candidate = this.gameCode!.replaceAll(' ', '');
    this.http.get(`/api/game/${candidate}/probe`).subscribe((data: any) => {
      this.router.navigate(['/game'], { queryParams: { code: data.code } });
    });
  }
}
