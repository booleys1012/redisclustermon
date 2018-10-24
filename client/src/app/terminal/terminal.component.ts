import { JsonPipe } from '@angular/common';
import { Component, OnInit, ViewChildren, ViewChild, AfterViewInit, QueryList, ElementRef } from '@angular/core';
import { MatDialog, MatDialogRef, MatList, MatListItem, MatSnackBar, MatSlideToggle, MatTooltipModule } from '@angular/material';
import { ContentType } from './shared/model/contenttype';
import { Message } from './shared/model/message';
import { SocketService } from './shared/services/socket.service';
import { DialogUserComponent } from './dialog-user/dialog-user.component';
import { DialogUserType } from './dialog-user/dialog-user-type';
import { MapToIterablePipe } from './shared/pipes/map-to-iterable.pipe';
import { ReversePipe } from './shared/pipes/reverse.pipe';


const AVATAR_URL = 'https://api.adorable.io/avatars/285';


@Component({
  selector: 'rcm-terminal',
  templateUrl: './terminal.component.html',
  styleUrls: ['./terminal.component.css']
})
export class TerminalComponent implements OnInit, AfterViewInit {
  
  contenttype = ContentType;
  
  reverseCmdIndx = 0;
  messages: Message[] = [];
  messageContent: string;
  
  dynamicCommands      = null;
  dynamicCommandsOrder = null;
  
  dialogRef: MatDialogRef<DialogUserComponent> | null;
  defaultDialogUserParams: any = {
    disableClose: true,
    data: {
      title: 'Lets get started...',
      dialogType: DialogUserType.NEW
    }
  };

  // getting a reference to the overall list, which is the parent container of the list items
  @ViewChild(MatList, { read: ElementRef }) matList: ElementRef;

  // getting a reference to the items/messages within the list
  @ViewChildren(MatListItem, { read: ElementRef }) matListItems: QueryList<MatListItem>;

  constructor(private socketService: SocketService,
    public dialog: MatDialog
  ) { }

  ngOnInit(): void {
    this.initModel();
    // Using timeout due to https://github.com/angular/angular/issues/14748
//    setTimeout(() => {
//      this.openUserPopup(this.defaultDialogUserParams);
//    }, 0);
  }

  ngAfterViewInit(): void {
    // subscribing to any changes in the list of items / messages
    this.matListItems.changes.subscribe(elements => {
      this.scrollToBottom();
    });
  }

  // auto-scroll fix: inspired by this stack overflow post
  // https://stackoverflow.com/questions/35232731/angular2-scroll-to-bottom-terminal-style
  private scrollToBottom(): void {
    try {
      this.matList.nativeElement.scrollTop = this.matList.nativeElement.scrollHeight;
    } catch (err) {
    }
  }

  private initModel(): void {
    const randomId = this.getRandomId();
  }

  
  
  private getRandomId(): number {
    return Math.floor(Math.random() * (1000000)) + 1;
  }

  public onClickUserInfo() {
    this.openUserPopup({
      data: { }
    });
  }

  private openUserPopup(params): void {
    this.dialogRef = this.dialog.open(DialogUserComponent, params);
  }
  public displayRequestHistory(offset) {
    if (offset === -1) {
      for (let mIdx = this.messages.length - 1 - this.reverseCmdIndx; mIdx > -1 ; mIdx += -1 ) {
        if (this.messages[mIdx].contenttype === ContentType.TERMINALREQUEST) {
          this.reverseCmdIndx = this.messages.length - mIdx;
          this.messageContent = this.messages[mIdx].content;
          break;
        }
      }
    } else if (offset === 1) {
      for (let mIdx = this.messages.length - this.reverseCmdIndx + 1; mIdx < this.messages.length ; mIdx += 1 ) {
        if (this.messages[mIdx].contenttype === ContentType.TERMINALREQUEST) {
          this.reverseCmdIndx = this.messages.length - mIdx;
          this.messageContent = this.messages[mIdx].content;
          break;
        }
      }
    }
  }
  
  public sendMessage(message: string): void {
    if (!message) {
      return;
    }

    this.socketService.send({
      contenttype: ContentType.TERMINALREQUEST,
      content: message
    });
    this.messages.push({
      contenttype: ContentType.TERMINALREQUEST,
      content: message
    });
    this.messageContent = null;
    this.reverseCmdIndx = 0;
  }

  
  loadCmdtemplate(cmdname: string): void {
    if (cmdname in this.dynamicCommands) {
      this.messageContent = this.dynamicCommands[cmdname].example;
      
      
    }
  }
  
  onTerminalResponse(event: Message) {
    if (event.contenttype === ContentType.TERMINALRESPONSE) {
      this.messages.push(event);
      this.scrollToBottom()
    } else if (event.contenttype === ContentType.CLUSTERCOMMANDLIST) {
      this.dynamicCommands = event.content;
      let readCommands = [];
      let writeCommands = [];
      
      for (const cmdname of Object.keys(this.dynamicCommands)) {
        if (this.dynamicCommands[cmdname].read_or_write == 'write') {
          writeCommands.push(cmdname);
        } else {
          readCommands.push(cmdname);
        }
      }
      readCommands.sort();
      writeCommands.sort();
      this.dynamicCommandsOrder = readCommands.concat(writeCommands);
      
    } else {
      //ignored
    }
  }
}

