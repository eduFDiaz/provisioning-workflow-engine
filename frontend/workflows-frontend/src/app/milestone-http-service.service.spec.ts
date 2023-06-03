import { TestBed } from '@angular/core/testing';

import { MilestoneHttpService } from './milestone-http-service.service';

describe('MilestoneServiceService', () => {
  let service: MilestoneHttpService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MilestoneHttpService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
