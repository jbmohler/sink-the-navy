import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-game',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './game.component.html',
  styleUrl: './game.component.css',
})
export class GameComponent {
  columns = 'A B C D E F G H I J K L M N'.split(' ');
  rows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14];

  values: { [key: string]: number | undefined } = {};

  currentTurn = 1;
  currentMode: 'turn' | 'hilite' = 'turn';

  highlights: string[] = [];

  value(iCol: string, iRow: number) {
    const keyStr = `${iCol}:${iRow}`;
    return this.values[keyStr];
  }

  onClickOpenWater(iCol: string, iRow: number) {
    const keyStr = `${iCol}:${iRow}`;
    // console.log(iCol, iRow, this.values[keyStr] );

    if (this.currentMode === 'turn') {
      if (this.values[keyStr] === undefined) {
        this.values[keyStr] = this.currentTurn;
      } else if (this.values[keyStr] === this.currentTurn) {
        this.values[keyStr] = undefined;
      } else {
        alert('already occupied');
        //this.values[keyStr] = this.currentTurn;
      }
    }

    if (this.currentMode === 'hilite') {
      this.highlights = [keyStr];
      console.log(this.highlights);

      setTimeout(() => {
        this.highlights = [];
      }, 4000);
    }
  }

  onCompleteTurn() {
    this.currentTurn += 1;
  }

  onHighlight() {
    this.currentMode = this.currentMode === 'turn' ? 'hilite' : 'turn';
  }
}
