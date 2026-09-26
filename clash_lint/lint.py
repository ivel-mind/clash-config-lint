"""Lint a Clash Meta YAML before import. Local only, no network."""
from __future__ import annotations

from dataclasses import dataclass

import yaml

PROXY_TYPES = {
    "ss",
    "ssr",
    "vmess",
    "vless",
    "trojan",
    "hysteria",
    "hysteria2",
    "tuic",
    "wireguard",
    "socks",
    "socks5",
    "http",
    "anytls",
}
PORT_KEYS = ("port", "socks-port", "mixed-port", "redir-port", "tproxy-port")


@dataclass(frozen=True)
class Finding:
    level: str
    path: str
    message: str

    def format(self) -> str:
        where = self.path or "<root>"
        return f"{self.level}: {where}: {self.message}"


def lint_text(text: str) -> list[Finding]:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return [Finding("error", "", f"YAML 无法解析: {exc}")]
    if data is None:
        return [Finding("error", "", "文件是空的")]
    if not isinstance(data, dict):
        return [Finding("error", "", "顶层必须是映射")]
    out: list[Finding] = []
    out.extend(_lint_ports(data))
    proxies = data.get("proxies")
    providers = data.get("proxy-providers")
    if proxies is None and not providers:
        out.append(Finding("error", "", "没有 proxies，也没有 proxy-providers"))
    if proxies is not None:
        out.extend(_lint_proxies(proxies))
    rules = data.get("rules")
    if rules is not None:
        out.extend(_lint_rules(rules))
    return out


def _lint_ports(data: dict) -> list[Finding]:
    out: list[Finding] = []
    for key in PORT_KEYS:
        if key not in data:
            continue
        if not _valid_port(data[key]):
            out.append(Finding("error", key, "端口要在 1 到 65535"))
    return out


def _lint_proxies(proxies: object) -> list[Finding]:
    if not isinstance(proxies, list):
        return [Finding("error", "proxies", "必须是列表")]
    out: list[Finding] = []
    seen: dict[str, int] = {}
    for i, item in enumerate(proxies):
        path = f"proxies[{i}]"
        if not isinstance(item, dict):
            out.append(Finding("error", path, "每一项必须是映射"))
            continue
        name = str(item.get("name") or "").strip()
        if not name:
            out.append(Finding("error", path, "缺少 name"))
        else:
            if name in seen:
                out.append(Finding("error", path, f"name 与 proxies[{seen[name]}] 重复"))
            seen[name] = i
        kind = str(item.get("type") or "").strip()
        if kind not in PROXY_TYPES:
            out.append(Finding("error", f"{path}.type", "不是已知的代理类型"))
        server = str(item.get("server") or "").strip()
        if not server:
            out.append(Finding("error", f"{path}.server", "缺少 server"))
        if not _valid_port(item.get("port")):
            out.append(Finding("error", f"{path}.port", "端口要在 1 到 65535"))
    return out


def _lint_rules(rules: object) -> list[Finding]:
    if not isinstance(rules, list):
        return [Finding("error", "rules", "必须是列表")]
    out: list[Finding] = []
    for i, rule in enumerate(rules):
        if not isinstance(rule, str) or "," not in rule:
            out.append(Finding("error", f"rules[{i}]", "要写成 TYPE,value,policy"))
    return out


def _valid_port(value: object) -> bool:
    if isinstance(value, bool) or not isinstance(value, int):
        return False
    return 1 <= value <= 65535
