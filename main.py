import customtkinter as ctk
import threading
import colorsys
import json
import os
import pyautogui
import time


# ── theme ──────────────────────────────────────────────────────────────────────
BG = "#0d0d0f"
SURFACE = "#16161a"
SURFACE2 = "#1e1e24"
ACCENT = "#ffffff"
ACCENT_DIM = "#6e6d75"
SUCCESS = "#3ddc97"
WARNING = "#ffb347"
TEXT = "#e8e8f0"
TEXT_DIM = "#6b6b80"
BORDER = "#2a2a35"


# ── config helpers ─────────────────────────────────────────────────────────────
def load_config():
    if os.path.exists("config.json"):
        with open("config.json") as f:
            return json.load(f)
    return None


def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)


# ── bot logic ──────────────────────────────────────────────────────────────────
def wait_for_change(x, y, original_color, threshold=30):
    while True:
        current = pyautogui.screenshot().getpixel((x, y))
        diff = sum(abs(c1 - c2) for c1, c2 in zip(original_color, current))
        if diff > threshold:
            break


def get_color(px, py, samples=3, delay=0.05):
    readings = []
    for _ in range(samples):
        readings.append(pyautogui.screenshot().getpixel((px, py)))
        time.sleep(delay)
    avg_r = sum(p[0] for p in readings) // samples
    avg_g = sum(p[1] for p in readings) // samples
    avg_b = sum(p[2] for p in readings) // samples
    return avg_r, avg_g, avg_b


def map_to_hue_y(value, max_value, top_y, bottom_y):
    return top_y + (value / max_value) * (bottom_y - top_y)


def map_to_sv_y(value, max_value, top_y, bottom_y):
    return bottom_y - (value / max_value) * (bottom_y - top_y)


def move_slider(x, start_y, target_y, duration=0.5):
    pyautogui.click(x, start_y)
    time.sleep(0.05)
    pyautogui.mouseDown(button='left')
    time.sleep(0.05)
    pyautogui.moveTo(x, target_y, duration=duration)
    time.sleep(0.05)
    pyautogui.mouseUp(button='left')
    time.sleep(0.05)


