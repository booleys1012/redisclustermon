import { Component, OnInit, AfterViewInit, Output, EventEmitter, Inject } from '@angular/core';
import { SocketService } from '../shared/services/socket.service';
import { EchartoptionhelperService } from '../shared/services/echartoptionhelper.service';
import { StatisticscacheService } from '../shared/services/statisticscache.service';
import { Message } from '../shared/model/message';
import { ContentType } from '../shared/model/contenttype';
import { StatDef } from '../shared/model/statdef';
import { MatDialog, MatDialogRef, MatList, MatListItem, MatSnackBar, MatSlideToggle, MatButtonToggleModule, 
  MatProgressSpinnerModule, MAT_DIALOG_DATA } from '@angular/material';
import { environment } from '../../../environments/environment';

const HIDE_CHART_TEXT = '[ hide chart ]';
const SERVER_URL = environment.rooturl;
const STATISTICSMAP: { [s: string]: StatDef } = {
  'used_memory':               { 'name': 'used_memory',               'unit': 'bytes' },
  'used_memory_rss':           { 'name': 'used_memory_rss',           'unit': 'bytes' },
  'instantaneous_ops_per_sec': { 'name': 'instantaneous_ops_per_sec', 'unit': 'ops' },
};
const STATISTICS: Array<StatDef> = Object.keys(STATISTICSMAP).map(function(key) { return STATISTICSMAP[key]; });


declare var echarts;

@Component({
  selector: 'rcm-summary',
  templateUrl: './summary.component.html',
  styleUrls: ['./summary.component.css']
})



export class SummaryComponent implements OnInit, AfterViewInit {

  @Output() terminalResponse = new EventEmitter<Message>();
  
  ioConnection: any = undefined;

  summary: any      = undefined;
  summarydata: any  = undefined;
  rcmmasters: any   = {};
  
  statisticsmap     = STATISTICSMAP;
  statisticslist    = STATISTICS ;
  selectedstatistic = STATISTICS[0].name;
  
  chartvisible      = true;
  mychart           = undefined;
  
  
  
  constructor(
    private socketService: SocketService,
    public echartOptionService: EchartoptionhelperService,
    private statcacheService: StatisticscacheService,
    public snackBar: MatSnackBar,
    public dialog: MatDialog
  ) { 
  }

  ngOnInit() {
    this.initIoConnection();
  }

  ngAfterViewInit(): void {
  }
  
