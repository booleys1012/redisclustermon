import { RedisClusterMonitorClientPage } from './app.po';

describe('redis-cluster-monitor App', () => {
  let page: RedisClusterMonitorClientPage;

  beforeEach(() => {
    page = new RedisClusterMonitorClientPage();
  });

  it('should display welcome message', () => {
    page.navigateTo();
    expect(page.getParagraphText()).toEqual('Welcome to rcm');
  });
});
