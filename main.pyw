import pyperclip
from pynput import keyboard
import pyautogui
import tkinter as tk
from tkinter import messagebox
import time
import threading
import requests
import queue
import re
import numpy as np

# --- AYARLAR ---
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_ADI = "gemini-3-flash-preview:latest"  # Ana model (F8)
TEXT_MODEL_CANDIDATES = [
    MODEL_ADI,
    "gemini-3-flash-preview:cloud",
]

KISAYOL_METIN = keyboard.Key.f8  # Metin secimi icin kisayol


# Global değişkenler
root = None
gui_queue = queue.Queue()
kisayol_basildi = False


# --- MENÜ SEÇENEKLERİ VE PROMPT'LAR ---
ISLEMLER = {
    "📈 Trend Yorumu": (
        "Aşağıdaki veriyi istatistiksel olarak analiz et ve trend yorumu yap. "
        "Verinin genel eğilimini, artış/azalış örüntülerini ve dikkat çekici noktaları belirt."
        "Cevabın kısa ve öz olsun, gereksiz açıklama ekleme."
    ),
    "🔍 Anomali Tespiti": (
        "Aşağıdaki veriyi incele ve anomalileri tespit et. "
        "Hangi değerlerin anormal olduğunu ve neden anormal sayıldığını açıkla. "
        "IQR veya standart sapma yöntemini kullanarak değerlendir."
        "Cevabın kısa ve öz olsun, gereksiz açıklama ekleme."
        
    ),
    "🎲 Yapay Veri Üret": (
        "Aşağıdaki verinin istatistiksel özelliklerine (ortalama, standart sapma, dağılım) "
        "uygun 20 adet yapay veri üret. Sadece sayıları virgülle ayırarak ver, başka açıklama ekleme."
        "Cevabın kısa ve öz olsun, gereksiz açıklama ekleme."
    ),
    "📊 CSV'ye Dönüştür": (
        "Aşağıdaki veriyi pandas kullanarak CSV formatına dönüştüren Python kodu yaz. "
        "Kodu çalıştırılabilir şekilde ver, sadece kodu yaz."
    ),
    "📚 Veri Hikayesi": (
        "Aşağıdaki veriyi bir time series olarak yorumla. Veri noktaları arasındaki ilişki hakkında yorum yap,"
        "veri noktaları arasındaki farkın sensör kalitesi gibi etkenlerden mi etkilendiği hakkında yorum yap."
        "Daha isabetli yorumlar için verilen istatistiksel verilerden yararlan"
        "Cevabın kısa ve öz olsun, gereksiz açıklamalar ekleme."
    ),
    "📝 Hipotez Önerisi": (
        "Aşağıdaki veri ve istatistikleri kullanarak veriyi anlamamıza faydalı olacak istatistiki testler öner"
        "Öneride bulunduğun test hakkında kısa ama öz bir neden sun. Nedenin kısa ve öz olsun."
    ),
    "✍ Kısa Rapor": (
        "Veriyi ve verinin istatistik bilgilerini kullanarak, teknik olmayan bir okuyucuya yönelik veri hakkında bilgi ver."
        "Cevabın kısa ve öz olsun."
    )
}


def get_available_text_model():
    """Metin işlemede kullanılabilir modeli seçer."""
    preferred_models = []
    for model in TEXT_MODEL_CANDIDATES:
        if model and model not in preferred_models:
            preferred_models.append(model)

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            return MODEL_ADI

        models = response.json().get("models", [])
        installed_lower = {m.get("name", "").lower(): m.get("name", "") for m in models}

        for candidate in preferred_models:
            candidate_lower = candidate.lower()
            if candidate_lower in installed_lower:
                return installed_lower[candidate_lower]

            candidate_base = candidate_lower.split(":")[0]
            for installed_name_lower, installed_name in installed_lower.items():
                if installed_name_lower.startswith(candidate_base + ":"):
                    return installed_name
    except Exception:
        pass

    return MODEL_ADI

