#!/usr/bin/env python3
"""
gui_control_node.py  —  Interfaz gráfica de control
Topics publicados:
  /gui/num_cajas  (Int32)  — número de cajas seleccionado
  /gui/comando    (String) — "START" o "STOP"
"""
import tkinter as tk
from tkinter import ttk
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String


class GUIControlNode(Node):
    def __init__(self):
        super().__init__('gui_control_node')
        self.pub_num_cajas = self.create_publisher(Int32, '/gui/num_cajas', 10)
        self.pub_comando   = self.create_publisher(String, '/gui/comando', 10)
        self.en_marcha     = False
        self.get_logger().info('GUI Control Node iniciado')

    def publicar_num_cajas(self, n):
        self.pub_num_cajas.publish(Int32(data=n))

    def publicar_start(self):
        self.en_marcha = True
        self.pub_comando.publish(String(data='START'))
        self.get_logger().info('Comando: START')

    def publicar_stop(self):
        self.en_marcha = False
        self.pub_comando.publish(String(data='STOP'))
        self.get_logger().info('Comando: STOP')


class App:
    C_BG      = "#001A1A"   # fondo oscuro turquesa
    C_PANEL   = "#002B2B"   # paneles
    C_ACCENT  = "#00897B"   # color principal
    C_LIGHT   = "#4DB6AC"   # color claro
    C_GREEN   = "#1E8449"   # botón start 
    C_RED     = "#C0392B"   # botón stop 
    C_YELLOW  = "#D4AC0D"   # indicador espera
    C_TEXT    = "#E0F7F4"   # texto principal
    C_SUBTEXT = "#80CBC4"   # texto secundario

    def __init__(self, root, node):
        self.root = root
        self.node = node
        self.num_cajas_var = tk.IntVar(value=3)

        root.title("Sistema de Clasificación de Tapones — REC")
        root.configure(bg=self.C_BG)
        root.attributes('-fullscreen', True)
        root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

        self._build_ui()
        self._update_loop()

    def _build_ui(self):
        # ── Título ──────────────────────────────────────────────────────────────
        frm_title = tk.Frame(self.root, bg=self.C_ACCENT)
        frm_title.pack(fill="x")
        tk.Label(frm_title, text="CLASIFICACIÓN DE TAPONES",
                 font=("Arial", 28, "bold"),
                 bg=self.C_ACCENT, fg="white", pady=20).pack()
        tk.Label(frm_title, text="Panel de Control — Proyecto REC",
                 font=("Arial", 14),
                 bg=self.C_ACCENT, fg="white", pady=6).pack()

        # ── Contenedor central ──────────────────────────────────────────────────
        frm_center = tk.Frame(self.root, bg=self.C_BG)
        frm_center.pack(fill="both", expand=True, padx=80, pady=40)

        # ── Configuración ───────────────────────────────────────────────────────
        frm_config = tk.LabelFrame(frm_center,
                                   text="  CONFIGURACIÓN  ",
                                   font=("Arial", 14, "bold"),
                                   bg=self.C_PANEL, fg=self.C_TEXT,
                                   bd=2, relief="groove",
                                   padx=40, pady=30)
        frm_config.pack(fill="x", pady=(0, 30))

        tk.Label(frm_config,
                 text="Número de colores a clasificar:",
                 font=("Arial", 16),
                 bg=self.C_PANEL, fg=self.C_TEXT).pack(pady=(0, 20))

        self.spin = tk.Spinbox(frm_config,
                               from_=1, to=6,
                               textvariable=self.num_cajas_var,
                               font=("Arial", 48, "bold"),
                               width=3, justify="center",
                               bg="#0D001A", fg=self.C_TEXT,
                               buttonbackground=self.C_ACCENT,
                               relief="flat", bd=6)
        self.spin.pack(pady=(0, 20))

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Teal.Horizontal.TScale",
                        background=self.C_PANEL,
                        troughcolor="#004D40",
                        sliderlength=40,
                        sliderrelief="flat")
        self.slider = ttk.Scale(frm_config,
                                from_=1, to=6,
                                orient="horizontal",
                                variable=self.num_cajas_var,
                                style="Teal.Horizontal.TScale",
                                command=lambda v: self.num_cajas_var.set(int(float(v))))
        self.slider.pack(fill="x", pady=(0, 20))

        tk.Button(frm_config,
                  text="✔   APLICAR",
                  font=("Arial", 14, "bold"),
                  bg=self.C_ACCENT, fg="white",
                  relief="flat", cursor="hand2",
                  activebackground="#1A6B62",
                  activeforeground="white",
                  pady=12,
                  command=self._aplicar).pack(fill="x")

        # ── Start / Stop ────────────────────────────────────────────────────────
        frm_control = tk.LabelFrame(frm_center,
                                    text="  CONTROL  ",
                                    font=("Arial", 14, "bold"),
                                    bg=self.C_PANEL, fg=self.C_TEXT,
                                    bd=2, relief="groove",
                                    padx=40, pady=30)
        frm_control.pack(fill="x", pady=(0, 30))

        frm_btns = tk.Frame(frm_control, bg=self.C_PANEL)
        frm_btns.pack(fill="x")

        self.btn_start = tk.Button(frm_btns,
                                   text="▶   START",
                                   font=("Arial", 20, "bold"),
                                   bg=self.C_GREEN, fg="white",
                                   relief="flat", cursor="hand2",
                                   activebackground="#145A32",
                                   activeforeground="white",
                                   pady=20,
                                   command=self._start)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 16))

        self.btn_stop = tk.Button(frm_btns,
                                  text="■   STOP",
                                  font=("Arial", 20, "bold"),
                                  bg=self.C_RED, fg="white",
                                  relief="flat", cursor="hand2",
                                  activebackground="#78281F",
                                  activeforeground="white",
                                  pady=20,
                                  command=self._stop)
        self.btn_stop.pack(side="left", fill="x", expand=True)

        # ── Estado ──────────────────────────────────────────────────────────────
        frm_estado = tk.LabelFrame(frm_center,
                                   text="  ESTADO  ",
                                   font=("Arial", 14, "bold"),
                                   bg=self.C_PANEL, fg=self.C_TEXT,
                                   bd=2, relief="groove",
                                   padx=40, pady=20)
        frm_estado.pack(fill="x")

        def row(label):
            f = tk.Frame(frm_estado, bg=self.C_PANEL)
            f.pack(fill="x", pady=6)
            tk.Label(f, text=label,
                     font=("Arial", 14),
                     bg=self.C_PANEL, fg=self.C_SUBTEXT,
                     width=22, anchor="w").pack(side="left")
            val = tk.Label(f, text="—",
                           font=("Arial", 14, "bold"),
                           bg=self.C_PANEL, fg=self.C_TEXT,
                           anchor="w")
            val.pack(side="left")
            return val

        self.lbl_estado  = row("Estado:")
        self.lbl_ncajas  = row("Cajas configuradas:")

        # ── Indicador inferior ──────────────────────────────────────────────────
        frm_ind = tk.Frame(self.root, bg=self.C_BG)
        frm_ind.pack(fill="x", pady=10)
        self.lbl_indicator = tk.Label(frm_ind,
                                      text="● SISTEMA EN ESPERA",
                                      font=("Arial", 14, "bold"),
                                      bg=self.C_BG, fg=self.C_YELLOW)
        self.lbl_indicator.pack()

        tk.Label(frm_ind,
                 text="Pulsa ESC para salir de pantalla completa",
                 font=("Arial", 9),
                 bg=self.C_BG, fg="white").pack()

    def _aplicar(self):
        self.node.publicar_num_cajas(self.num_cajas_var.get())

    def _start(self):
        self.node.publicar_start()

    def _stop(self):
        self.node.publicar_stop()

    def _update_loop(self):
        n = self.num_cajas_var.get()
        self.lbl_ncajas.config(text=str(n))

        if self.node.en_marcha:
            self.lbl_estado.config(text="EN MARCHA", fg="#58D68D")
            self.lbl_indicator.config(text="● SISTEMA EN MARCHA", fg="#58D68D")
        else:
            self.lbl_estado.config(text="Detenido", fg=self.C_SUBTEXT)
            self.lbl_indicator.config(text="● SISTEMA EN ESPERA", fg=self.C_YELLOW)

        self.root.after(200, self._update_loop)


def ros_spin(node):
    rclpy.spin(node)


def main(args=None):
    rclpy.init(args=args)
    node = GUIControlNode()

    thread = threading.Thread(target=ros_spin, args=(node,), daemon=True)
    thread.start()

    root = tk.Tk()
    App(root, node)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
