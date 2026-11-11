import re
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SCENARIOS = {
    'scenario1': {'label': 'Scenario 1 (h2 attacks h3)'},
    'scenario2': {'label': 'Scenario 2 (h2 attacks h6)'},
    'scenario3': {'label': 'Scenario 3 (h5 attacks h6)'},
}

LINK_COST_RE = re.compile(
    r'^(?P<ts>\S+ \S+) Link cost: (?P<a>\S+)-(?P<b>\S+) base=(?P<base>[\d.]+) '
    r'load=(?P<load>[\d.]+) anomaly=(?P<anomaly>\d+) cost=(?P<cost>[\d.]+)'
)
PING_RE = re.compile(r'^\[(?P<epoch>\d+\.\d+)\].*icmp_seq=(?P<seq>\d+)')

BASELINE_LINKS = ['01-02', '02-06']
REROUTE_LINKS = ['01-05', '03-05', '03-06']
ALL_LINKS = BASELINE_LINKS + REROUTE_LINKS


def parse_ryu_log(path):
    rows = []
    try:
        f = open(path, errors='ignore')
    except FileNotFoundError:
        print(f"WARNING: {path} not found")
        return rows
    with f:
        for line in f:
            m = LINK_COST_RE.match(line)
            if not m:
                continue
            try:
                ts = datetime.strptime(m.group('ts'), '%Y-%m-%d %H:%M:%S,%f')
            except ValueError:
                continue
            a, b = m.group('a')[-2:], m.group('b')[-2:]
            link = '-'.join(sorted([a, b]))
            rows.append({
                'ts': ts,
                'link': link,
                'load': float(m.group('load')),
                'anomaly': int(m.group('anomaly')),
                'cost': float(m.group('cost')),
            })
    return rows


def parse_ping_log(path):
    pings = []
    try:
        f = open(path, errors='ignore')
    except FileNotFoundError:
        print(f"WARNING: {path} not found")
        return pings
    with f:
        for line in f:
            m = PING_RE.match(line)
            if m:
                pings.append((float(m.group('epoch')), int(m.group('seq'))))
    return pings


def loss_percent_series(pings, window=2.0, interval=0.2):
    if not pings:
        return [], []
    pings.sort()
    t0, tN = pings[0][0], pings[-1][0]
    times, losses = [], []
    expected = window / interval
    t = t0
    while t < tN:
        count = sum(1 for (ts, seq) in pings if t <= ts < t + window)
        loss = max(0.0, (expected - count) / expected * 100)
        times.append(t - t0)
        losses.append(loss)
        t += window
    return times, losses


def plot_link_cost(rows, label, outpath):
    if not rows:
        print(f"No link cost rows for {label}")
        return
    t0 = min(r['ts'] for r in rows)
    plt.figure(figsize=(10, 5))
    any_plotted = False
    for link in ALL_LINKS:
        pts = [r for r in rows if r['link'] == link]
        if not pts:
            continue
        xs = [(p['ts'] - t0).total_seconds() for p in pts]
        ys = [p['cost'] for p in pts]
        plt.plot(xs, ys, marker='o', markersize=3, label=f"s{link}")
        any_plotted = True
    if not any_plotted:
        plt.close()
        print(f"No matching links for {label}")
        return
    plt.xlabel('Time (s)')
    plt.ylabel('Link cost Cij(t)')
    plt.title(f'Link cost vs time - {label}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(outpath, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Saved {outpath}")


def plot_loss(pings, label, outpath):
    times, losses = loss_percent_series(pings)
    if not times:
        print(f"No ping data for {label}")
        return
    plt.figure(figsize=(10, 5))
    plt.plot(times, losses, marker='o', markersize=3, color='red')
    plt.xlabel('Time (s)')
    plt.ylabel('Packet loss (%)')
    plt.title(f'Packet loss vs time (h1->h6 baseline flow) - {label}')
    plt.ylim(-5, 105)
    plt.grid(True, alpha=0.3)
    plt.savefig(outpath, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Saved {outpath}")


def plot_throughput(rows, label, outpath):
    if not rows:
        print(f"No link cost rows for {label}")
        return
    t0 = min(r['ts'] for r in rows)
    plt.figure(figsize=(10, 5))
    any_plotted = False
    for link in ALL_LINKS:
        pts = [r for r in rows if r['link'] == link]
        if not pts:
            continue
        xs = [(p['ts'] - t0).total_seconds() for p in pts]
        ys = [p['load'] * 40.0 for p in pts]
        plt.plot(xs, ys, marker='o', markersize=3, label=f"s{link}")
        any_plotted = True
    if not any_plotted:
        plt.close()
        print(f"No matching links for {label}")
        return
    plt.xlabel('Time (s)')
    plt.ylabel('Link throughput (Mbps)')
    plt.title(f'Throughput vs time (per-link load) - {label}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(outpath, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Saved {outpath}")


for name, info in SCENARIOS.items():
    rows = parse_ryu_log(f"{name}_ryu.log")
    pings = parse_ping_log(f"{name}_ping.log")
    plot_link_cost(rows, info['label'], f"{name}_link_cost.png")
    plot_loss(pings, info['label'], f"{name}_packet_loss.png")
    plot_throughput(rows, info['label'], f"{name}_throughput.png")

print("All done.")
