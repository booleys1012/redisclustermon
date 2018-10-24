import { browser, by, element } from 'protractor';

export class RedisClusterMonitorClientPage {
  navigateTo() {
    return browser.get('/');
  }

  getParagraphText() {
    return element(by.css('rcm-root h1')).getText();
  }
}
