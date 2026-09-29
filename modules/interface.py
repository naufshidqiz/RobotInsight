"""Canvas-drawn RobotInsight face with lightweight state-driven animation."""

import math
import threading
import time
import textwrap
import tkinter as tk

from PIL import Image, ImageTk


_current_state = "idle"
_state_lock = threading.Lock()
_state_started = time.monotonic()
_window_ready = threading.Event()

_capture_image = None
_capture_lock = threading.Lock()
_capture_changed = threading.Event()
_conversation = {"question": "", "answer": ""}
_conversation_lock = threading.Lock()

BACKGROUND = "#f7f4e9"
INK = "#282d30"
TEAL = "#62bdb3"
TEAL_DARK = "#398e89"
GOLD = "#f1c76a"


def show_capture(pil_image):
    """Show a camera image over the character while vision runs."""
    global _capture_image
    with _capture_lock:
        _capture_image = pil_image.copy()
        _capture_changed.set()


def clear_capture():
    """Hide the camera image overlay."""
    global _capture_image
    with _capture_lock:
        _capture_image = None
        _capture_changed.set()


def set_state(state: str):
    global _current_state, _state_started
    with _state_lock:
        if state != _current_state:
            _current_state = state
            _state_started = time.monotonic()


def get_state() -> str:
    with _state_lock:
        return _current_state


def set_conversation(question=None, answer=None):
    """Update the two side-panel captions from the assistant worker thread."""
    with _conversation_lock:
        if question is not None:
            _conversation["question"] = question
        if answer is not None:
            _conversation["answer"] = answer


def _rounded_rectangle(canvas, x1, y1, x2, y2, radius, *, fill, outline, width, sx, sy):
    """Draw a smooth rounded rectangle in the character's 1000x700 coordinate space."""
    points = []
    corners = (
        (x2 - radius, y1 + radius, -90, 0),
        (x2 - radius, y2 - radius, 0, 90),
        (x1 + radius, y2 - radius, 90, 180),
        (x1 + radius, y1 + radius, 180, 270),
    )
    for cx, cy, start, end in corners:
        for step in range(7):
            angle = math.radians(start + (end - start) * step / 6)
            points.extend((sx(cx + radius * math.cos(angle)), sy(cy + radius * math.sin(angle))))
    canvas.create_polygon(
        points, smooth=True, splinesteps=12, fill=fill, outline=outline,
        width=max(1, round(width * min(sx(1) - sx(0), sy(1) - sy(0)))),
        joinstyle=tk.ROUND, tags="art",
    )


