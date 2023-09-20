#!/usr/bin/env python3
import requests
import json

CLIENT_VERSION="0.1.0"

CLASH_HOST="http://127.0.0.1:9090"

API_LOG="/logs"
API_TRAFFIC="/traffic"
API_VERSION="/version"
API_CONFIGS="/configs"
API_PROXY="/proxies"
API_RULES="/rules"
API_CONNECTIONS="/connections"
API_PROVIDER_PROXY="/providers/proxies"
API_DNS="/dns/query"

def test_api():
    res = requests.get(f"{CLASH_HOST}")
    if res.ok:
        return res.text == '{"hello":"clash"}\n'
    return False

class ClashApi:
    def __init__(self) -> None:
        assert test_api(), "Clash API is not available"

    def get_logs(self):
        res = requests.get(f"{CLASH_HOST}{API_LOG}")
        if res.ok:
            return json.loads(res.text)

    def get_traffic(self):
        res = requests.get(f"{CLASH_HOST}{API_TRAFFIC}")
        if res.ok:
            return json.loads(res.text)
    
    def get_version(self):
        res = requests.get(f"{CLASH_HOST}{API_VERSION}")
        if res.ok:
            return json.loads(res.text)
    
    def get_config(self):
        res = requests.get(f"{CLASH_HOST}{API_CONFIGS}")
        if res.ok:
            return json.loads(res.text)
    
    def reload_config(self, conf_path):
        put_data = {
            "path": conf_path
        }
        put_data = json.dumps(put_data)
        res = requests.put(f"{CLASH_HOST}{API_CONFIGS}",
                           data=put_data)
        return res.ok
    
    def get_proxies(self):
        res = requests.get(f"{CLASH_HOST}{API_PROXY}")
        if res.ok:
            return json.loads(res.text)
    
    def get_proxies_names(self):
        proxies = self.get_proxies()
        return list(proxies['proxies'])

    def get_proxy_with_name(self, name):
        res = requests.get(f"{CLASH_HOST}{API_PROXY}/{name}")
        if res.ok:
            return json.loads(res.text)
    
    def select_proxy(self, selector_name, proxy_name):
        put_data = {
            "name": proxy_name
        }
        put_data = json.dumps(put_data)
        res = requests.put(f"{CLASH_HOST}{API_PROXY}/{selector_name}",
                           data=put_data)
        return res.ok

    def get_proxy_delay(self, name):
        delay_test_data = {
            "timeout": 60_000,
            "url": "https://www.google.com",
        }
        res = requests.get(f"{CLASH_HOST}{API_PROXY}/{name}/delay",
                           data=delay_test_data)
        if res.ok:
            return json.loads(res.text)
    
    def get_proxies_delays(self):
        proxies = self.get_proxies_names()
        delays = list()
        for p in proxies:
            delay = self.get_proxy_delay(p)
            delays.append(delay)
        
        return dict(zip(proxies, delays))
    
    def get_rules(self):
        res = requests.get(f"{CLASH_HOST}{API_RULES}")
        if res.ok:
            return json.loads(res.text)

    def get_connections(self):
        res = requests.get(f"{CLASH_HOST}{API_CONNECTIONS}")
        if res.ok:
            return json.loads(res.text)
    
    def get_providers_proxis(self):
        res = requests.get(f"{CLASH_HOST}{API_PROVIDER_PROXY}")
        if res.ok:
            return json.loads(res.text)
    
    def get_providers_proxies_with_name(self, name):
        res = requests.get(f"{CLASH_HOST}{API_PROVIDER_PROXY}/{name}")
        if res.ok:
            return json.loads(res.text)
    
    def select_provider(self, selector_name, proxy_name):
        put_data = {
            "name": proxy_name
        }
        put_data = json.dumps(put_data)
        res = requests.put(f"{CLASH_HOST}{API_PROVIDER_PROXY}/{selector_name}",
                           data=put_data)
        return res.ok
    
    def get_provider_health(self, name):
        res = requests.get(f"{CLASH_HOST}{API_PROVIDER_PROXY}/{name}/healthcheck")
        if res.ok:
            return json.loads(res.text)

