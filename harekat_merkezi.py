import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping 

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time, math, threading 
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mysql.connector
import winsound

# --- KONFİGÜRASYON ---
BAGLANTI_ADRESI = 'tcp:127.0.0.1:5762' 

class MilliMuharebeSistemi:
    def __init__(self, root):
        self.root = root
        self.root.title("MİLLİ GÜÇ 77: STRATEJİK HAREKAT MERKEZİ")
        self.root.geometry("1200x750")
        self.root.configure(bg='#020202')
        self.vehicle = None

        # --- ŞANLI ÜST PANEL ---
        header = tk.Frame(root, bg="#020202")
        header.pack(side="top", fill="x", pady=10)
        tk.Label(header, text="VAKİT TAMAM: MİLLİ BEKA VE STRATEJİK DARBE SİSTEMİ", font=("Courier", 24, "bold"), fg="#00FF41", bg="#020202").pack()
        tk.Label(header, text="AVCI-YILDIRIM ENTEGRE MUHAREBE KONSEPTİ", font=("Courier", 12), fg="#00FF41", bg="#020202").pack()

        main_frame = tk.Frame(root, bg="#020202")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # SOL PANEL: AVCI (AJAN SIZMA)
        self.avci_frm = tk.LabelFrame(main_frame, text=" AVCI V12 - AJAN SIZMA & SEAD ", fg="#00FF41", bg="#050505", font=("Courier", 12, "bold"))
        self.avci_frm.pack(side="left", fill="both", expand=True, padx=5)
        
        self.avci_log = tk.Text(self.avci_frm, height=20, width=45, bg="#000", fg="#00FF41", font=("Courier", 9))
        self.avci_log.pack(pady=10, padx=10)

        # SAĞ PANEL: YILDIRIM (HİPERSONİK)
        self.yildirim_frm = tk.LabelFrame(main_frame, text=" YILDIRIM v8 - 600KM HİPERSONİK ANALİZ (MACH 7.7) ", fg="#FF0000", bg="#050505", font=("Courier", 12, "bold"))
        self.yildirim_frm.pack(side="right", fill="both", expand=True, padx=5)

        self.fig, self.ax = plt.subplots(figsize=(5, 4), facecolor='#050505')
        self.ax.set_facecolor('#000')
        self.ax.tick_params(colors='gray')
        self.ax.set_xlabel("Menzil (KM)", color="gray"); self.ax.set_ylabel("İrtifa (KM)", color="gray")
        self.line, = self.ax.plot([], [], 'r-', lw=2)
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=self.yildirim_frm)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        threading.Thread(target=self.harekat_dongusu, daemon=True).start()

    def log_avci(self, msg):
        self.avci_log.insert(tk.END, f"> {msg}\n")
        self.avci_log.see(tk.END)

    def harekat_dongusu(self):
        try:
            self.log_avci("MİLLİ SİSTEMLER AKTİF EDİLİYOR...")
            winsound.Beep(1200, 300)
            self.vehicle = connect(BAGLANTI_ADRESI, wait_ready=True)
            
            # 1. Ajan Sızma (Alçak İrtifa)
            self.vehicle.mode = VehicleMode("GUIDED")
            self.vehicle.armed = True
            self.vehicle.simple_takeoff(5)
            while self.vehicle.location.global_relative_frame.alt < 4: time.sleep(1)

            # 2. Zikzak Sızma Manevrası
            start = self.vehicle.location.global_relative_frame
            rota = [
                LocationGlobalRelative(start.lat + 0.0006, start.lon + 0.0004, 5),
                LocationGlobalRelative(start.lat + 0.0012, start.lon - 0.0004, 5),
                LocationGlobalRelative(start.lat + 0.0018, start.lon + 0.0000, 5)
            ]

            self.log_avci("PASİF RADAR ATLATMA MODU: ZİKZAK BAŞLADI.")
            for i, nokta in enumerate(rota):
                winsound.Beep(900, 100)
                self.vehicle.simple_goto(nokta)
                while True:
                    curr = self.vehicle.location.global_relative_frame
                    d = math.sqrt((nokta.lat - curr.lat)**2 + (nokta.lon - curr.lon)**2) * 111319
                    if d < 3: break
                    time.sleep(1)

            target_name = "S-400 STRATEJİK BATARYA (600KM HEDEF)"
            self.log_avci("HEDEF TESPİT EDİLDİ. RADAR KÖR EDİLDİ.")
            for f in range(1500, 2500, 150): winsound.Beep(f, 40)
            
            # SQL Kaydı
            db = mysql.connector.connect(host="localhost", user="root", password="", database="avci_yildirim_projesi")
            cursor = db.cursor(); cursor.execute("INSERT INTO harekat_merkezi (hedef_notu, radar_durumu) VALUES (%s, 1)", (target_name,))
            db.commit(); db.close()

            # 3. YILDIRIM Gerçek Zamanlı Ateşleme
            self.yildirim_atesle()

        except Exception as e:
            self.log_avci(f"SİSTEM HATASI: {e}")

    def yildirim_atesle(self):
        v0 = 2640  # Mach 7.7
        g = 9.81; aci = np.radians(33); rho = 1.225; Cd = 0.09; A = 0.35; m = 1800
        
        # dt=2.0 -> Her adımda 2 saniyelik fizik hesaplanır
        dt = 2.0 
        x, y = 0, 0
        vx = v0 * np.cos(aci); vy = v0 * np.sin(aci); x_d, y_d = [], []

        winsound.Beep(400, 1000)
        self.log_avci("YILDIRIM: MACH 7.7 HIZIYLA 600 KM HAREKATI BAŞLADI.")
        
        start_sim = time.time()

        while y >= 0:
            v_an = math.sqrt(vx**2 + vy**2)
            current_rho = rho * math.exp(-y / 8500) 
            
            Fd = 0.5 * current_rho * (v_an**2) * Cd * A
            ax = -(Fd * (vx / v_an)) / m
            ay = -g - (Fd * (vy / v_an)) / m
            
            vx += ax * dt; vy += ay * dt; x += vx * dt; y += vy * dt
            
            if y < 0: break
            
            x_d.append(x / 1000); y_d.append(y / 1000)
            self.line.set_data(x_d, y_d); self.ax.relim(); self.ax.autoscale_view(); self.canvas_plot.draw()
            
            # Sesli takip sinyali
            if len(x_d) % 20 == 0: winsound.Beep(180, 50)

            # --- ZAMAN FRENİ (4 DAKİKA İÇİN) ---
            # Her koordinat çiziminde 1.5 saniye bekleyerek 
            # simülasyonun 15 saniyede bitmesini engelliyoruz.
            time.sleep(1.5) 

        total_m = (time.time() - start_sim) / 60
        winsound.Beep(2200, 1500)
        self.log_avci(f"DARBE BAŞARILI. HEDEF İMHA EDİLDİ.")
        self.log_avci(f"TOPLAM UÇUŞ SÜRESİ: {total_m:.2f} DAKİKA")

if __name__ == "__main__":
    root = tk.Tk(); app = MilliMuharebeSistemi(root); root.mainloop()
    