import tkinter as tk
from tkinter import ttk
import random
import math
import time

# ── Palette ──────────────────────────────────────────────────────────────────
BG         = "#0D0D1A"   # deep space navy
PANEL      = "#13132B"   # card background
ACCENT     = "#7C3AED"   # violet pulse
ACCENT2    = "#06B6D4"   # cyan spark
SUCCESS    = "#10B981"   # emerald win
DANGER     = "#EF4444"   # red lose
WARM       = "#F59E0B"   # amber hint
TEXT       = "#E2E8F0"   # off-white
MUTED      = "#64748B"   # slate muted
BORDER     = "#1E1E3F"   # subtle border


class ParticleCanvas(tk.Canvas):
    """Ambient floating particle background."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.configure(bg=BG, highlightthickness=0)
        self.particles = []
        self._make_particles(40)
        self._animate()

    def _make_particles(self, n):
        w, h = 740, 620
        for _ in range(n):
            x = random.uniform(0, w)
            y = random.uniform(0, h)
            r = random.uniform(1, 3)
            speed = random.uniform(0.2, 0.8)
            drift = random.uniform(-0.3, 0.3)
            alpha_hex = random.choice(["33", "55", "77", "44"])
            color = random.choice([ACCENT, ACCENT2, WARM])
            oid = self.create_oval(x - r, y - r, x + r, y + r,
                                   fill=color + alpha_hex, outline="")
            self.particles.append([oid, x, y, r, speed, drift, 0, 0])

    def _animate(self):
        h = 620
        for p in self.particles:
            oid, x, y, r, speed, drift, _, _ = p
            y -= speed
            x += drift
            if y < -5:
                y = h + 5
                x = random.uniform(0, 740)
            if x < -5 or x > 745:
                drift = -drift
                p[5] = drift
            p[1], p[2] = x, y
            self.coords(oid, x - r, y - r, x + r, y + r)
        self.after(30, self._animate)


class GlowButton(tk.Canvas):
    """Custom canvas button with glow pulse animation."""

    def __init__(self, master, text, command, color=ACCENT, width=200, height=50, **kw):
        super().__init__(master, width=width, height=height,
                         bg=PANEL, highlightthickness=0, **kw)
        self.command = command
        self.color = color
        self.w, self.h = width, height
        self.text = text
        self._glow = 0
        self._dir = 1
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._pulse()

    def _draw(self, hover=False):
        self.delete("all")
        g = self._glow
        # outer glow
        for i in range(6, 0, -1):
            alpha = int(20 + g * 1.5) - i * 3
            alpha = max(0, min(255, alpha))
            hex_alpha = format(alpha, '02x')
            pad = i * 2
            self.create_rectangle(pad, pad, self.w - pad, self.h - pad,
                                   outline=self.color + hex_alpha,
                                   fill="", width=1)
        # fill
        fill = self.color if not hover else ACCENT2
        self.create_rectangle(6, 6, self.w - 6, self.h - 6,
                               fill=fill, outline="", )
        # text
        self.create_text(self.w // 2, self.h // 2, text=self.text,
                         fill="white", font=("Segoe UI", 13, "bold"))

    def _pulse(self):
        self._glow += self._dir * 2
        if self._glow >= 40:
            self._dir = -1
        elif self._glow <= 0:
            self._dir = 1
        self._draw()
        self.after(50, self._pulse)

    def _on_enter(self, _):
        self._draw(hover=True)

    def _on_leave(self, _):
        self._draw()

    def _on_click(self, _):
        if self.command:
            self.command()


class NumberGuessingGame(tk.Tk):

    DIFFICULTIES = {
        "Easy":   {"low": 1,   "high": 50,   "tries": 10, "label": "1 – 50"},
        "Medium": {"low": 1,   "high": 100,  "tries": 7,  "label": "1 – 100"},
        "Hard":   {"low": 1,   "high": 500,  "tries": 8,  "label": "1 – 500"},
        "Legend": {"low": 1,   "high": 1000, "tries": 10, "label": "1 – 1000"},
    }

    def __init__(self):
        super().__init__()
        self.title("🎯 Mind Reader — Number Guessing")
        self.geometry("740x620")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Game state
        self.secret      = tk.IntVar()
        self.tries_left  = tk.IntVar()
        self.max_tries   = tk.IntVar()
        self.score       = tk.IntVar(value=0)
        self.streak      = tk.IntVar(value=0)
        self.difficulty  = tk.StringVar(value="Medium")
        self.guess_history = []
        self.game_active = False

        self._build_ui()
        self._new_game()

    # ── UI BUILD ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Particle background
        self.canvas_bg = ParticleCanvas(self, width=740, height=620)
        self.canvas_bg.place(x=0, y=0)

        # ── Header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self.canvas_bg, bg=BG)
        hdr.place(x=0, y=0, width=740, height=80)

        tk.Label(hdr, text="🎯  MIND READER", font=("Segoe UI", 22, "bold"),
                 fg=ACCENT2, bg=BG).pack(side="left", padx=24, pady=18)

        # Score + Streak right
        stat_frame = tk.Frame(hdr, bg=BG)
        stat_frame.pack(side="right", padx=24)
        tk.Label(stat_frame, text="SCORE", font=("Segoe UI", 8), fg=MUTED, bg=BG).grid(row=0, column=0, padx=8)
        tk.Label(stat_frame, text="STREAK", font=("Segoe UI", 8), fg=MUTED, bg=BG).grid(row=0, column=1, padx=8)
        tk.Label(stat_frame, textvariable=self.score,  font=("Segoe UI", 20, "bold"),
                 fg=WARM, bg=BG).grid(row=1, column=0, padx=8)
        tk.Label(stat_frame, textvariable=self.streak, font=("Segoe UI", 20, "bold"),
                 fg=SUCCESS, bg=BG).grid(row=1, column=1, padx=8)

        # Divider line
        tk.Frame(self.canvas_bg, bg=BORDER, height=1).place(x=0, y=78, width=740)

        # ── Difficulty selector ───────────────────────────────────────────────
        diff_frame = tk.Frame(self.canvas_bg, bg=BG)
        diff_frame.place(x=20, y=90, width=700, height=50)
        tk.Label(diff_frame, text="DIFFICULTY:", font=("Segoe UI", 9),
                 fg=MUTED, bg=BG).pack(side="left", padx=(4, 10))
        for name in self.DIFFICULTIES:
            rb = tk.Radiobutton(diff_frame, text=name, variable=self.difficulty,
                                value=name, command=self._new_game,
                                font=("Segoe UI", 10, "bold"),
                                fg=TEXT, bg=BG, selectcolor=PANEL,
                                activebackground=BG, activeforeground=ACCENT2,
                                indicatoron=False, relief="flat",
                                padx=12, pady=4, cursor="hand2")
            rb.pack(side="left", padx=4)

        # ── Central card ─────────────────────────────────────────────────────
        card = tk.Frame(self.canvas_bg, bg=PANEL, bd=0)
        card.place(x=60, y=150, width=620, height=340)
        # card border glow
        tk.Frame(self.canvas_bg, bg=ACCENT, height=2).place(x=60, y=150, width=620)

        # Range label
        self.range_lbl = tk.Label(card, text="", font=("Segoe UI", 11),
                                   fg=MUTED, bg=PANEL)
        self.range_lbl.pack(pady=(22, 0))

        # Big prompt display
        self.prompt_lbl = tk.Label(card, text="",
                                    font=("Segoe UI", 16, "bold"),
                                    fg=TEXT, bg=PANEL, wraplength=550, justify="center")
        self.prompt_lbl.pack(pady=(8, 0))

        # Hint arrow display
        self.hint_lbl = tk.Label(card, text="",
                                  font=("Segoe UI", 36),
                                  fg=ACCENT, bg=PANEL)
        self.hint_lbl.pack(pady=4)

        # Tries bar
        tries_row = tk.Frame(card, bg=PANEL)
        tries_row.pack(pady=(0, 8))
        tk.Label(tries_row, text="ATTEMPTS LEFT:", font=("Segoe UI", 9),
                 fg=MUTED, bg=PANEL).pack(side="left", padx=(0, 8))
        self.tries_lbl = tk.Label(tries_row, textvariable=self.tries_left,
                                   font=("Segoe UI", 18, "bold"), fg=ACCENT2, bg=PANEL)
        self.tries_lbl.pack(side="left")

        # Progress dots
        self.dot_frame = tk.Frame(card, bg=PANEL)
        self.dot_frame.pack()

        # Input row
        input_row = tk.Frame(card, bg=PANEL)
        input_row.pack(pady=(16, 0))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Game.TEntry",
                         fieldbackground="#1A1A35", foreground=TEXT,
                         insertcolor=ACCENT2, bordercolor=ACCENT,
                         lightcolor=ACCENT, darkcolor=ACCENT,
                         font=("Segoe UI", 18))
        self.entry = ttk.Entry(input_row, width=8, style="Game.TEntry",
                                font=("Segoe UI", 18), justify="center")
        self.entry.pack(side="left", ipady=6, padx=(0, 10))
        self.entry.bind("<Return>", lambda _: self._submit_guess())
        self.entry.focus()

        self.guess_btn = GlowButton(input_row, "GUESS", self._submit_guess,
                                     color=ACCENT, width=120, height=44,
                                     bg=PANEL)
        self.guess_btn.pack(side="left")

        # History strip
        self.hist_lbl = tk.Label(card, text="", font=("Segoe UI", 9),
                                  fg=MUTED, bg=PANEL, wraplength=560)
        self.hist_lbl.pack(pady=(10, 0))

        # ── Bottom buttons ────────────────────────────────────────────────────
        btn_row = tk.Frame(self.canvas_bg, bg=BG)
        btn_row.place(x=60, y=510, width=620, height=60)

        GlowButton(btn_row, "🔄  NEW GAME", self._new_game,
                   color=SUCCESS, width=180, height=46, bg=BG).pack(side="left", padx=(0, 12))
        GlowButton(btn_row, "💡  REVEAL", self._reveal,
                   color=WARM, width=150, height=46, bg=BG).pack(side="left", padx=(0, 12))
        GlowButton(btn_row, "❌  QUIT", self.destroy,
                   color=DANGER, width=130, height=46, bg=BG).pack(side="left")

        # ── Footer ────────────────────────────────────────────────────────────
        tk.Label(self.canvas_bg, text="Press ENTER or click GUESS to submit  •  Good luck!",
                 font=("Segoe UI", 8), fg=MUTED, bg=BG).place(x=0, y=590, width=740)

    # ── GAME LOGIC ────────────────────────────────────────────────────────────

    def _new_game(self):
        cfg = self.DIFFICULTIES[self.difficulty.get()]
        low, high, tries = cfg["low"], cfg["high"], cfg["tries"]
        self.secret.set(random.randint(low, high))
        self.tries_left.set(tries)
        self.max_tries.set(tries)
        self.game_active = True
        self.guess_history = []
        self._low_bound  = low
        self._high_bound = high

        self.range_lbl.config(text=f"Guess a number between {cfg['label']}")
        self.prompt_lbl.config(text="I'm thinking of a number…  Can you find it?", fg=TEXT)
        self.hint_lbl.config(text="🤔", fg=ACCENT)
        self.hist_lbl.config(text="")
        self._update_dots()
        self.entry.config(state="normal")
        self.entry.delete(0, "end")
        self.entry.focus()

    def _submit_guess(self):
        if not self.game_active:
            self._new_game()
            return

        raw = self.entry.get().strip()
        if not raw.lstrip("-").isdigit():
            self._flash_prompt("⚠  Please enter a valid number!", DANGER)
            return

        guess = int(raw)
        cfg = self.DIFFICULTIES[self.difficulty.get()]
        low, high = cfg["low"], cfg["high"]

        if not (low <= guess <= high):
            self._flash_prompt(f"⚠  Number must be between {low} and {high}!", DANGER)
            return

        self.tries_left.set(self.tries_left.get() - 1)
        self.guess_history.append(str(guess))
        self.hist_lbl.config(text="Tried: " + "  ›  ".join(self.guess_history))
        self.entry.delete(0, "end")
        self._update_dots()

        secret = self.secret.get()

        if guess == secret:
            self._win(guess)
        elif self.tries_left.get() == 0:
            self._lose(secret)
        else:
            diff = abs(guess - secret)
            if diff == 1:
                temp = "🔥  BURNING HOT — just 1 away!"
                col  = DANGER
                arrow = "🎯" if guess < secret else "🎯"
            elif diff <= 5:
                temp = "♨️  Very warm — so close!"
                col  = WARM
                arrow = "⬆️" if guess < secret else "⬇️"
            elif diff <= 15:
                temp = "🌡  Getting warmer…"
                col  = "#F97316"
                arrow = "⬆️" if guess < secret else "⬇️"
            elif diff <= 40:
                temp = "❄️  Cool — keep searching"
                col  = ACCENT2
                arrow = "⬆️" if guess < secret else "⬇️"
            else:
                temp = "🧊  Ice cold!"
                col  = "#94A3B8"
                arrow = "⬆️" if guess < secret else "⬇️"

            direction = "Go HIGHER ↑" if guess < secret else "Go LOWER ↓"
            self.prompt_lbl.config(text=f"{temp}\n{direction}", fg=col)
            self.hint_lbl.config(text=arrow, fg=col)
            self._animate_shake()

    def _win(self, guess):
        self.game_active = False
        tries_used = self.max_tries.get() - self.tries_left.get()
        pts = max(10, 100 - tries_used * 8)
        self.score.set(self.score.get() + pts)
        self.streak.set(self.streak.get() + 1)
        self.prompt_lbl.config(
            text=f"🎉  CORRECT!  It was {guess}!\n+{pts} points  •  Used {tries_used} guess{'es' if tries_used != 1 else ''}",
            fg=SUCCESS)
        self.hint_lbl.config(text="🏆", fg=WARM)
        self.entry.config(state="disabled")
        self._animate_victory()

    def _lose(self, secret):
        self.game_active = False
        self.streak.set(0)
        self.prompt_lbl.config(
            text=f"💀  Out of guesses!\nThe number was  {secret}", fg=DANGER)
        self.hint_lbl.config(text="😱", fg=DANGER)
        self.entry.config(state="disabled")

    def _reveal(self):
        if self.game_active:
            self.prompt_lbl.config(
                text=f"🔓  The secret number is  {self.secret.get()}", fg=WARM)
            self.hint_lbl.config(text="🙈", fg=WARM)
            self.game_active = False
            self.streak.set(0)
            self.entry.config(state="disabled")

    # ── UI HELPERS ────────────────────────────────────────────────────────────

    def _update_dots(self):
        for w in self.dot_frame.winfo_children():
            w.destroy()
        total = self.max_tries.get()
        left  = self.tries_left.get()
        for i in range(total):
            if i < left:
                color = SUCCESS
            else:
                color = "#2D2D4E"
            dot = tk.Frame(self.dot_frame, bg=color, width=14, height=14)
            dot.grid(row=0, column=i, padx=2, pady=4)

    def _flash_prompt(self, msg, color):
        self.prompt_lbl.config(text=msg, fg=color)
        self.entry.delete(0, "end")

    def _animate_shake(self):
        orig_x = 60
        for i, dx in enumerate([4, -4, 3, -3, 2, -2, 0]):
            self.after(i * 25, lambda d=dx: self._shift_card(orig_x + d))

    def _shift_card(self, x):
        # find card and move it
        for widget in self.canvas_bg.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_x() in range(55, 70):
                widget.place(x=x)
                break

    def _animate_victory(self):
        colors = [WARN := WARM, SUCCESS, ACCENT2, ACCENT, WARN, SUCCESS]
        for i, c in enumerate(colors):
            self.after(i * 120, lambda col=c: self.hint_lbl.config(fg=col))


if __name__ == "__main__":
    app = NumberGuessingGame()
    app.mainloop()
