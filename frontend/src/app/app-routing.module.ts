import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MilestoneGroupComponent } from './milestone-group/milestone-group.component';

const routes: Routes = [
  { path: 'dashboard', component: MilestoneGroupComponent },
  { path: '', redirectTo: '/dashboard', pathMatch: "full" }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
