import { Injectable } from '@angular/core';

@Injectable()
export class EchartoptionhelperService {
  
  option =  {
    _selectedmetric: '',
    _serieskeyorder: [],
    _maxentries: 100,
    _trim : function() {
//      if (this.xAxis.data.length > this._maxentries) {
//        this.xAxis.data.shift();
//      }
      for (let i = 0; i < this.series.length; i++) {
        if (this.series[i].data.length > this._maxentries) {
          this.series[i].data.shift();
        }
      }
    },
    title: {
      x: 'center',
      text: 'loading...'
    },
    tooltip: {
        trigger: 'item',
        axisPointer: {
            type: 'cross',
            label: {
                backgroundColor: '#283b56'
            }
        }
    },
    legend: {
        show: true,
        type: 'scroll',
        orient: 'vertical',
        right: 10,
        top: 20,
        bottom: 20,
    },
    xAxis: {
        type: 'time',
        boundaryGap: true
      },
    yAxis: {
        name: 'hello',
        type: 'value',
        scale: true,
        splitNumber: 2,
        nameRotate: 90,
        boundaryGap: ['20%', '20%']
    },
    series: []
  };
  public hideTitle(): void {
    this.option.title['show'] = false;
  }
  public setTitle(title: string): void {
    this.option.title.text = title
  }
  public setSelectedMetric(metricname: string): void{
    this.option._selectedmetric = metricname;
  }
  
  public setYaxisName(label: string): void {
    this.option.yAxis.name = label;
  }

  public addSeries(serieskey: string, seriesopts: any): void {
    this.option._serieskeyorder.push(serieskey);
    this.option.series.push(seriesopts);
  }
  
  public setDataPoints(xData, seriesdatamap) {
    //this.option.xAxis.data = xData;
    for (const series of Object.keys(seriesdatamap)) {
      const seriesindex = this.option._serieskeyorder.indexOf(series);
      if (seriesindex !== -1) {
        this.option.series[seriesindex].data = seriesdatamap[series].map(function(val, index) { return [ xData[index], val ]; });
      }
    }
    this.option._trim();
  }
  
  public addDataPoint(newX: Date | number, series_data: any): any {
    //this.option.xAxis.data.push(newX);
    
    for (const seriesname of Object.keys(series_data)) {
      const seriesindex = this.option._serieskeyorder.indexOf(seriesname);
      if (seriesindex !== -1) {
        this.option.series[seriesindex].data.push(series_data[seriesname]);
      }
    }
    this.option._trim()
  }
  
  public refreshTo(chart: any): any {
    chart.setOption(this.option)
  }
  

}
