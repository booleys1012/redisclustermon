import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { 
  MatButtonModule, 
  MatCardModule,
  MatDialog,
  MatDialogModule,
  MatIconModule, 
  MatFormFieldModule,
  MatInputModule, 
  MatListModule,
  MatSidenavModule, 
  MatToolbarModule, 
  MatExpansionModule,
  MatGridListModule,
  MatChipsModule,
  MatSnackBarModule,
  MatSlideToggleModule,
  MatButtonToggleModule,
  MatProgressSpinnerModule,
  MatTooltipModule,
} from '@angular/material';

@NgModule({
  imports: [
    CommonModule,
    MatButtonModule, 
    MatCardModule,
    MatDialogModule,
    MatIconModule, 
    MatFormFieldModule,
    MatInputModule, 
    MatListModule,
    MatSidenavModule, 
    MatToolbarModule, 
    MatExpansionModule,
    MatGridListModule,
    MatChipsModule,
    MatSnackBarModule,
    MatSlideToggleModule,
    MatButtonToggleModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  exports: [
    MatButtonModule, 
    MatCardModule,
    MatDialogModule,
    MatIconModule, 
    MatFormFieldModule,
    MatInputModule, 
    MatListModule,
    MatSidenavModule, 
    MatToolbarModule, 
    MatExpansionModule,
    MatGridListModule,
    MatChipsModule,
    MatSnackBarModule,
    MatSlideToggleModule,
    MatButtonToggleModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  declarations: [],
  providers: [
    MatDialog
  ]
})
export class MaterialModule { }
