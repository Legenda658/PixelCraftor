from PySide6.QtGui import QImage, QColor, QPainter
from PySide6.QtCore import Qt
import re
class XBMConverter:
    def __init__(self):
        pass
    def image_to_xbm(self, image, name="image"):
        if not isinstance(image, QImage):
            return None
        width = image.width()
        height = image.height()
        xbm_data = f"#define {name}_width {width}\n"
        xbm_data += f"#define {name}_height {height}\n"
        xbm_data += f"static unsigned char {name}_bits[] = {{\n"
        mono_image = image.convertToFormat(QImage.Format_Mono)
        bytes_data = []
        for y in range(height):
            row_bytes = []
            for x in range(0, width, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < width:
                        pixel = mono_image.pixelIndex(x + bit, y)
                        if pixel == 0:
                            byte |= (1 << bit)
                row_bytes.append(byte)
            bytes_data.extend(row_bytes)
        for i in range(0, len(bytes_data), 12):
            chunk = bytes_data[i:i+12]
            xbm_data += "  " + ", ".join(f"0x{b:02x}" for b in chunk)
            if i + 12 < len(bytes_data):
                xbm_data += ",\n"
            else:
                xbm_data += "\n"
        xbm_data += "};\n"
        return xbm_data
    def xbm_to_image(self, xbm_data):
        width_match = re.search(r'#define\s+\w+_width\s+(\d+)', xbm_data)
        height_match = re.search(r'#define\s+\w+_height\s+(\d+)', xbm_data)
        if not width_match or not height_match:
            return None
        width = int(width_match.group(1))
        height = int(height_match.group(1))
        bits_match = re.search(r'static\s+unsigned\s+char\s+\w+_bits\[\]\s*=\s*{([^}]+)}', xbm_data, re.DOTALL)
        if not bits_match:
            return None
        bits_str = bits_match.group(1)
        bytes_str = re.findall(r'0x[0-9a-fA-F]{2}', bits_str)
        bytes_data = [int(b, 16) for b in bytes_str]
        image = QImage(width, height, QImage.Format_Mono)
        image.fill(Qt.white)  
        for y in range(height):
            for x in range(width):
                byte_index = (y * ((width + 7) // 8)) + (x // 8)
                if byte_index < len(bytes_data):
                    bit_index = x % 8
                    if bytes_data[byte_index] & (1 << bit_index):
                        image.setPixel(x, y, 0)  
                    else:
                        image.setPixel(x, y, 1)  
        result = QImage(width, height, QImage.Format_ARGB32)
        result.fill(Qt.white)
        painter = QPainter(result)
        painter.drawImage(0, 0, image)
        painter.end()
        return result 