def run_bot(status_callback=None):
    def log(msg):
        if status_callback:
            status_callback(msg)
        else:
            print(msg)

    cfg = load_config()
    if cfg is None:
        log("Error: config.json not found. Please calibrate first.")
        return

    x, y = cfg["preview"]
    hue_x = cfg["hue"]["x"]
    hue_top = cfg["hue"]["top"]
    hue_bottom = cfg["hue"]["bottom"]
    sat_x = cfg["sat"]["x"]
    sat_top = cfg["sat"]["top"]
    sat_bottom = cfg["sat"]["bottom"]
    val_x = cfg["val"]["x"]
    val_top = cfg["val"]["top"]
    val_bottom = cfg["val"]["bottom"]

    log("Waiting 2 seconds...")
    time.sleep(2)

    log("Capturing preview color...")
    preview_rgb = get_color(x, y)

    r, g, b = [c / 255 for c in preview_rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    game_h = round(h * 359)
    game_s = round(s * 100)
    game_v = round(v * 100)

    log(f"Color captured: H{game_h} S{game_s} B{game_v}")
    log("Waiting for screen to change...")
    log("Do not move your mouse.")
    wait_for_change(x, y, preview_rgb)
    time.sleep(1)

    hue_y = map_to_hue_y(game_h, 359, hue_top, hue_bottom)
    sat_y = map_to_sv_y(game_s, 100, sat_top, sat_bottom)
    val_y = map_to_sv_y(game_v, 100, val_top, val_bottom)

    log("Adjusting sliders...")
    move_slider(hue_x, hue_bottom, hue_y)
    move_slider(sat_x, sat_bottom, sat_y)
    move_slider(val_x, val_bottom, val_y)

    log("Done.")


# ── main app ───────────────────────────────────────────────────────────────────
class DialedBot(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("dialed.gg bot")
        self.geometry("420x660")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.config_data = load_config()
        self.calibration_step = 0
        self.calibration_positions = {}
        self.bot_running = False
        self._tracking = False

        self._build_ui()
        self._refresh_status_bar()

    # ── layout ─────────────────────────────────────────────────────────────────
    def _build_ui(self):

        # header
        header = ctk.CTkFrame(self, fg_color=SURFACE,
                              corner_radius=0, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="dialed.gg bot",
            font=ctk.CTkFont(family="Courier New", size=22, weight="bold"),
            text_color=ACCENT,
        ).place(x=20, y=18)

        self.status_dot = ctk.CTkLabel(
            header,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_DIM,
        )
        self.status_dot.place(x=375, y=24)

        # hsv display
        hsv_frame = ctk.CTkFrame(self, fg_color=SURFACE2, corner_radius=12)
        hsv_frame.pack(fill="x", padx=20, pady=(16, 0))

        ctk.CTkLabel(
            hsv_frame,
            text="LAST CAPTURE",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=TEXT_DIM,
        ).pack(anchor="w", padx=16, pady=(12, 4))

        hsv_row = ctk.CTkFrame(hsv_frame, fg_color="transparent")
        hsv_row.pack(fill="x", padx=16, pady=(0, 14))

        self.h_label = self._hsv_tile(hsv_row, "H", "—")
        self.s_label = self._hsv_tile(hsv_row, "S", "—")
        self.v_label = self._hsv_tile(hsv_row, "B", "—")

        # color swatch
        self.swatch = ctk.CTkFrame(
            self, fg_color=SURFACE2, corner_radius=12, height=56
        )
        self.swatch.pack(fill="x", padx=20, pady=(10, 0))
        self.swatch.pack_propagate(False)

        self.swatch_label = ctk.CTkLabel(
            self.swatch,
            text="no color captured yet",
            font=ctk.CTkFont(family="Courier New", size=11),
            text_color=TEXT_DIM,
        )
        self.swatch_label.place(relx=0.5, rely=0.5, anchor="center")

        # log box
        log_frame = ctk.CTkFrame(self, fg_color=SURFACE2, corner_radius=12)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(14, 0))

        ctk.CTkLabel(
            log_frame,
            text="LOG",
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=TEXT_DIM,
        ).pack(anchor="w", padx=14, pady=(10, 4))

        self.log_box = ctk.CTkTextbox(
            log_frame,
            fg_color="transparent",
            font=ctk.CTkFont(family="Courier New", size=12),
            text_color=TEXT,
            wrap="word",
            state="disabled",
        )
        self.log_box._textbox.bind(
            "<MouseWheel>",
            lambda e: self.log_box._textbox.yview_scroll(
                int(-1 * (e.delta / 120)), "units")
        )
        self.log_box.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        # buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=16)
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        self.calibrate_btn = ctk.CTkButton(
            btn_frame,
            text="Recalibrate" if self.config_data else "Calibrate",
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            fg_color=SURFACE2,
            hover_color=SURFACE,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT,
            corner_radius=8,
            height=44,
            command=self._start_calibration,
        )
        self.calibrate_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.run_btn = ctk.CTkButton(
            btn_frame,
            text="▶  Run Bot",
            font=ctk.CTkFont(family="Courier New", size=13, weight="bold"),
            fg_color=ACCENT,
            hover_color=ACCENT_DIM,
            text_color="#000000",
            corner_radius=8,
            height=44,
            command=self._start_bot,
        )
        self.run_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # status bar
        self.status_bar = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family="Courier New", size=11),
            text_color=TEXT_DIM,
            height=24,
        )
        self.status_bar.pack(pady=(0, 8))

    def _hsv_tile(self, parent, label, value):
        tile = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=8)
        tile.pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkLabel(
            tile,
            text=label,
            font=ctk.CTkFont(family="Courier New", size=10),
            text_color=TEXT_DIM,
        ).pack(pady=(8, 0))

        val_label = ctk.CTkLabel(
            tile,
            text=value,
            font=ctk.CTkFont(family="Courier New", size=20, weight="bold"),
            text_color=ACCENT,
        )
        val_label.pack(pady=(0, 8))
        return val_label

    # ── logging ────────────────────────────────────────────────────────────────
    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"› {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    # ── status bar ─────────────────────────────────────────────────────────────
    def _refresh_status_bar(self):
        if self.config_data:
            self.status_bar.configure(
                text="● calibrated  —  ready to run", text_color=SUCCESS
            )
            self.status_dot.configure(text_color=SUCCESS)
        else:
            self.status_bar.configure(
                text="○ not calibrated  —  run calibration first", text_color=WARNING
            )
            self.status_dot.configure(text_color=WARNING)

    # ── cursor tracker ─────────────────────────────────────────────────────────
    def _start_cursor_tracker(self):
        self._tracking = True
        self._track_cursor()

    def _track_cursor(self):
        if not self._tracking:
            return
        pos = pyautogui.position()
        self.status_bar.configure(
            text=f"cursor: ({pos.x}, {pos.y})  —  press Enter to capture",
            text_color=TEXT_DIM,
        )
        self.after(100, self._track_cursor)

    def _stop_cursor_tracker(self):
        self._tracking = False

    # ── calibration ────────────────────────────────────────────────────────────
    CALIBRATION_STEPS = [
        ("preview", "Hover over the CENTER of the color swatch"),
        ("hue_top", "Hover over the TOP of the hue slider track"),
        ("hue_bot", "Hover over the BOTTOM of the hue slider track"),
        ("sat",     "Hover over the CENTER of the saturation slider (X position only)"),
        ("val",     "Hover over the CENTER of the brightness slider (X position only)"),
    ]

    def _start_calibration(self):
        self._clear_log()
        self.calibration_step = 0
        self.calibration_positions = {}
        self._log("Starting calibration — open the game first.")
        self._log("Hover over each point and press Enter to capture.")
        self._next_calibration_step()

    def _next_calibration_step(self):
        if self.calibration_step >= len(self.CALIBRATION_STEPS):
            self._finish_calibration()
            return

        key, instruction = self.CALIBRATION_STEPS[self.calibration_step]
        step_num = self.calibration_step + 1
        total = len(self.CALIBRATION_STEPS)
        self._log(f"[{step_num}/{total}] {instruction}")

        self.bind("<Return>", lambda e: self._capture_position())
        self._start_cursor_tracker()

        self.calibrate_btn.configure(
            text=f"Capture ({step_num}/{total})",
            fg_color=SURFACE2,
            hover_color=ACCENT_DIM,
            text_color="#ffffff",
            border_width=0,
            command=self._capture_position,
        )

    def _capture_position(self):
        if hasattr(self, "_last_capture") and time.time() - self._last_capture < 0.3:
            return
        self._last_capture = time.time()

        key, _ = self.CALIBRATION_STEPS[self.calibration_step]
        pos = pyautogui.position()
        self.calibration_positions[key] = pos
        self._log(f"  ✓ captured ({pos.x}, {pos.y})")
        self.calibration_step += 1
        self._next_calibration_step()

    def _finish_calibration(self):
        self.unbind("<Return>")
        self._stop_cursor_tracker()

        p = self.calibration_positions
        shared_top = p["hue_top"].y
        shared_bottom = p["hue_bot"].y

        config = {
            "preview": [p["preview"].x, p["preview"].y],
            "hue": {"x": p["hue_top"].x, "top": shared_top, "bottom": shared_bottom},
            "sat": {"x": p["sat"].x,     "top": shared_top, "bottom": shared_bottom},
            "val": {"x": p["val"].x,     "top": shared_top, "bottom": shared_bottom},
        }

        save_config(config)
        self.config_data = config
        self._log("Calibration saved ✓")
        self._log(f"  Slider Y range: {shared_top} → {shared_bottom}")
        self._log(
            f"  Hue X: {p['hue_top'].x}  Sat X: {p['sat'].x}  Val X: {p['val'].x}")

        self.calibrate_btn.configure(
            text="Recalibrate",
            fg_color=SURFACE2,
            hover_color=SURFACE,
            border_color=BORDER,
            border_width=1,
            text_color=TEXT,
            command=self._start_calibration,
        )
        self._refresh_status_bar()

    # ── bot runner ─────────────────────────────────────────────────────────────
    def _start_bot(self):
        if self.bot_running:
            return
        if not self.config_data:
            self._log("⚠ Run calibration first.")
            return

        self._clear_log()
        self.bot_running = True
        self.run_btn.configure(
            text="Running...", state="disabled", fg_color=SURFACE2)
        threading.Thread(target=self._run_bot_thread, daemon=True).start()

    def _run_bot_thread(self):
        try:
            run_bot(status_callback=self._on_bot_status)
        except Exception as e:
            self.after(0, self._log, f"Error: {e}")
        finally:
            self.after(0, self._bot_finished)

    def _on_bot_status(self, msg):
        self.after(0, self._log, msg)

        if msg.startswith("Color captured:"):
            try:
                parts = msg.split()
                h = parts[2][1:]
                s = parts[3][1:]
                v = parts[4][1:]
                self.after(0, lambda val=h: self.h_label.configure(text=val))
                self.after(0, lambda val=s: self.s_label.configure(text=val))
                self.after(0, lambda val=v: self.v_label.configure(text=val))

                hf = int(h) / 359
                sf = int(s) / 100
                vf = int(v) / 100
                r, g, b = colorsys.hsv_to_rgb(hf, sf, vf)
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    int(r * 255), int(g * 255), int(b * 255)
                )
                self.after(
                    0, lambda c=hex_color: self.swatch.configure(fg_color=c))
                self.after(0, lambda: self.swatch_label.configure(text=""))
            except Exception:
                pass

    def _bot_finished(self):
        self.bot_running = False
        self.run_btn.configure(
            text="▶  Run Bot", state="normal", fg_color=ACCENT)


# ── entry ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = DialedBot()
    app.mainloop()