  openMasterDialog(node): void {
    let dialogRef = this.dialog.open(MasterSummaryDialogComponent, {
      width: '80%',
      data: {
        title: node,
        summary: this.summary[node]
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed');
    });
  }
  
  private hostvalsummary(item: any) {
    return {
        id:                 item.node['id'],
        link_state:         item.node['link-state'],
        cluster_state:      item.info['cluster_state'],
        cluster_slots_fail: item.info['cluster_slots_fail'],
        cluster_slots_ok:   item.info['cluster_slots_ok'],
        slots:              item.node['slots'],
        flags:              item.node['flags'],
        keys:               item.info.db0.keys,
        slaves:             item['slaves'].map(x => this.hostvalsummary(x))
    }
  }
  
  private summarydatamap(summary: any) {
    const result: any = {};
    for (const item of Object.keys(summary)) {
      result[item] = this.hostvalsummary(summary[item])
    }
    return result;
  }

  private summarydatamapequal(summarydata1, summarydata2) {
    const keys1 = Object.keys(summarydata1);
    const keys2 = Object.keys(summarydata2);

    let equal: boolean = (keys1.sort().join(',') === keys2.sort().join(','));
    if (equal) {
      for (const k of keys1) {
        // compare link-state
        if (summarydata1[k].link_state !== summarydata2[k].link_state) {
          console.log('link state for ' + k + ' has changed');
          equal = false;
          break;
        }
        // compare slots
        if (summarydata1[k].slots.join(',') !== summarydata2[k].slots.join(',')) {
          equal = false;
          break
        }
      }
    }
    return equal;
  }

  private summarychanged(newsummary: any, newmasters: any) {
    let changed = false;
    if (this.summarydata === undefined) {
      changed = true;
    } else {
      // check master list change
      if (newmasters.toString() != this.rcmmasters) {
        changed = true;
      }

      // check link-states
      if (!this.summarydatamapequal(this.summarydata, newsummary)) {
        changed = true;
      }
    }
    return changed;
  }
  
  public onSelectMetricChange(newMetricValue) {
    if (newMetricValue !== HIDE_CHART_TEXT) {
      this.selectedstatistic = newMetricValue;
      this.updateChart(newMetricValue);
    }
  }
  
  private updateChart(statisticname: string): void {
    this.echartOptionService.setDataPoints(
      this.statcacheService.statcache[statisticname].times,
      this.statcacheService.statcache[statisticname].series)
    
    this.echartOptionService.setSelectedMetric(statisticname);
    this.echartOptionService.setYaxisName(this.statisticsmap[this.selectedstatistic].unit);
    this.echartOptionService.setTitle(statisticname);
    this.echartOptionService.refreshTo(this.mychart);
    this.mychart.resize();
  }
  
  
  
  private initCachedCharting(firstsummary: any): void {
    
    this.statcacheService.initCache(
      this.echartOptionService.option._maxentries,
      STATISTICS,
      Object.keys(firstsummary));
    
    // based on prepared DOM, initialize echarts instance
    this.mychart = echarts.init(document.getElementById('echart'));

    
    for (const k of this.statcacheService.seriesnames) {
       this.echartOptionService.addSeries(k, {
          name: k,
          scale: true,
          type: 'line',
//          step: 'start',
          data: []
       });
    }
    this.echartOptionService.hideTitle();
    this.echartOptionService.refreshTo(this.mychart);
  }
  
  private ingestClusterSummary(content: any): void {
    
      const unixtime = new Date(content.unixtime * 1000);
      this.summary   = content.csummary;
    
      if (this.mychart === undefined) {
        this.initCachedCharting(this.summary);
      }
      
      for (const statname of this.statisticslist) {
        let seriesvalues = {};
        for (const seriesname of Object.keys(this.summary)) {
          seriesvalues[seriesname] = null;
          try {
            seriesvalues[seriesname] = this.summary[seriesname].info[statname.name];
          } catch {}
        }
        this.statcacheService.updateAllSeriesInStat(statname.name, unixtime, seriesvalues);
        
      }
      
      if (this.selectedstatistic !== HIDE_CHART_TEXT) {
        this.updateChart(this.selectedstatistic);
      }
    
    
      const newsummarydata = this.summarydatamap(this.summary);
      const masters        = Object.keys(this.summary);

      if (this.summarychanged(newsummarydata, masters)) {
        this.summarydata    = newsummarydata;
        this.rcmmasters     = masters;
      }
  }
  
  private initIoConnection(): void {
    this.socketService.initSocket(SERVER_URL);

    this.ioConnection = this.socketService.onMessage()
      .subscribe((message: Message) => {
        if (message.contenttype === ContentType.CLUSTERSUMMARY) {
          this.ingestClusterSummary(JSON.parse(message.content))
        } else if (message.contenttype === ContentType.TERMINALRESPONSE) {
          this.terminalResponse.emit(message);
        } else if (message.contenttype === ContentType.CLUSTERCOMMANDLIST) {
          // should not happen
          this.terminalResponse.emit(message);
        } else {
          // should not happen
          console.log('should not happen');
        }
        
      });
    
  }


  public openSnackBar(message: string) {
    this.snackBar.open(message, '', {
      duration: 400,
    });
  }
}


@Component({
  selector: 'rcm-dialog-overview-example-dialog',
  templateUrl: 'master-summary-dialog.html',
})
export class MasterSummaryDialogComponent {

  constructor(
    public dialogRef: MatDialogRef<MasterSummaryDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any) { }

  onCloseClick(): void {
    this.dialogRef.close();
  }

}
