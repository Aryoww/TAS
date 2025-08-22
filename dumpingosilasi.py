import serial
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- KONFIGURASI ---
# GANTI dengan port serial Arduino Anda (cek di Arduino IDE)
# Contoh di Windows: 'COM3', 'COM4', dll.
# Contoh di Linux/Mac: '/dev/ttyUSB0', '/dev/tty.usbmodem1411', dll.
SERIAL_PORT = 'COM3' 
BAUD_RATE = 115200
OUTPUT_FILENAME = 'hasil_eksperimen.csv' # Nama file untuk menyimpan data

# --- INISIALISASI ---
# Mencoba terhubung ke port serial
try:
    arduino = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=.1)
    print(f"Berhasil terhubung ke {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"Error: Tidak bisa membuka port serial {SERIAL_PORT}.")
    print("Pastikan port sudah benar dan tidak digunakan oleh program lain.")
    exit()

# List untuk menyimpan data yang masuk
data_waktu = []
data_sudut = []
data_output_pid = []

# Setup untuk plot real-time
fig, ax = plt.subplots(figsize=(12, 6))
line1, = ax.plot([], [], 'r-', label='Sudut Pendulum (°)')
line2, = ax.plot([], [], 'b-', label='Output PID')
ax.legend()
plt.title('Monitoring Rotary Pendulum Real-Time')
plt.xlabel('Waktu (detik)')
plt.ylabel('Nilai')

# Fungsi untuk inisialisasi plot
def init():
    ax.set_xlim(0, 10) # Sumbu X awal
    ax.set_ylim(-180, 180) # Sesuaikan rentang sumbu Y jika perlu
    return line1, line2,

# Fungsi yang dipanggil berulang kali untuk update grafik
def animate(i):
    try:
        # Baca data dari serial
        line_data = arduino.readline().decode('utf-8').strip()
        
        # Cek apakah data tidak kosong
        if line_data:
            # Pisahkan data berdasarkan koma
            waktu_ms, sudut, output_pid = map(float, line_data.split(','))
            
            # Konversi waktu dari ms ke detik
            waktu_s = waktu_ms / 1000.0
            
            # Tambahkan data baru ke list
            data_waktu.append(waktu_s)
            data_sudut.append(sudut)
            data_output_pid.append(output_pid)
            
            print(f"Waktu: {waktu_s:.2f} s, Sudut: {sudut:.2f}°, PID: {output_pid:.2f}")

            # Update data di grafik
            line1.set_data(data_waktu, data_sudut)
            line2.set_data(data_waktu, data_output_pid)
            
            # Atur ulang batas sumbu X agar grafik terus berjalan
            if waktu_s > ax.get_xlim()[1]:
                ax.set_xlim(waktu_s - 10, waktu_s + 2)
                ax.figure.canvas.draw()
                
            # Atur ulang batas sumbu Y secara dinamis
            ax.relim()
            ax.autoscale_view(True, True, True)

    except (ValueError, IndexError, UnicodeDecodeError) as e:
        # Abaikan jika ada data yang tidak lengkap/salah format
        print(f"Data error, dilewati: {e}")
        pass
        
    return line1, line2,

# --- EKSEKUSI ---
# Mulai animasi plot
# interval=10 berarti fungsi animate akan dipanggil setiap 10 milidetik
ani = FuncAnimation(fig, animate, init_func=init, blit=True, interval=10, save_count=50)

# Tampilkan plot
plt.show()

# --- PENYIMPANAN DATA ---
# Kode di bawah ini akan dijalankan setelah Anda menutup jendela grafik
print("\nPlot ditutup. Menyimpan data ke file...")

# Buat DataFrame menggunakan Pandas
df = pd.DataFrame({
    'Waktu (s)': data_waktu,
    'Sudut (derajat)': data_sudut,
    'Output PID': data_output_pid
})

# Simpan DataFrame ke file CSV
try:
    df.to_csv(OUTPUT_FILENAME, index=False)
    print(f"Data berhasil disimpan sebagai '{OUTPUT_FILENAME}'")
except Exception as e:
    print(f"Gagal menyimpan data: {e}")

# Tutup koneksi serial
arduino.close()
print("Koneksi serial ditutup.")