def markdown_temizle(metin: str) -> str:
    metin = re.sub(r'\*\*(.*?)\*\*', r'\1', metin)  # **bold**
    metin = re.sub(r'\*(.*?)\*', r'\1', metin)       # *italic*
    metin = re.sub(r'#{1,6}\s*', '', metin)           # # Başlıklar
    metin = re.sub(r'`{1,3}(.*?)`{1,3}', r'\1', metin, flags=re.DOTALL)  # `kod`
    return metin.strip() # Gemini cevapları yazarken markdown kullanır, bunları silerek daha okunaklı yazılar oluşturulur.

def clipboard_to_data():
    # 1. Clipboard'dan veriyi al
    raw_data = pyperclip.paste()
    
    # 2. Sanitizasyon (Sadece sayıları, noktaları ve eksileri yakala)
    # Regex açıklaması: -? (negatif olabilir), \d* (rakamlar), \.? (opsiyonel ondalık), \d+ (rakamlar)
    numbers = re.findall(r'-?\d*\.?\d+', raw_data)
    
    # 3. String'den Float'a dönüştür
    data_list = [float(n) for n in numbers]
    
    # 4. Numpy Array'e çevir (İstatistiksel işler için en ideali budur)
    return np.array(data_list)

def ollama_cevap_al(prompt):
    """Ollama API'den cevap al."""
    try:
        aktif_model = get_available_text_model()
        payload = {
            "model": aktif_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            },
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()

        err_msg = (
            f"Ollama API Hatası: {response.status_code}\n"
            f"Model: {aktif_model}\n"
            f"Cevap: {response.text}"
        )
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("API Hatası", err_msg)))
        return None

    except requests.exceptions.ConnectionError:
        err_msg = (
            "Ollama'ya bağlanılamadı.\n"
            "Programın çalıştığından emin olun!\n"
            "(http://localhost:11434)"
        )
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("Bağlantı Hatası", err_msg)))
        return None
    except Exception as e:
        err_msg = f"Beklenmeyen Hata: {e}"
        print(f"❌ {err_msg}")
        gui_queue.put((messagebox.showerror, ("Hata", err_msg)))
        return None


def strip_code_fence(text):
    if not text:
        return text
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        lines = lines[1:] if lines else []
        while lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def secili_metni_kopyala(max_deneme=4):
    sentinel = f"__AI_ASISTAN__{time.time_ns()}__"
    try:
        pyperclip.copy(sentinel)
    except Exception:
        pass

    for _ in range(max_deneme):
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        metin = pyperclip.paste()
        if metin and metin.strip() and metin != sentinel:
            return metin
    return ""


def pencere_modunda_gosterilsin_mi(komut_adi):
    return True


def sonuc_penceresi_goster(baslik, icerik):
    pencere = tk.Toplevel(root)
    pencere.title(baslik)
    pencere.geometry("780x520")
    pencere.minsize(520, 320)
    pencere.attributes("-topmost", True)

    frame = tk.Frame(pencere, bg="#1f1f1f")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    text_alani = tk.Text(
        frame,
        wrap="word",
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
        font=("Segoe UI", 10),
        padx=10,
        pady=10,
    )
    kaydirma = tk.Scrollbar(frame, command=text_alani.yview)
    text_alani.configure(yscrollcommand=kaydirma.set)

    text_alani.pack(side="left", fill="both", expand=True)
    kaydirma.pack(side="right", fill="y")

    text_alani.insert("1.0", icerik)
    text_alani.config(state="disabled")

    alt_frame = tk.Frame(pencere, bg="#1f1f1f")
    alt_frame.pack(fill="x", padx=10, pady=(0, 10))

    def panoya_kopyala():
        pyperclip.copy(icerik)

    tk.Button(
        alt_frame,
        text="Panoya Kopyala",
        command=panoya_kopyala,
        bg="#3d3d3d",
        fg="white",
        activebackground="#4d4d4d",
        activeforeground="white",
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="left")

    tk.Button(
        alt_frame,
        text="Kapat",
        command=pencere.destroy,
        bg="#3d3d3d",
        fg="white",
        activebackground="#4d4d4d",
        activeforeground="white",
        relief="flat",
        padx=12,
        pady=6,
    ).pack(side="right")

    pencere.focus_force()
    pencere.lift()


