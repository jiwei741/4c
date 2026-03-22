# Streaming Service

## 目标

`services/streaming` 对应成员 C 的 Kafka / Flink / PostGIS 实时管道。

它未来负责：

- 历史影像回放
- Sentinel-2 特征更新事件
- 分割和特征工程任务调度
- 结果落 PostGIS

## 当前边界

输入：

- ingestion 的原始资产事件
- segmentation 的特征更新结果

输出：

- 面向 backend / frontend 的时空状态表
- 给 inference 使用的增量特征事件

## 当前实现阶段

本次先落：

- topic 和 sink 约定
- 服务目录
- 配置模板

真正的 Kafka / Flink 作业后补。
