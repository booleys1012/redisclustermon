import { Injectable } from '@angular/core';
import { StatDef } from '../model/statdef';

@Injectable()
export class StatisticscacheService {
  
  private cachesize: number;
  public  statcache: any = {};
  private statunitmap: { [s: string]: string } = {};
  public  seriesnames: Array<string> = [];
  
  constructor() { }
  
  public initCache(
    size: number,
    statdefs: Array<StatDef>,
    serieslist: Array<string>): void {
    
    this.cachesize = size;
    for (const statdef of statdefs) {
      this.registerStat(statdef);
    }
    for (const seriesname of serieslist) {
      this.registerSeries(seriesname);
    }
    
  }
  
  private registerStat(statdef: StatDef): void {
    if (!(statdef.name in this.statcache)) {
      const self = this;
      this.statcache[statdef.name] = {
        series: {},
        times: new Array(self.cachesize + 1).fill(null),
        push: function(time: Date, seriesdata: { [s: string]: number }): void {
          this.times.push(time);
          for (const cacheseriesname of Object.keys(this.series)) {
            if (cacheseriesname in seriesdata) {
              this.series[cacheseriesname].push(seriesdata[cacheseriesname]);
            } else {
              this.series[cacheseriesname].push(null);
            }
          }
          this.runcleaner();
        },
        runcleaner: function() {
          while (this.times.length > self.cachesize) {
            this.times.shift();
          }
          for (const seriesname of Object.keys(this.series)) {
            while (this.series[seriesname].length > self.cachesize) {
              this.series[seriesname].shift();
            }
          }
        }
      };
    }
    this.statunitmap[statdef.name] = statdef.unit;
  }
  
  private registerSeries(name: string) {
    this.seriesnames.push(name);
    for (const statname of Object.keys(this.statcache)) {
      this.statcache[statname].series[name] = [];
      for (let i = 0; i < this.cachesize; i++) {
        this.statcache[statname].series[name].push(null);
      }
    }
  }
  
  public updateAllSeriesInStat(
    statname: string,
    newtime: Date,
    seriesvalues: { [s:string]: number }
  ): void {
    if (statname in this.statcache) {
      this.statcache[statname].push(newtime, seriesvalues);
    }
  }
  
  
  
  
}
