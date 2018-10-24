import { TestBed, inject } from '@angular/core/testing';

import { EchartoptionhelperService } from './echartoptionhelper.service';

describe('EchartoptionhelperService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [EchartoptionhelperService]
    });
  });

  it('should be created', inject([EchartoptionhelperService], (service: EchartoptionhelperService) => {
    expect(service).toBeTruthy();
  }));
});