class ClashClient:
    def __init__(self) -> None:
        self.api = ClashApi()
        self.proxies = self.api.get_proxies()['proxies']
        self.cmds = {
            "print": self.cli_print,
            "select": self.cli_select,
            "update": self.cli_update,
            "h": self.cli_print_help,
            "q": exit,
        }
        self.cmd_helps = {
            "print": "Usage: > print selector[s] [selector name]. Print selectors and proxies",
            "select": "Usage: > selector [selector name] [proxy name]. Select proxy for selector",
            "update": "Usage: > update. Update selector and proxy information",
            "h": "Print this help",
            "q": "Quit client",
        }
    
    def __get_selectors_internal(self):
        self.selectors = [self.proxies[k] for k in self.proxies if self.proxies[k]['type'] == 'Selector']

    def __get_selectors(self):
        if not hasattr(self, 'selectors'):
            self.__get_selectors_internal()
        return self.selectors

    def __print_proxy(self, proxy):
        print(f" Proxy: {proxy['name']} (alive: {proxy['alive']})")
        if len(proxy['history']) > 0:
            history = proxy['history'][-1]
            if 'delay' in history and 'meanDelay' in history:
                print(f" - delay: {history['delay']}, mean_delay: {history['meanDelay']}")
    
    def __print_selector(self, selector: dict, *args):
        assert selector['type'] == 'Selector', f"target is not a selector"
        print("-" * 27, "SELECTOR", "-" * 27)
        print(f"Selector: {selector['name']}")
        print(f" - aliveness: {selector['alive']}")
        print(f" - selected_proxy: {selector['now']}")
        print(f"Proxies: ")
        for i, proxy in enumerate(selector['all']):
            if not self.proxies[proxy]['alive']:
                continue
            print(i, ":", end="")
            self.__print_proxy(self.proxies[proxy])
        print("-" * 64)
    
    def print_selector(self, *args):
        if len(args) < 1:
            print("selector name not specified")
            return False

        selector_name = args[0]
        self.__get_selectors()
        
        for s in self.selectors:
            if s['name'] == selector_name:
                self.__print_selector(s)

    def print_selectors(self, *args):
        self.__get_selectors()
        for s in self.selectors:
            print(f"{s['name']}")
    
    def cli_select(self, *args):
        if len(args) < 2:
            print("select [selector] [proxy index]")
            return False
        
        self.__get_selectors()
        selector = args[0]
        proxy_idx = int(args[1])

        proxy = self.proxies[selector]['all'][proxy_idx]
        return self.api.select_proxy(selector, proxy)

    def cli_print(self, *args):
        types_print = {
            "selector": self.print_selector,
            "selectors": self.print_selectors
        }

        if len(args) == 0:
            print("Args for print:")
            print(list(types_print.keys()))
            return False

        if args[0] in types_print:
            types_print[args[0]](*args[1:])
            return True

        return False

    def cli_update(self, *args):
        self.proxies = self.api.get_proxies()['proxies']
        self.__get_selectors_internal()
        return True

    def cli_print_help(self, *args):
        print("Available commands: ")
        print(list(self.cmds.keys()))
        print()
        for c in self.cmd_helps:
            print(f"  {c} \t {self.cmd_helps[c]}")
        return True
    
    def main(self):
        print(f"Clash Version: {self.api.get_version()['version']}")
        print(f"Client Version: {CLIENT_VERSION}")
        self.cli_print_help()
        cmd = "start"
        while(cmd != 'q'):
            cmd = input("> ")
            cmd = cmd.split()
            if cmd[0] not in self.cmds or not self.cmds[cmd[0]](*cmd[1:]):
                print(f"x {cmd} failed")

def main():
    cli = ClashClient()
    cli.main()

if __name__ == "__main__":
    main()
