import serial
import struct
import time
import zlib
# Define Bootloader Commands
COMMAND_BL_GET_VER = 0x51
COMMAND_BL_GET_VER_LEN = 6  # 1 Byte Len + 1 Byte Cmd + 4 Byte CRC

# CRC Calculation Function
# def get_crc(buff, length):
#     Crc = 0xFFFFFFFF
#     for data in buff[0:length]:
#         Crc = Crc ^ data
#         for i in range(32):
#             if (Crc & 0x80000000):
#                 Crc = (Crc << 1) ^ 0x04C11DB7
#             else:
#                 Crc = (Crc << 1)
#     return Crc



def get_crc(buff, length):
    crc = zlib.crc32(bytearray(buff[:length])) & 0xFFFFFFFF  # Ensure 32-bit unsigned
    return crc

# Open Serial Port
def open_serial_port(port):
    try:
        ser = serial.Serial(port, 115200, timeout=5)
        print(f"Connected to {port}")
        return ser
    except serial.SerialException:
        print("Error: Could not open serial port!")
        return None

# Send Full Command Packet
def send_command(ser, command):
    # Create Command Packet
    packet = bytearray([COMMAND_BL_GET_VER_LEN - 1, command])

    # Compute CRC
    crc = get_crc(packet, len(packet))
    print(f"Computed CRC: {hex(crc)}")  # ✅ Debug output

    # Ensure CRC is a valid 32-bit unsigned integer
    crc = crc & 0xFFFFFFFF  # ✅ Fix possible negative values

    # Append CRC to the packet
    packet.extend(struct.pack('<I', crc))  # ✅ Little-endian format

    print(f"Sending Packet: {[hex(x) for x in packet]}")

    # Send Full Packet
    ser.write(packet)
    ser.flush()
    time.sleep(0.5)  # Ensure STM32 has time to process

    # Read ACK + Length
    ack = ser.read(2)
    if len(ack) == 2 and ack[0] == 0xA5:
        length_to_read = ack[1]
        response = ser.read(length_to_read)  # Read full response
        print(f"Received: {[hex(x) for x in ack + response]}")
        return response
    else:
        print("Bootloader did not acknowledge command.")
        return None


# Main Execution
if __name__ == "__main__":
    port = input("Enter the Port Name of your device (e.g., COM3 or /dev/ttyUSB0): ")
    ser = open_serial_port(port)

    if ser:
        response = send_command(ser, COMMAND_BL_GET_VER)
        if len(response) > 0:
            print("Bootloader responded correctly!")
        else:
            print("No response from Bootloader. Check CRC and transmission.")

        ser.close()
