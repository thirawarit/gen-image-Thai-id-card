from PIL import Image, ImageDraw, ImageFont
import os
import random
import json
import textwrap

def generate_random_id(n=13):
    """สร้างหมายเลขสุ่มสำหรับ ID หรือ Code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(n)])

def wrap_text_by_pixels(draw, text, font, max_width_px):
    """
    ตัดข้อความยาวๆ ให้ขึ้นบรรทัดใหม่โดยอ้างอิงจากความกว้างสูงสุดเป็นพิกเซล
    
    :param draw: ImageDraw object
    :param text: ข้อความที่ต้องการตัด
    :param font: ImageFont object
    :param max_width_px: ความกว้างสูงสุดของพื้นที่ที่ต้องการให้ข้อความอยู่ (หน่วยเป็นพิกเซล)
    :return: ข้อความที่ถูกตัดและใส่ \\n เรียบร้อยแล้ว
    """
    if not text:
        return ""

    words = text.split()
    if not words:
        return ""

    lines = []
    current_line = words[0]

    for word in words[1:]:
        # ทดลองต่อคำถัดไปในบรรทัดปัจจุบัน
        test_line = current_line + " " + word
        
        # วัดความกว้างของบรรทัดที่ทดลองเป็นพิกเซล
        # เราใช้ xy=(0,0) เพราะเราสนใจแค่ความกว้าง-สูง ไม่ใช่ตำแหน่ง
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]  # x1 - x0

        if line_width <= max_width_px:
            # ถ้ายังไม่เกินความกว้างสูงสุด ก็ต่อคำเข้าไปในบรรทัดปัจจุบัน
            current_line = test_line
        else:
            # ถ้าเกินแล้ว ให้บันทึกบรรทัดปัจจุบันไว้
            lines.append(current_line)
            # และเริ่มบรรทัดใหม่ด้วยคำนี้
            current_line = word

    # เพิ่มบรรทัดสุดท้ายที่เหลืออยู่เข้าไปในลิสต์
    lines.append(current_line)

    return '\n'.join(lines)

def create_thai_id_card(data, output_filename, id_number=None, code_number=None):
    """
    สร้างรูปภาพบัตรประชาชนจากข้อมูลที่ได้รับในรูปแบบ dictionary
    และบันทึกเป็นไฟล์ตามชื่อที่ระบุ
    """
    # ดึงข้อมูลจาก dictionary
    name_th = data.get("name_th", "")
    name_en = data.get("name_en", "")
    dob = data.get("dob_th", "")
    religion = data.get("religion", "")
    address = data.get("address", "")
    issue_date = data.get("issue_date_th", "")
    exp_date = data.get("exp_date_th", "")

    # สร้างพื้นหลังของบัตรประชาชน ขนาดเท่าของจริง (1011x636 พิกเซล สำหรับ 300 dpi)
    card_width, card_height = 1011, 636
    background_color = (173, 216, 230)  # สีฟ้าอ่อน
    card = Image.new('RGB', (card_width, card_height), background_color)
    draw = ImageDraw.Draw(card)

    # ฟอนต์ (จำเป็นต้องมีฟอนต์ภาษาไทยและภาษาอังกฤษในเครื่อง: ./fonts)
    try:
        font_thai_title = ImageFont.truetype("fonts/dilleniaupc-Bold.ttf", 66)  # ฟอนต์ภาษาไทย
        font_eng_title = ImageFont.truetype("fonts/dilleniaupc-Bold.ttf", 66)  # ฟอนต์ภาษาอังกฤษ
        font_thai = ImageFont.truetype("fonts/dilleniaupc-Bold.ttf", 40)  # ฟอนต์ภาษาไทย
        font_thai_mid = ImageFont.truetype("fonts/dilleniaupc-Bold.ttf", 52)  # ฟอนต์ภาษาไทย
        font_eng = ImageFont.truetype("fonts/dilleniaupc-Bold.ttf", 40)  # ฟอนต์ภาษาอังกฤษ
        font_eng_mid = ImageFont.truetype("fonts/dilleniaupc-Bold.ttf", 52)  # ฟอนต์ภาษาอังกฤษ
        font_id = ImageFont.truetype("fonts/dilleniaupc-Bold.ttf", 66)  # ฟอนต์สำหรับหมายเลขบัตร
    except IOError:
        font_thai_title = ImageFont.load_default()
        font_thai = ImageFont.load_default()
        font_eng = ImageFont.load_default()
        font_id = ImageFont.load_default()


    # ตราโลโก้ราชการ
    draw.ellipse((20, 20, 145, 145), fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    draw.text((50, 70), "ตรารัฐ", font=font_thai, fill=(0, 0, 0))

    # คิวอาร์โค้ด (พื้นที่จำลอง)
    draw.rectangle((0, 160, 90, card_height), fill=(255, 255, 255))

    # chip-electronic
    draw.rounded_rectangle((110, 210, 260, 340), radius=25, fill=(156, 155, 133), outline=(0, 0, 0), width=1)

    # หัวบัตร
    draw.text((190, 30), "บัตรประจำตัวประชาชน", font=font_thai_title, fill=(0, 0, 0))
    draw.text((580, 30), "Thai National ID Card", font=font_eng_title, fill=(0, 0, 102))
    draw.text((190, 73), "เลขประจำตัวประชาชน", font=font_thai, fill=(0, 0, 0))
    draw.text((190, 106), "Identification Number", font=font_thai, fill=(0, 0, 102))

    # หมายเลขบัตรประชาชน
    id_number = generate_random_id()
    draw.text((460, 80), f"{id_number[:1]} {id_number[1:5]} {id_number[5:10]} {id_number[10:12]} {id_number[12:]}", font=font_id, fill=(0, 0, 0))

    # ชื่อภาษาไทย
    draw.text((120, 160), "ชื่อตัวและชื่อสกุล", font=font_thai, fill=(0, 0, 0))
    draw.text((300, 148), f"{name_th}", font=font_thai_title, fill=(0, 0, 0))

    # ชื่อภาษาอังกฤษ
    try:
        name_eng_parts = name_en.split(' ')
        title_eng, first_name_eng, last_name_eng = name_eng_parts[0], name_eng_parts[1], ' '.join(name_eng_parts[2:])
        name_eng_formatted = f"{title_eng} {first_name_eng}"
    except IndexError:
        name_eng_formatted = name_en
        last_name_eng = ""
        
    draw.text((320, 200), "Name", font=font_eng, fill=(0, 0, 102))
    draw.text((420, 195), f"{name_eng_formatted}", font=font_eng_mid, fill=(0, 0, 102))
    draw.text((320, 245), "Last name", font=font_eng, fill=(0, 0, 102))
    draw.text((470, 240), f"{last_name_eng}", font=font_eng_mid, fill=(0, 0, 102))
    
    # แปลงเดือนไทยเป็นอังกฤษสำหรับวันเกิด, วันออกบัตร, วันหมดอายุ
    toEngMonth = {
        "ม.ค.": "Jan.", "ก.พ.": "Feb.", "มี.ค.": "Mar.", "เม.ย.": "Apr.",
        "พ.ค.": "May", "มิ.ย.": "Jun.", "ก.ค.": "Jul.", "ส.ค.": "Aug.",
        "ก.ย.": "Sep.", "ต.ค.": "Oct.", "พ.ย.": "Nov.", "ธ.ค.": "Dec.",
    }

    def format_date_to_eng(date_th):
        if not date_th: return ""
        try:
            d, m, y = date_th.split(' ')
            return f"{d} {toEngMonth.get(m, m)} {int(y) - 543}"
        except (ValueError, KeyError):
            return "" # หากรูปแบบวันที่ผิดพลาด

    # วันเกิด
    dob_en = format_date_to_eng(dob)
    draw.text((350, 295), "เกิดวันที่", font=font_thai, fill=(0, 0, 0))
    draw.text((460, 290), f"{dob}", font=font_thai_mid, fill=(0, 0, 0))
    draw.text((350, 335), "Date of Birth", font=font_eng, fill=(0, 0, 102))
    draw.text((525, 330), f"{dob_en}", font=font_eng_mid, fill=(0, 0, 102))

    # ศาสนา (วาดเฉพาะกรณีที่ไม่ใช่ "ไม่ระบุ")
    if religion != "ไม่ระบุ":
        # ศาสนา (ตำแหน่งด้านล่างจากวันเกิด)
        draw.text((350, 370), f"ศาสนา", font=font_thai, fill=(0, 0, 0))
        draw.text((440, 370), f"{religion}", font=font_thai, fill=(0, 0, 102))

    # ที่อยู่ (ตำแหน่งด้านซ้ายล่างถัดจากศาสนา)
    address_prefix = "ที่อยู่ "
    full_address_text = address_prefix + address
    # กำหนดความกว้างสูงสุดของพื้นที่ที่อยู่เป็นพิกเซล
    # (ตัวการ์ดกว้าง 1011px, ที่อยู่เริ่มที่ x=120, รูปถ่ายเริ่มที่ x=760 -> พื้นที่ว่าง ~640px)
    max_pixel_width = 580  # กำหนดน้อยกว่าพื้นที่จริงเล็กน้อยเพื่อความสวยงาม

    # เรียกใช้ฟังก์ชันใหม่ที่เราสร้างขึ้น
    wrapped_address = wrap_text_by_pixels(draw, full_address_text, font_thai, max_pixel_width)

    # วาดข้อความที่ตัดแล้วลงบนการ์ด
    draw.multiline_text((120, 410), wrapped_address, font=font_thai, fill=(0, 0, 0), spacing=25)

    # วันที่ออกบัตร (ตำแหน่งใกล้ล่างซ้าย)
    Dth, Mth, Yth = issue_date.split(' ')
    issue_date_en = ' '.join([Dth, toEngMonth[Mth], str(int(Yth) - 543)])
    draw.text((120, 500), f"{issue_date}", font=font_thai, fill=(0, 0, 0))
    draw.text((120, 535), f"วันออกบัตร", font=font_thai, fill=(0, 0, 0))
    draw.text((120, 570), f"{issue_date_en}", font=font_thai, fill=(0, 0, 102))
    draw.text((120, 600), f"Date of Issue", font=font_thai, fill=(0, 0, 102))

    # วันหมดอายุ (ตำแหน่งล่างขวาของรูปภาพ)
    Dth, Mth, Yth = exp_date.split(' ')
    exp_date_en = ' '.join([Dth, toEngMonth[Mth], str(int(Yth) - 543)])
    draw.text((560, 500), f"{exp_date}", font=font_thai, fill=(0, 0, 0))
    draw.text((560, 535), f"วันบัตรหมดอายุ", font=font_thai, fill=(0, 0, 0))
    draw.text((560, 570), f"{exp_date_en}", font=font_thai, fill=(0, 0, 102))
    draw.text((560, 600), f"Date of Expiry", font=font_thai, fill=(0, 0, 102))

    # เพิ่มพื้นที่สำหรับภาพถ่ายบุคคล (ตำแหน่งขวาล่าง)
    photo_box = (760, 300, 980, 580)
    draw.rectangle(photo_box, fill=(255, 255, 255))
    code_number = code_number or generate_random_id(n=14)
    draw.text((830, 440), "รูปถ่าย", font=font_thai, fill=(0, 0, 0))
    draw.text((760, 585), f"{code_number[:4]}-{code_number[4:6]}-{code_number[6:14]}", font=font_thai, fill=(0, 0, 0))

    # บันทึกภาพบัตรประชาชน
    card.save(output_filename)



if __name__ == "__main__":
    
    jsonl_file = "data.jsonl"
    output_dir = "output_cards_with_textwrapping"

    # สร้างโฟลเดอร์สำหรับเก็บผลลัพธ์หากยังไม่มี
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # ตรวจสอบว่ามีไฟล์ข้อมูลหรือไม่
    if not os.path.exists(jsonl_file):
        print(f"ไม่พบไฟล์ {jsonl_file}. กรุณาสร้างไฟล์และใส่ข้อมูลลงไป")
    else:
        # อ่านไฟล์ JSONL และสร้างบัตรสำหรับแต่ละรายการ
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                try:
                    # แปลง JSON string เป็น dictionary
                    data = json.loads(line.strip())
                    
                    # กำหนดชื่อไฟล์ผลลัพธ์
                    output_filename = os.path.join(output_dir, f"thai_id_card_{i}.png")
                    
                    # เรียกใช้ฟังก์ชันสร้างบัตร
                    create_thai_id_card(data, output_filename)

                except json.JSONDecodeError:
                    print(f"ข้ามบรรทัดที่ {i+1} เนื่องจากข้อมูลไม่ใช่รูปแบบ JSON ที่ถูกต้อง")
                except Exception as e:
                    print(f"เกิดข้อผิดพลาดในการประมวลผลบรรทัดที่ {i+1}: {e}")