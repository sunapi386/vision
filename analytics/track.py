#!/usr/bin/env python3
"""Minimal analytics tracker. Appends events to a JSONL file."""

import json
import sys
import urllib.request
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

LOG_PATH = "/var/www/jasonsun.org/analytics.jsonl"
GEO_CACHE_PATH = "/var/www/jasonsun.org/geo-cache.json"

PRIVATE_PREFIXES = ("127.", "10.", "192.168.", "0.", "::1", "fc", "fd", "fe80")
NOISE_EVENTS = {"test", "test2", "verify", "lan-test", "external-test", "e2e-test", "setup-complete", "restart-test"}


def _lookup_geo(ips):
    cache = {}
    try:
        with open(GEO_CACHE_PATH) as f:
            cache = json.load(f)
    except Exception:
        pass

    uncached = [ip for ip in ips
                if ip not in cache and not any(ip.startswith(p) for p in PRIVATE_PREFIXES)]

    if uncached:
        for i in range(0, len(uncached), 100):
            batch = uncached[i:i + 100]
            try:
                req = urllib.request.Request(
                    "http://ip-api.com/batch?fields=query,country,countryCode,city,regionName,lat,lon",
                    data=json.dumps(batch).encode(),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    results = json.loads(resp.read())
                for r in results:
                    q = r.get("query", "")
                    if q and r.get("country"):
                        cache[q] = {
                            "country": r.get("country", ""),
                            "cc": r.get("countryCode", ""),
                            "city": r.get("city", ""),
                            "region": r.get("regionName", ""),
                            "lat": r.get("lat", 0),
                            "lon": r.get("lon", 0),
                        }
            except Exception:
                pass

        try:
            with open(GEO_CACHE_PATH, "w") as f:
                json.dump(cache, f)
        except Exception:
            pass

    return {ip: cache[ip] for ip in ips if ip in cache}


def _load_events():
    events = []
    ips = set()
    try:
        with open(LOG_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    if e.get("event") not in NOISE_EVENTS:
                        events.append(e)
                    if e.get("ip"):
                        ips.add(e["ip"])
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    return events, ips


def _build_summary(events, geo):
    by_day = defaultdict(lambda: {"pageviews": 0, "plays": 0, "ips": set()})
    locations = defaultdict(lambda: {"pageviews": 0, "ips": set(), "by_day": defaultdict(lambda: {"pv": 0, "ips": set()})})
    referrers = defaultdict(int)
    total = {"pageviews": 0, "plays": 0, "completes": 0, "ips": set(), "sessions": set()}

    for e in events:
        ip = e.get("ip", "")
        ev = e.get("event", "")
        day = (e.get("ts") or "")[:10]
        sid = e.get("sid", "")

        if ip:
            total["ips"].add(ip)
        if sid:
            total["sessions"].add(sid)

        if ev == "pageview":
            total["pageviews"] += 1
            if day:
                by_day[day]["pageviews"] += 1
                if ip:
                    by_day[day]["ips"].add(ip)

            if ip and ip in geo:
                g = geo[ip]
                loc_key = f"{g['city']}, {g['cc']}"
                locations[loc_key]["pageviews"] += 1
                locations[loc_key]["ips"].add(ip)
                locations[loc_key]["cc"] = g["cc"]
                locations[loc_key]["country"] = g["country"]
                if day:
                    locations[loc_key]["by_day"][day]["pv"] += 1
                    locations[loc_key]["by_day"][day]["ips"].add(ip)

            ref = e.get("ref", "")
            if ref:
                try:
                    host = ref.replace("https://", "").replace("http://", "").split("/")[0]
                    if host and "jasonsun.org" not in host:
                        referrers[host] += 1
                except Exception:
                    pass

        elif ev == "play":
            total["plays"] += 1
        elif ev == "complete":
            total["completes"] += 1

    daily = []
    for day in sorted(by_day.keys()):
        d = by_day[day]
        daily.append({"date": day, "pageviews": d["pageviews"], "plays": d["plays"], "unique_ips": len(d["ips"])})

    loc_list = []
    for key, loc in locations.items():
        loc_days = {}
        for day, dd in loc["by_day"].items():
            loc_days[day] = {"pageviews": dd["pv"], "unique_ips": len(dd["ips"])}
        loc_list.append({
            "location": key, "cc": loc.get("cc", ""), "country": loc.get("country", ""),
            "pageviews": loc["pageviews"], "unique_ips": len(loc["ips"]), "by_day": loc_days,
        })
    loc_list.sort(key=lambda x: (-x["unique_ips"], -x["pageviews"]))

    ref_list = [{"host": h, "count": c} for h, c in referrers.items()]
    ref_list.sort(key=lambda x: -x["count"])

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "totals": {
            "events": len(events),
            "pageviews": total["pageviews"],
            "plays": total["plays"],
            "completes": total["completes"],
            "unique_ips": len(total["ips"]),
            "sessions": len(total["sessions"]),
        },
        "daily": daily,
        "locations": loc_list,
        "referrers": ref_list[:20],
    }


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/stats":
            self._handle_stats()
        elif self.path == "/api/summary":
            self._handle_summary()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_stats(self):
        events, ips = _load_events()
        geo = _lookup_geo(list(ips))
        body = json.dumps({"events": events, "geo": geo}).encode()
        self._respond_json(body)

    def _handle_summary(self):
        events, ips = _load_events()
        geo = _lookup_geo(list(ips))
        summary = _build_summary(events, geo)
        body = json.dumps(summary, indent=2).encode()
        self._respond_json(body)

    def _respond_json(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/track":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}
        ip = self.headers.get("X-Forwarded-For", self.headers.get("X-Real-IP", self.client_address[0]))
        if ip and "," in ip:
            ip = ip.split(",")[0].strip()
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "ip": ip,
            "ua": self.headers.get("User-Agent", ""),
            "ref": self.headers.get("Referer", ""),
        }
        entry.update(data)
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9100
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Tracker listening on 0.0.0.0:{port}")
    server.serve_forever()
