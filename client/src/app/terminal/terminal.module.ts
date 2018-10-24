import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { MaterialModule } from '../shared/material/material.module';

import { TerminalComponent } from './terminal.component';
import { SocketService } from './shared/services/socket.service';
import { DialogUserComponent } from './dialog-user/dialog-user.component';
import { MapToIterablePipe } from './shared/pipes/map-to-iterable.pipe';
import { SummaryComponent, MasterSummaryDialogComponent } from './summary/summary.component';
import { EchartoptionhelperService } from './shared/services/echartoptionhelper.service';
import { StatisticscacheService } from './shared/services/statisticscache.service';
import { ReversePipe } from './shared/pipes/reverse.pipe';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MaterialModule
  ],
  declarations: [TerminalComponent, DialogUserComponent, MasterSummaryDialogComponent, MapToIterablePipe, SummaryComponent, ReversePipe],
  providers: [SocketService, EchartoptionhelperService, StatisticscacheService],
  entryComponents: [DialogUserComponent, MasterSummaryDialogComponent, SummaryComponent]
})
export class TerminalModule { }
