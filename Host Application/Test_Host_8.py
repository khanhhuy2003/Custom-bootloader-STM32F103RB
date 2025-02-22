import serial
import struct
import time
import binascii  # ✅ Import binascii for CRC

# Bootloader Command for Memory Write
COMMAND_BL_MEM_WRITE = 0x57

# ✅ Use STM32-Compatible CRC
def get_crc(data):
    return binascii.crc32(data) & 0xFFFFFFFF  # ✅ Matches STM32 HAL CRC

# Open Serial Port
def open_serial_port(port):
    try:
        ser = serial.Serial(port, 115200, timeout=5)
        print(f"✅ Connected to {port}")
        return ser
    except serial.SerialException:
        print("❌ Error: Could not open serial port!")
        return None

# Send Memory Write Command
def send_mem_write(ser, address, data_bytes):
    # Ensure even payload length (half-word aligned)
    if len(data_bytes) % 2 != 0:
        data_bytes += bytes([0xFF])  # Pad with 0xFF

    payload_length = len(data_bytes)

    # Construct Packet
    packet = bytearray()
    packet.append(6 + payload_length)  # Correct Length (Command + Address + Payload Len + Data)
    packet.append(COMMAND_BL_MEM_WRITE)  # Command Code

    # Append Memory Address (Little Endian)
    packet.extend(struct.pack('<I', address))

    # Append Payload Length
    packet.append(payload_length)

    # Append Data Payload
    packet.extend(data_bytes)

    # ✅ Compute Correct STM32 HAL CRC
    crc = get_crc(packet)
    packet.extend(struct.pack('<I', crc))  # Append CRC (Little Endian)

    # Send Packet
    print(f"🛠 Computed CRC: 0x{crc:08X}")  # ✅ Print CRC for debugging
    print(f"📤 Sending Packet: {[hex(x) for x in packet]}")
    ser.write(packet)
    ser.flush()

    # Wait for Response
    time.sleep(0.1)
    response = ser.read(2)  # Expecting ACK + Write Status
    print(f"📥 Received Response: {[hex(x) for x in response]}")

    # Validate Response
    if len(response) >= 2:
        if response[0] == 0xA5:  # ACK
            status = response[1]
            if status == 0x00:
                print("✅ Flash Write SUCCESS!")
            else:
                print(f"❌ Flash Write FAILED! Status Code: {hex(status)}")
        else:
            print("❌ Bootloader sent NACK (Invalid CRC or Command)")
    else:
        print("❌ No response from Bootloader. Check connection or CRC!")

# **Main Execution**
if __name__ == "__main__":
    port = input("Enter the Port Name (e.g., COM3 or /dev/ttyUSB0): ")
    ser = open_serial_port(port)

    if ser:
        # Example Address & Data
        memory_address = 0x08006000  # Example flash memory address
        test_data = bytes([0xDE, 0xAD, 0xBE, 0xEF, 0x11, 0x22, 0x33, 0x44, 0x88])  # Test Data

        # Send Memory Write Command
        send_mem_write(ser, memory_address, test_data)

        # Close Serial Port
        ser.close()
