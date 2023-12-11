import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-game',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './game.component.html',
  styleUrl: './game.component.css',
})
export class GameComponent {
  columns = 'A B C D E F G H I J K L M N'.split(' ');
  rows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14];

  values: { [key: string]: number | undefined } = {};

  value(iCol: string, iRow: number) {
    const keyStr = `${iCol}:${iRow}`;
    return this.values[keyStr];
  }

  onClickOpenWater(iCol: string, iRow: number) {
    const keyStr = `${iCol}:${iRow}`;
    this.values[keyStr] = 1;
    console.log(iCol, iRow);
  }
}
