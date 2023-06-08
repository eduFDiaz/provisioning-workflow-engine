import { TestBed } from '@angular/core/testing';

import { MilestoneWsService } from './milestone-ws-service.service';

describe('MilestoneWsServiceService', () => {
  let service: MilestoneWsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MilestoneWsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
