import { Directive, ElementRef } from '@angular/core';

@Directive({
  selector: '[stepTitlessss]'
})
export class StepTitleDirective {

  constructor(private el: ElementRef) {
    const element = this.el.nativeElement;
    const height = element.getBoundingClientRect().height;
    const width = element.getBoundingClientRect().width;
    element.style.transform = `translate(-${width/2 + 120}px, -${height+30}px)`;
    element.style.textAlign = 'center';
    console.log("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
  }

}
