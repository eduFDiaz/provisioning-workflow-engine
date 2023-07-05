import { TestBed } from '@angular/core/testing';

import { HttpService } from './milestone-http-service.service';

describe('MilestoneServiceService', () => {
  let service: HttpService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(HttpService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