def _run_ui():
    root = tk.Tk()
    root.title("RobotInsight")
    root.configure(bg=BACKGROUND)
    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda _event: root.attributes("-fullscreen", False))
    root.bind("<F11>", lambda _event: root.attributes("-fullscreen", True))

    canvas = tk.Canvas(root, bg=BACKGROUND, bd=0, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    root.update()

    photo_label = tk.Label(root, bg=BACKGROUND, bd=3, highlightthickness=3,
                           highlightbackground=INK, relief="flat")
    photo_label.place_forget()
    photo_ref = {"image": None}

    def update_capture_overlay():
        if _capture_changed.is_set():
            _capture_changed.clear()
            with _capture_lock:
                captured = _capture_image
            if captured is None:
                photo_label.place_forget()
                photo_ref["image"] = None
            else:
                width = max(220, int(root.winfo_screenwidth() * 0.27))
                height = max(160, int(root.winfo_screenheight() * 0.27))
                image = captured.copy()
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
                photo_ref["image"] = ImageTk.PhotoImage(image)
                photo_label.configure(image=photo_ref["image"])
                photo_label.place(relx=0.50, rely=0.50, anchor="center")
                photo_label.lift()
        root.after(60, update_capture_overlay)

    def animate():
        canvas.delete("art")
        width = max(1, canvas.winfo_width())
        height = max(1, canvas.winfo_height())
        scale = min(width / 1000, height / 700)
        ox = (width - 1000 * scale) / 2
        oy = (height - 700 * scale) / 2
        base_sx = lambda x: ox + x * scale
        base_sy = lambda y: oy + y * scale
        # Reserve generous side margins for the conversation panels.
        sx = lambda x: base_sx(500 + (x - 500) * 0.72)
        sy = lambda y: base_sy(350 + (y - 350) * 0.72)
        sw = lambda n: max(1, round(n * scale))

        with _state_lock:
            state = _current_state
            elapsed = time.monotonic() - _state_started
        phase = time.monotonic()

        # Gentle idle blinking; the first second of warmup opens the eyes.
        blink = max(0.13, 1 - max(0, 1 - abs((phase % 4.7) - 4.48) / 0.22))
        openness = 1.0
        if state == "warmup":
            openness = min(1.0, 0.12 + elapsed * 0.95)
        elif state == "idle":
            openness = blink
        elif state == "thinking":
            openness = 0.82 + 0.05 * math.sin(phase * 1.5)

        # Soft floor shadow and two little antennae make the sketch a small robot.
        canvas.create_oval(sx(305), sy(604), sx(695), sy(635), fill="#e8e3d4", outline="", tags="art")
        canvas.create_line(sx(420), sy(178), sx(392), sy(119), fill=INK, width=sw(8), capstyle=tk.ROUND, tags="art")
        canvas.create_line(sx(580), sy(178), sx(608), sy(119), fill=INK, width=sw(8), capstyle=tk.ROUND, tags="art")
        canvas.create_oval(sx(376), sy(94), sx(408), sy(126), fill=GOLD, outline=INK, width=sw(5), tags="art")
        canvas.create_oval(sx(592), sy(94), sx(624), sy(126), fill=TEAL, outline=INK, width=sw(5), tags="art")

        # Side sensors peek out from behind the rounded face screen.
        for x in (192, 774):
            _rounded_rectangle(canvas, x, 330, x + 34, 420, 15, fill=TEAL,
                               outline=INK, width=5, sx=sx, sy=sy)
            canvas.create_oval(sx(x + 10), sy(360), sx(x + 24), sy(374),
                               fill="#eafffc", outline="", tags="art")

        # Face shell and inset screen.
        _rounded_rectangle(canvas, 210, 158, 790, 590, 104, fill="#fffdf7",
                           outline=INK, width=8, sx=sx, sy=sy)
        _rounded_rectangle(canvas, 230, 178, 770, 570, 90, fill="#fffdf7",
                           outline="#d9d4c7", width=2, sx=sx, sy=sy)

        # Listening sound ripples and thinking dots are kept subtle and state-specific.
        if state == "listening":
            pulse = 0.5 + 0.5 * math.sin(phase * 5)
            for side in (-1, 1):
                cx = 500 + side * 345
                for ring in range(3):
                    radius = 29 + ring * 20 + pulse * 5
                    canvas.create_arc(sx(cx - radius), sy(310 - radius), sx(cx + radius), sy(310 + radius),
                                      start=290 if side < 0 else 70, extent=140 if side < 0 else 140,
                                      style=tk.ARC, outline=TEAL_DARK, width=sw(5 - ring), tags="art")
        elif state == "thinking":
            for index, (x, y) in enumerate(((706, 248), (736, 220), (760, 188))):
                bob = math.sin(phase * 2.4 + index) * 4
                radius = 5 + index * 2
                canvas.create_oval(sx(x - radius), sy(y + bob - radius), sx(x + radius), sy(y + bob + radius),
                                   fill=GOLD, outline=INK, width=sw(2), tags="art")

        # Keep slow model and web requests visible so the robot never appears frozen.
        status_text = {
            "thinking": "Thinking...",
            "searching": "Searching the web...",
            "capturing": "Taking a look...",
        }.get(state, "")
        if status_text:
            canvas.create_text(sx(500), sy(650), text=status_text, fill=TEAL_DARK,
                               font=("Segoe UI", max(12, round(22 * scale)), "bold"), tags="art")

        # Question and answer stay visible beside the smaller character.
        panel_top, panel_bottom = 145, 555
        for x1, x2, heading, key in (
            (18, 270, "MY QUESTION", "question"),
            (730, 982, "AI ANSWER", "answer"),
        ):
            _rounded_rectangle(canvas, x1, panel_top, x2, panel_bottom, 22,
                               fill="#fffdf7", outline="#d9d4c7", width=2,
                               sx=base_sx, sy=base_sy)
            canvas.create_text(base_sx(x1 + 18), base_sy(panel_top + 24), text=heading,
                               anchor="w", fill=TEAL_DARK,
                               font=("Segoe UI", max(10, round(15 * scale)), "bold"), tags="art")
            with _conversation_lock:
                panel_text = _conversation[key]
            panel_text = panel_text.strip() or ("Waiting for your question..." if key == "question" else "Waiting for an answer...")
            panel_text = panel_text[:360]
            wrapped = "\n".join(textwrap.wrap(panel_text, width=23, break_long_words=True))
            canvas.create_text(base_sx(x1 + 18), base_sy(panel_top + 52), text=wrapped,
                               anchor="nw", width=base_sx(x2 - 16) - base_sx(x1 + 18),
                               fill=INK, justify="left",
                               font=("Segoe UI", max(9, round(14 * scale))), tags="art")

        pupil_dx = math.sin(phase * 0.8) * 4 if state == "idle" else 0
        pupil_dy = -14 if state == "thinking" else (1 if state == "listening" else 0)
        if state == "capturing":
            pupil_dx = math.sin(phase * 2) * 5

        for center_x in (382, 618):
            eye_top = 292 + (1 - openness) * 31
            eye_bottom = 392 - (1 - openness) * 35
            canvas.create_oval(sx(center_x - 58), sy(eye_top), sx(center_x + 58), sy(eye_bottom),
                               fill="#ffffff", outline=INK, width=sw(6), tags="art")
            canvas.create_oval(sx(center_x - 26 + pupil_dx), sy(321 + pupil_dy),
                               sx(center_x + 26 + pupil_dx), sy(374 + pupil_dy),
                               fill=TEAL_DARK, outline=INK, width=sw(4), tags="art")
            canvas.create_oval(sx(center_x - 8 + pupil_dx), sy(332 + pupil_dy),
                               sx(center_x + 12 + pupil_dx), sy(355 + pupil_dy),
                               fill="#20292c", outline="", tags="art")
            canvas.create_oval(sx(center_x - 13 + pupil_dx), sy(328 + pupil_dy),
                               sx(center_x - 4 + pupil_dx), sy(337 + pupil_dy),
                               fill="white", outline="", tags="art")
            brow_y = 263 if state != "listening" else 249
            canvas.create_line(sx(center_x - 48), sy(brow_y + 8), sx(center_x), sy(brow_y),
                               sx(center_x + 48), sy(brow_y + 8), fill=INK, width=sw(8),
                               smooth=True, capstyle=tk.ROUND, tags="art")

        # A little nose keeps the face close to the original hand-drawn sketch.
        canvas.create_line(sx(492), sy(406), sx(480), sy(428), sx(503), sy(431),
                           fill=INK, width=sw(5), smooth=True, capstyle=tk.ROUND, tags="art")

        # Smiling mouth; during speech it gently opens and closes like a talking character.
        if state == "speaking":
            mouth_open = 12 + 30 * abs(math.sin(phase * 10.5))
            canvas.create_oval(sx(455), sy(466 - mouth_open / 2), sx(545), sy(466 + mouth_open),
                               fill="#8c4550", outline=INK, width=sw(5), tags="art")
            if mouth_open > 27:
                canvas.create_arc(sx(468), sy(464), sx(532), sy(493), start=180, extent=180,
                                  style=tk.ARC, outline="#ffd1ca", width=sw(5), tags="art")
        elif state == "capturing":
            canvas.create_oval(sx(480), sy(454), sx(520), sy(494), fill="#fffdf7",
                               outline=INK, width=sw(5), tags="art")
            flash = max(0, math.sin(phase * 7))
            if flash > 0.8:
                canvas.create_line(sx(500), sy(438), sx(500), sy(424), fill=GOLD, width=sw(5), tags="art")
                canvas.create_line(sx(463), sy(449), sx(451), sy(439), fill=GOLD, width=sw(5), tags="art")
                canvas.create_line(sx(537), sy(449), sx(549), sy(439), fill=GOLD, width=sw(5), tags="art")
        else:
            smile = 495 if state == "thinking" else 480
            canvas.create_line(sx(420), sy(smile), sx(460), sy(smile + 24), sx(500), sy(smile + 30),
                               sx(540), sy(smile + 24), sx(580), sy(smile), fill=INK,
                               width=sw(8), smooth=True, capstyle=tk.ROUND, tags="art")

        # Tiny cheek marks give the robot a warm, friendly expression.
        if state in ("idle", "listening", "speaking"):
            for x in (316, 684):
                canvas.create_arc(sx(x - 18), sy(433), sx(x + 18), sy(451), start=10, extent=160,
                                  style=tk.ARC, outline="#dc9d8c", width=sw(4), tags="art")

        if state == "capturing":
            pulse = 0.5 + 0.5 * math.sin(phase * 3)
            radius = 310 + pulse * 8
            canvas.create_oval(sx(500 - radius), sy(374 - radius), sx(500 + radius), sy(374 + radius),
                               outline=TEAL, width=sw(2), dash=(sw(7), sw(8)), tags="art")

        root.after(33, animate)

    update_capture_overlay()
    animate()
    _window_ready.set()
    root.mainloop()


def start():
    """Launch the fullscreen animated face on its own UI thread."""
    thread = threading.Thread(target=_run_ui, daemon=True)
    thread.start()
    _window_ready.wait(timeout=8)
    print("[UI] Animated interface ready")
