import pyautogui
import json
import time


def run_calibration(status_callback=None):
    def log(msg):
        if status_callback:
            status_callback(msg)
        else:
            print(msg)

    config = {}

    steps = [
        ("preview",   "Hover over the CENTER of the color preview swatch"),
        ("hue_top",   "Hover over the TOP of the hue slider"),
        ("hue_bot",   "Hover over the BOTTOM of the hue slider"),
        ("sat_top",   "Hover over the TOP of the saturation slider"),
        ("sat_bot",   "Hover over the BOTTOM of the saturation slider"),
        ("val_top",   "Hover over the TOP of the brightness slider"),
        ("val_bot",   "Hover over the BOTTOM of the brightness slider"),
    ]

    positions = {}

    for key, instruction in steps:
        log(f"{instruction}, then press Enter...")
        input()
        pos = pyautogui.position()
        positions[key] = pos
        log(f"  Captured: ({pos.x}, {pos.y})")
        time.sleep(0.2)

    config = {
        "preview": [positions["preview"].x, positions["preview"].y],
        "hue": {
            "x":      positions["hue_top"].x,
            "top":    positions["hue_top"].y,
            "bottom": positions["hue_bot"].y,
        },
        "sat": {
            "x":      positions["sat_top"].x,
            "top":    positions["sat_top"].y,
            "bottom": positions["sat_bot"].y,
        },
        "val": {
            "x":      positions["val_top"].x,
            "top":    positions["val_top"].y,
            "bottom": positions["val_bot"].y,
        },
    }

    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

    log("Calibration complete! config.json saved.")
    return config


if __name__ == "__main__":
    print("=== Dialed.gg Bot Calibration ===")
    print("Open the game in your browser and start a round before continuing.")
    print("You will hover over 7 positions and press Enter for each.\n")
    run_calibration()
    print("\nYou're all set. Run main.py to start the bot.")
