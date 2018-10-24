import { TestBed, inject } from '@angular/core/testing';

import { StatisticscacheService } from './statisticscache.service';

describe('StatisticscacheService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [StatisticscacheService]
    });
  });

  it('should be created', inject([StatisticscacheService], (service: StatisticscacheService) => {
    expect(service).toBeTruthy();
  }));
});
