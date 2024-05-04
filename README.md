# Kafka Clone for Big Data Project

## Getting Started

1. Start the ZooKeeper:
    ```shell
    python zookeeper.py --port <portnumber> --brokers <bpno1-bpno2-bpno3>
    ```

2. Start the Broker:
    ```shell
    python broker.py -p <pno> -i <bid>
    ```

3. Start the Producer:
    ```shell
    python producer.py -z <zookeeperportno> -t <messageid> -i <producerid>
    ```

4. Start the Consumer:
    ```shell
    python consumer.py -z <zookeeperportno> -c <consumer_portnumber> -t <messageid> -i <consumerid>
    ```

