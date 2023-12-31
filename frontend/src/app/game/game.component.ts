import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, take } from 'rxjs';

function convertUint8_to_hexStr(uint8: Uint8Array) {
  return Array.from(uint8)
    .map((i) => i.toString(16).padStart(2, '0'))
    .join('');
}

function getClientId() {
  let arr = new Uint8Array(8);
  window.crypto.getRandomValues(arr);
  return convertUint8_to_hexStr(arr);
}

@Component({
  selector: 'app-game',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './game.component.html',
  styleUrl: './game.component.css',
})
export class GameComponent implements OnInit {
  private http = inject(HttpClient);
  private activated = inject(ActivatedRoute);
  private cdr = inject(ChangeDetectorRef);

  code?: string;

  columns = 'A B C D E F G H I J K L M N'.split(' ');
  rows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14];

  values: { [key: string]: number | undefined } = {};

  currentTurn = 1;
  currentMode: 'turn' | 'hilite' = 'turn';

  highlights: string[] = [];
  turnmarksDelimited: string = '';
  turnmarks: number[] = [];

  clientId = getClientId();

  ngOnInit() {
    this.activated.queryParams.subscribe((params: any) => {
      this.code = params.code;
      console.log(params);

      this.createEventSource().subscribe((data) => {
        // console.log(data);

        if (data.source !== this.clientId && data.shot) {
          for (const keyStr in data.shot) {
            const update = data.shot[keyStr];
            const cvalue = update === null ? undefined : update;
            this.values[keyStr] = cvalue;
            if (cvalue && this.currentTurn !== cvalue) {
              this.currentTurn = cvalue;
            }
          }
          this.cdr.detectChanges();
        }

        if (data.source !== this.clientId && data.highlights) {
          this.highlights = data.highlights;
          this.cdr.detectChanges();
        }

        if (data.source !== this.clientId && data.turnmarks) {
          this.turnmarksDelimited = data.turnmarks
            .map((r: any) => r.toString())
            .join(' ');
          this.turnmarks = data.turnmarks;
          this.cdr.detectChanges();
        }

        if (data.source === 'root' && data.board) {
          for (const keyStr in data.board) {
            this.values[keyStr] = data.board[keyStr];
          }
          this.cdr.detectChanges();
        }
      });
    });
  }

  value(iCol: string, iRow: number) {
    const keyStr = `${iCol}:${iRow}`;
    return this.values[keyStr];
  }

  putGameData(tail: string, data: any) {
    return this.http
      .put(`/api/game/${this.code}/${tail}`, data, {
        headers: { 'Content-Type': 'application/json' },
      })
      .pipe(take(1));
  }

  setCellValue(keyStr: string, value: number | undefined) {
    const data = {
      source: this.clientId,
      shot: { [keyStr]: value ?? null },
    };
    this.putGameData('cell-shot', data).subscribe((d) => {
      this.values[keyStr] = value;
    });
  }

  onClickOpenWater(iCol: string, iRow: number) {
    const keyStr = `${iCol}:${iRow}`;
    // console.log(iCol, iRow, this.values[keyStr] );

    if (this.currentMode === 'turn') {
      if (this.values[keyStr] === undefined) {
        this.setCellValue(keyStr, this.currentTurn);
      } else if (this.values[keyStr] === this.currentTurn) {
        this.setCellValue(keyStr, undefined);
      } else {
        alert('already occupied');
        //this.values[keyStr] = this.currentTurn;
      }
    }

    if (this.currentMode === 'hilite') {
      this.highlights.push(keyStr);

      const data = { source: this.clientId, highlights: this.highlights };
      this.putGameData('cell-highlight', data).subscribe((data) => {
        setTimeout(() => {
          this.highlights = [];
          const data = { source: this.clientId, highlights: this.highlights };
          this.putGameData('cell-highlight', data).subscribe();
        }, 10000);
      });
    }
  }

  onCompleteTurn() {
    this.currentTurn += 1;
  }

  onHighlight() {
    this.currentMode = this.currentMode === 'turn' ? 'hilite' : 'turn';
  }

  onEnteredTMD() {
    const turnmarks = this.turnmarksDelimited.split(' ').map(parseFloat);
    const data = { source: this.clientId, turnmarks: turnmarks };
    this.putGameData('turn-highlight', data).subscribe((data) => {
      this.turnmarks = turnmarks;
    });
  }

  createEventSource(): Observable<any> {
    const eventSource = new EventSource(`/api/game/${this.code}/cell-events`);

    return new Observable((observer) => {
      eventSource.onmessage = (event) => {
        const messageData = JSON.parse(event.data);
        observer.next(messageData);
      };
    });
  }
}
