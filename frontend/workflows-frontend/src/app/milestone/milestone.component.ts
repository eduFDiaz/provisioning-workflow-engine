import { AfterViewInit, ChangeDetectorRef, Component, ElementRef, EventEmitter, Input, OnInit, Output, QueryList, ViewChildren } from '@angular/core';
import { Workflow } from '../Models/Workflow';

@Component({
  selector: 'app-milestone',
  templateUrl: './milestone.component.html',
  styleUrls: ['./milestone.component.scss']
})
export class MilestoneComponent implements OnInit, AfterViewInit {
  @Input() workflow?: Workflow;
  @ViewChildren('stepTitle') stepTitles: QueryList<ElementRef> | undefined;
  @Output() retryFlowEvent = new EventEmitter<string>();

  constructor(private cd: ChangeDetectorRef) { }
  ngOnInit() { 
    // console.log(this.workflow);
  }

  ngAfterViewInit(): void {
    this.applyTransformations();
    
    this.stepTitles?.changes.subscribe(() => {
      this.applyTransformations();
    });
  }
  
  private applyTransformations(): void {
    this.stepTitles?.forEach((titleElement) => {
      const element = titleElement.nativeElement;
      const height = element.getBoundingClientRect().height;
      const width = element.getBoundingClientRect().width;
  
      element.style.transform = `translate(-${width / 2 + 30}px, -${height+10}px)`;
      element.style.textAlign = 'center';
    });
  
    // Manually triggering change detection
    this.cd.detectChanges();
  }

  retryFlow() {
    this.retryFlowEvent.emit('retry flow from child');
  }
  
}