def islemi_yap(komut_adi, secili_metin):

    veri = clipboard_to_data()
    ortalama = np.mean(veri)
    std = np.std(veri)
    prompt_emri = ISLEMLER[komut_adi]
    full_prompt = (
        f"{prompt_emri}\n\n"
        f"Veri: {veri.tolist()}\n"
        f"Ortalama: {ortalama:.4f}\n"
        f"Standart Sapma: {std:.4f}"
    )

    print(f"🤖 İşlem: {komut_adi}")
    print("⏳ Ollama ile işleniyor...")

    sonuc = ollama_cevap_al(full_prompt)
    if not sonuc:
        print("❌ Sonuç alınamadı.")
        return

    sonuc = strip_code_fence(sonuc)
    sonuc = markdown_temizle(sonuc)
    if sonuc.startswith("'") and sonuc.endswith("'"):
        sonuc = sonuc[1:-1]

    if pencere_modunda_gosterilsin_mi(komut_adi):
        gui_queue.put((sonuc_penceresi_goster, (komut_adi, sonuc)))
        print("âœ… SonuÃ§ ayrÄ± pencerede gÃ¶sterildi.")
        return

    time.sleep(0.2)
    pyperclip.copy(sonuc)
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "v")
    print("✅ İşlem tamamlandı!")


def process_queue():
    """Kuyruktaki GUI işlemlerini ana thread'de çalıştırır."""
    try:
        while True:
            try:
                task = gui_queue.get_nowait()
            except queue.Empty:
                break
            func, args = task
            func(*args)
    finally:
        if root:
            root.after(100, process_queue)


def menu_goster():
    """Metni kopyalar ve menüyü gösterir (ana thread)."""
    secili_metin = secili_metni_kopyala()
    if not secili_metin.strip():
        gui_queue.put(
            (
                messagebox.showwarning,
                (
                    "Secim Bulunamadi",
                    "Lutfen once metin secin, sonra F8 ile menuyu acin.",
                ),
            )
        )
        return

    menu = tk.Menu(
        root,
        tearoff=0,
        bg="#2b2b2b",
        fg="white",
        activebackground="#4a4a4a",
        activeforeground="white",
        font=("Segoe UI", 10),
    )

    def komut_olustur(k_adi, s_metin):
        def komut_calistir():
            threading.Thread(
                target=islemi_yap, args=(k_adi, s_metin), daemon=True
            ).start()

        return komut_calistir

    for baslik in ISLEMLER.keys():
        menu.add_command(label=baslik, command=komut_olustur(baslik, secili_metin))

    menu.add_separator()
    menu.add_command(label="❌ İptal", command=lambda: None)

    try:
        x, y = pyautogui.position()
        menu.tk_popup(x, y)
    finally:
        menu.grab_release()


def on_press(key):
    global kisayol_basildi
    try:
        if key == KISAYOL_METIN and not kisayol_basildi:
            kisayol_basildi = True
            gui_queue.put((menu_goster, ()))
    except AttributeError:
        pass


def on_release(key):
    global kisayol_basildi
    try:
        if key == KISAYOL_METIN:
            kisayol_basildi = False
    except AttributeError:
        pass


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI Asistan - Metin İşleme")
    print("=" * 60)
    aktif_text_model = get_available_text_model()
    print(f"📦 Metin İşleme (F8): {aktif_text_model}")
    print()
    print("🔧 Kullanım:")
    print("   F8 - Metin sec ve AI islemleri yap")
    print()
    print("⚠️ Programı kapatmak için bu pencereyi kapatın veya Ctrl+C yapın.")
    print("=" * 60)

    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if test_response.status_code == 200:
            print("✅ Ollama bağlantısı başarılı!")
        else:
            print("⚠️ Ollama'ya bağlanılamadı, servisi kontrol edin!")
    except Exception:
        print("⚠️ Ollama çalışmıyor olabilir! 'ollama serve' ile başlatın.")

    print()

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    root = tk.Tk()
    root.withdraw()
    root.after(100, process_queue)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Kapatılıyor...")
