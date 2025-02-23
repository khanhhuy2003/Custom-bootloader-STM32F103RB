import serial
import hashlib

def compute_sha256(filename):
    sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.digest()

def receive_sha256(serial_port):
    ser = serial.Serial(serial_port, 115200, timeout=2)

    # Receive SHA-256 from STM32
    stm32_sha256 = ser.read(32)
    ser.close()

    return stm32_sha256

def print_sha256(hash_bytes, label):
    print(f"{label} SHA256: ", " ".join(f"{b:02X}" for b in hash_bytes))

# Compute SHA-256 for firmware
firmware_sha256 = compute_sha256("UserApplication.bin")

# Receive SHA-256 from STM32
stm32_sha256 = receive_sha256("COM3")  # Change to your actual port

# Print SHA-256 values
print_sha256(firmware_sha256, "Host")
print_sha256(stm32_sha256, "STM32")

# Compare hashes
if firmware_sha256 == stm32_sha256:
    print("✅ SHA-256 MATCHED! ✅")
else:
    print("❌ SHA-256 MISMATCH! ❌")
