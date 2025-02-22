import serial
import struct

COMMAND_BL_FLASH_ERASE = 0x56
COMMAND_BL_FLASH_ERASE_LEN = 8  # 1 Byte Len + 1 Byte Cmd + 1 Byte Page Number + 1 Byte Num Pages + 4 Byte CRC

def get_crc(buff, length):
    Crc = 0xFFFFFFFF
    for data in buff[0:length]:
        Crc = Crc ^ data
        for i in range(32):
            if (Crc & 0x80000000):
                Crc = (Crc << 1) ^ 0x04C11DB7
            else:
                Crc = (Crc << 1)
    return Crc & 0xFFFFFFFF  # Ensure CRC32 is 32-bit

def send_flash_erase(serial_port, page_number, num_pages):
    packet = bytearray([COMMAND_BL_FLASH_ERASE_LEN - 1, COMMAND_BL_FLASH_ERASE])
    packet.append(page_number)  # Start Page Number
    packet.append(num_pages)    # Number of Pages

    crc = get_crc(packet, len(packet))
    packet.extend(struct.pack('<I', crc))  # Append CRC in little-endian

    print(f"Sending Flash Erase Command: {[hex(x) for x in packet]}")
    serial_port.write(packet)
    serial_port.flush()

    response = serial_port.read(1)  # Read response from bootloader
    if response:
        if response[0] == 0x01:
            print("✅ Flash Erase Successful!")
        else:
            print("❌ Flash Erase Failed!")
    else:
        print("❌ No Response from Bootloader!")

# Example Usage
port = "COM3"  # Change to your serial port
ser = serial.Serial(port, 115200, timeout=5)

send_flash_erase(ser, page_number=16, num_pages=1)  # Example: Erase pages 16-17
ser.close()
