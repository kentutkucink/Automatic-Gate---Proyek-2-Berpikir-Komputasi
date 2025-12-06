# ==========================================================
# SISTEM PARKIR OTOMATIS
# Fitur:
#  - Input kendaraan masuk
#  - Hitung biaya parkir berdasarkan jenis kendaraan & waktu
#  - Slot dipisah per jenis: motor / mobil / bus
#  - Setiap slot berisi [nama, id_tiket, waktu_masuk_menit]
# ==========================================================
from datetime import datetime, timedelta
import time
import math
import threading

# ===========================================================
# MEKANISME WAKTU

# Tanggal dan waktu awal simulasi
sim_time = datetime(2025, 1, 1, 0, 0, 0)
SIM_START = sim_time  # Referensi waktu start

lock = threading.Lock()

def run_clock():
    global sim_time
    while True:
        time.sleep(1)  # 1 detik
        with lock:
            # Setiap satu detik = 1 jam untuk simulasi
            sim_time += timedelta(minutes=5)

# Mulai Thread waktu
threading.Thread(target=run_clock, daemon=True).start()

# Konversi tahun - bulan - hari - jam - waktu menjadi menit saja
def konversiWaktuFull(dt):
    """Convert datetime to minutes since simulation start."""
    delta = dt - SIM_START
    return int(delta.total_seconds() // 60)

# ==============================================================

# Data untuk slot parkir
# Setiap elemen dalam array slot_jenis: [nama, id_tiket, waktu_masuk_dalam_menit]

slot_motor = []
slot_mobil = []
slot_bus   = []

# Ketiga array slot parkir setiap jenis kendaraan disatukan dalam 1 slot parkir
slot_parkir = [slot_motor, slot_mobil, slot_bus]

# Slot parkir setiap jenis kendaraan
kapasitas_jenis = {
    "motor": 100,
    "mobil": 100,
    "bus": 20
}

# Hitung total kapasitas
kapasitas = sum(kapasitas_jenis.values())

# Mengubah str jenis kendaraan ke indeks agar sesuai urutan
jenis_to_index = {
    "motor": 0,
    "mobil": 1,
    "bus": 2
}

nomorTiket = 0
slotTerisi = 0

# Harga maximum dan tarif masing-masing kendaraan.
maksMobil = 10000
maksMotor = 10000
tarifMobil = 2000
tarifMotor = 1000
tarifBus = 20000


def kendaraanMasuk():
    global slotTerisi, nomorTiket

    jenis = input("Masukkan jenis kendaraan (Mobil, Bus, Motor): ").strip().lower()
    while jenis not in ["motor", "mobil", "bus"]:
        jenis = input("Masukkan jenis kendaraan yang benar! (Mobil/Bus/Motor): ").strip().lower()

    idx_jenis = jenis_to_index[jenis]
    list_jenis = slot_parkir[idx_jenis]
    # Mengelompokkan jenis kendaran sesuai slotnya dengan urutan indeks

    # Cek kapasitas per jenis
    if len(list_jenis) >= kapasitas_jenis[jenis]:
        print(f"Parkiran untuk {jenis} sudah penuh!")
        return

    # Ambil waktu simulasi sebagai datetime
    with lock:
        waktuMasukDT = sim_time

    waktuMasukMenit = konversiWaktuFull(waktuMasukDT)
    
    # Input nama dan id kendaraan sesuai data untuk identifikasi
    nama = input("Masukkan nama pemilik kendaraan: ").strip()
    if nama == "":
        nama = "Tanpa Nama"
    nomorTiket += 1
    id_tiket = nomorTiket
     # Input juga bisa diubah sehingga tak perlu input manual dan bisa otomatis menggunakan qr

    # Masukkan ke list jenis
    list_jenis.append([nama, id_tiket, waktuMasukMenit])
    slotTerisi += 1

    print(f"Tiket anda bernomor: {id_tiket}. Tolong diingat!")


def kendaraanKeluar():
    global slotTerisi
    rounding_unit = 1000

    if slotTerisi <= 0:
        print("Tidak ada kendaraan dalam tempat parkir!")
        return

    with lock:
        waktuKeluarDT = sim_time
    waktuKeluar = konversiWaktuFull(waktuKeluarDT)

    try:
        id_tiket = int(input("Masukkan nomor tiket anda: "))
    except ValueError:
        print("Input tiket harus berupa angka!")
        return
    # Setiap kesalahan jenis data input (ValueError), diberi peringatan, lalu diulang

    # Cari tiket di semua slot_jenis kendaraan
    ditemukan = bool
    #bool jir :v, bisa pake false aja si sebenarnya
    jenis_ketemu = None
    data_kendaraan = None
    list_jenis_ketemu = None
    # Data kendaraan dinyatakan dalam variabel kosong
    index_di_list = -1

    for jenis, idx in jenis_to_index.items():
        list_jenis = slot_parkir[idx]
        # Verifikasi jenis kendaraan agar data diproses di array yang sesuai
        for i, data in enumerate(list_jenis):
            # Pengecekan data pada list jenis kendaraan
            if data[1] == id_tiket:
                ditemukan = True
                jenis_ketemu = jenis
                data_kendaraan = data
                list_jenis_ketemu = list_jenis
                index_di_list = i
                # Apabila ditemukan = true, tiket ada, dan data kendaraan langsung dinyatakan
                break
        if ditemukan == False:
            break

    if not ditemukan:
        print("Tiket tidak valid!")
        return

    nama, id_tiket_real, waktuMasuk = data_kendaraan

    durasiWaktu = waktuKeluar - waktuMasuk
    jam_parkir = durasiWaktu / 60.0

    # Hitung biaya parkir berdasarkan jenis kendaraan
    if jenis_ketemu == "mobil":
        biaya_awal = jam_parkir * tarifMobil
        if biaya_awal >= maksMobil:
            biaya = maksMobil
        else:
            biaya = math.ceil(biaya_awal / rounding_unit) * rounding_unit
        print(f"Kendaraan: Mobil, Pemilik: {nama}")
        print(f"Durasi parkir: {jam_parkir:.2f} jam")
        print(f"Biaya parkir anda adalah Rp{biaya}")

    elif jenis_ketemu == "motor":
        biaya_awal = jam_parkir * tarifMotor
        if biaya_awal >= maksMotor:
            biaya = maksMotor
        else:
            biaya = math.ceil(biaya_awal / rounding_unit) * rounding_unit
        print(f"Kendaraan: Motor, Pemilik: {nama}")
        print(f"Durasi parkir: {jam_parkir:.2f} jam")
        print(f"Biaya parkir anda adalah Rp{biaya}")

    elif jenis_ketemu == "bus":
        # Bus -> 20k flat
        print(f"Kendaraan: Bus, Pemilik: {nama}")
        print(f"Durasi parkir: {jam_parkir:.2f} jam")
        print(f"Biaya parkir anda adalah Rp{tarifBus}")

    # Mengeluarkan kendaraan dari list slot
    list_jenis_ketemu.pop(index_di_list)
    slotTerisi -= 1


def opsiAksi():
    # Menu utama
    while True:
        total_terisi = slotTerisi
        total_kosong = kapasitas - total_terisi

        print("---------------------------------------------")
        print(f"Total slot terisi: {total_terisi}")
        print(f"Total parkiran kosong: {total_kosong}")
        print(f"  - Motor: {kapasitas_jenis['motor'] - len(slot_motor)} kosong")
        print(f"  - Mobil: {kapasitas_jenis['mobil'] - len(slot_mobil)} kosong")
        print(f"  - Bus  : {kapasitas_jenis['bus']   - len(slot_bus)} kosong")
        print("Kendaraan Masuk   = Opsi 1")
        print("Kendaraan Keluar  = Opsi 2")
        print("Exit Program      = Opsi 3")
        print("Display Waktu     = Opsi 4")

        try:
            aksiPilihan = int(input("Pilih Opsi: "))
        except ValueError:
            print("Masukkan angka 1, 2, 3, atau 4!")
            continue
        # Untuk setiap input dengan ValueError(kesalahan jenis input), akan diperingatkan, lalu melanjutkan program

        if aksiPilihan == 1:
            kendaraanMasuk()
        elif aksiPilihan == 2:
            kendaraanKeluar()
        elif aksiPilihan == 3:
            print("Terima kasih! Program selesai.")
            break
        elif aksiPilihan == 4:
            print("Sim time:", sim_time.strftime("%Y-%m-%d %H:%M"))
            print("Minutes since start:", konversiWaktuFull(sim_time))
        else:
            print("Masukkan angka 1, 2, 3, atau 4!")

# Mulai menu saat program di-run
opsiAksi()
