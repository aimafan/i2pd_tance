1. routerinfo结点的主动探测发现

2. routerinfo结点的本地数据库存储

3. leasesets结点的主动探测发现

4. leasesets结点的本地数据库存储

5. 在i2pd代码外面套一层，实现配置开启多个i2p结点实例

写一个kafka生产者，首先将数据放到kafka中，然后由客户端的消费者，将数据放入mysql


[*]写一个定期删Lease的脚本
[*]完善日志
[*]加上首次发现时间
[*]写一个说明文档