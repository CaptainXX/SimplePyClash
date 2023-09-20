# SimplePyClash

A simple python3 interface for [clash](https://github.com/Dreamacro/clash)

## Usage

- Run Clash

```sh
# Check if clash is running
$ ps aux | grep clash
root       61252  5.3  0.1 1238072 20312 ?       Ssl  11:08   0:01 /usr/bin/clash -d /etc/clash
```

- Run script `client.py`

```sh
$ python client.py 
Clash Version: v1.18.0
Client Version: 0.1.0
Available commands: 
['print', 'select', 'update', 'h', 'q']

  print          Usage: > print selector[s] [selector name]. Print selectors and proxies
  select         Usage: > selector [selector name] [proxy name]. Select proxy for selector
  update         Usage: > update. Update selector and proxy information
  h      Print this help
  q      Quit client
> print selectors
...
selectors in config...
...
> print selector S1
...
information about S1
...
> select S1 P1
> update
> print selector S1
...
P1 is now selected
...
> q
```

