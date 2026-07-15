# klipper-cam-sight

Camera based nozzle offset calibration for Klipper toolchangers. Runs on your printer - no extra software to install.

![Cam Sight demo](media/demo.webp)

## Install

SSH into your printer host and run these commands in order.

### 1. Download

```bash
cd ~
git clone https://github.com/charliemayall/klipper-cam-sight.git
cd klipper-cam-sight
```

### 2. Install

```bash
make install
```

This links Cam Sight into Moonraker and Klipper, adds `[cam_sight]` to `moonraker.conf`, and sets up the Mainsail sidebar entry (if you don't already have a custom `navi.json`).

### 3. Restart Moonraker

```bash
sudo systemctl restart moonraker
```

### 4. Klipper config

**Bondtech INDX users** - skip to step 5. Cam Sight writes the same `t{n}_offset_x` / `t{n}_offset_y` variables INDX uses. You still need INDX `CAL_Z` for Z.

**Everyone else** - add this to `printer.cfg`:

```ini
[include cam_sight.cfg]
```

You need a `[save_variables]` section (add one if you don't have it already - see [Klipper docs](https://www.klipper3d.org/Config_Reference.html#save_variables)).

Add this line to each toolchange macro, after the physical tool swap:

```gcode
APPLY_TOOL_OFFSET TOOL=1
```

Use the tool number you're loading (`TOOL=0` clears the offset).

Then restart Klipper:

```bash
sudo systemctl restart klipper
```

### 5. Mainsail sidebar

If `make install` created `~/printer_data/config/.theme/navi.json`, you're done - refresh Mainsail.

If you already had a custom sidebar, add this entry to your `navi.json`:

```json
{
  "title": "Cam Sight",
  "href": "/server/files/cam_sight/",
  "target": "_self",
  "position": 45
}
```

### 6. Open Cam Sight

In Mainsail, click **Cam Sight** in the sidebar.

Or go to: `http://<your-printer-ip>/server/files/cam_sight/`

## Calibrate

1. Pick your webcam from the dropdown in the header (if your webcam isn't showing already)
2. Set your tool count with **+** / **−** in the offsets panel.
3. **Calibrate mm/px** - follow the on-screen wizard (jog +X, +Y, click to circle the center at each position).
4. **Tool 0** - click to draw a 3 point circle around the nozzle centre.
5. **Each other tool** - select the tool in the table, click to draw a 3 point circle around the nozzle centre. Repeat until it lines up.
6. **Save offsets** - writes values for print time.

> **INDX users**: selecting a tool row runs `CHANGE_TOOL` automatically.

## Updates

If `make install` added an update manager entry, update from Mainsail's **Settings → Update Manager**. Otherwise pull manually:

```bash
cd ~/klipper-cam-sight
git pull
make install
sudo systemctl restart moonraker
```

## Development

From a clone on your dev machine:

```bash
make check           # install self-check + Python module asserts
make dev-frontend    # Vite dev server (uses .env for Moonraker URL if set)
make build-frontend  # production build → frontend/dist
```

Deploy to a printer host (set `DEPLOY_HOST` and `DEPLOY_PATH`):

```bash
DEPLOY_HOST=pi@printer DEPLOY_PATH=~/klipper-cam-sight make deploy
```
