import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MilestoneGroupComponent } from './milestone-group.component';

describe('DashboardComponent', () => {
  let component: MilestoneGroupComponent;
  let fixture: ComponentFixture<MilestoneGroupComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MilestoneGroupComponent]
    });
    fixture = TestBed.createComponent(MilestoneGroupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
