import { NgModule } from '@angular/core';
import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { MilestoneGroupComponent } from './milestone-group/milestone-group.component';
import { HttpClientModule } from '@angular/common/http';
import { ClarityModule } from "@clr/angular";
import { MilestoneComponent } from './milestone/milestone.component';
import { StepTitleDirective } from './step-title.directive';

@NgModule({
  declarations: [
    AppComponent,
    MilestoneComponent,
    MilestoneGroupComponent,
    StepTitleDirective
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserModule,
    BrowserAnimationsModule,
    ClarityModule
   ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
