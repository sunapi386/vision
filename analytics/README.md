# jasonsun.org analytics tracker

`track.py` is the lightweight analytics server for jasonsun.org. Deployed to
`/var/www/jasonsun.org/track.py` on ocean (192.168.2.244), run by the
`jasonsun-tracker` systemd unit (here as `jasonsun-tracker.service`) as
`www-data` on port **9100**. nginx proxies `location /api/` → `127.0.0.1:9100`
(see the jasonsun.org vhost in `sunapi386/nginx`).

NOT tracked (runtime data / secrets, live only on the server):
- `analytics.jsonl` — the append-only event log
- `geo-cache.json` — IP→geo cache
- `.htpasswd` — basic-auth for the protected `/dir` path

Deploy: `track.py` ships with the site via `release.py` (DEPLOY_PATH=/var/www/jasonsun.org/);
after changing it, `sudo systemctl restart jasonsun-tracker` on ocean.
