# clash-config-lint

导入 Clash Meta 配置之前，在本机检查 YAML。不联网，不修改原文件。

## 安装

```bash
pip install pyyaml
```

把 `clash_lint/` 放在当前目录，或把它的上一级加入 `PYTHONPATH`。

## 用法

```bash
python -m clash_lint config.yaml
```

没有问题时打印 `ok`，退出码 0。有错误时每行一条，退出码 1。

## 检查什么

- 顶层是映射，YAML 能解析
- `mixed-port` 等监听端口在 1–65535
- 有 `proxies` 或 `proxy-providers`
- 每个代理有 `name`、已知 `type`、`server`、合法 `port`
- `name` 不重复
- `rules` 里每一条都是 `TYPE,value,policy`

## 示例

```yaml
mixed-port: 7890
proxies:
  - name: example
    type: ss
    server: example.com
    port: 443
rules:
  - DOMAIN-SUFFIX,example.com,DIRECT
```

## 测试

```bash
python -m unittest tests/test_lint.py
```

## 许可

MIT
