from PIL import Image, ImageDraw, ImageFont
import os
import random
import matplotlib.pyplot as plt

def generate_random_id(n=13):
    return ''.join([str(random.randint(0, 9)) for _ in range(n)])

def create_thai_id_card(name_th, name_en, dob, religion, address, issue_date, exp_date, id_number=None, code_number=None):
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

    # กำหนดตำแหน่งและเนื้อหาบนบัตร

    # ตราโลโก้ราชการ
    logo_box = (20, 20, 145, 145)
    draw.ellipse(logo_box, fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    draw.text((50, 70), "ตรารัฐ", font=font_thai, fill=(0, 0, 0))

    # คิวอาร์โค้ด
    qr_box = (0, 160, 90, card_height)
    draw.rectangle(qr_box, fill=(255, 255, 255))

    # chip-electronic
    chip_box = (110, 210, 260, 340)
    draw.rounded_rectangle(chip_box, radius=25, fill=(156, 155, 133), outline=(0, 0, 0), width=1)

    # หัวบัตร (ตำแหน่งบนซ้าย)
    draw.text((190, 30), f"บัตรประจำตัวประชาชน", font=font_thai_title, fill=(0, 0, 0))
    draw.text((580, 30), f"Thai National ID Card", font=font_eng_title, fill=(0, 0, 102))
    draw.text((190, 75), f"เลขประจำตัวประชาชน", font=font_thai, fill=(0, 0, 0))
    draw.text((190, 110), f"Identification Number", font=font_thai, fill=(0, 0, 102))

    # หมายเลขบัตรประชาชน (ตำแหน่งบนซ้าย)
    id_number = id_number or generate_random_id()
    draw.text((460, 80), f"{id_number[:1]} {id_number[1:5]} {id_number[5:10]} {id_number[10:12]} {id_number[12:]}", font=font_id, fill=(0, 0, 0))

    # ชื่อภาษาไทย (ตำแหน่งใต้หมายเลขบัตร)
    draw.text((120, 160), f"ชื่อตัวและชื่อสกุล", font=font_thai, fill=(0, 0, 0))
    draw.text((300, 145), f"{name_th}", font=font_thai_title, fill=(0, 0, 0))

    # ชื่อภาษาอังกฤษ (ตำแหน่งใต้ชื่อภาษาไทย)
    name_eng, sur_eng = ' '.join(name_en.split(' ')[0:2]), name_en.split(' ')[2]
    draw.text((320, 200), f"Name", font=font_eng, fill=(0, 0, 102))
    draw.text((420, 195), f"{name_eng}", font=font_eng_mid, fill=(0, 0, 102))
    draw.text((320, 245), f"Last name", font=font_eng, fill=(0, 0, 102))
    draw.text((470, 240), f"{sur_eng}", font=font_eng_mid, fill=(0, 0, 102))

    # วันเกิด (ตำแหน่งขวาของชื่อภาษาไทย)
    toEngMonth = {
        "ม.ค.": "Jan.",
        "ก.พ.": "Feb.",
        "มี.ค.": "Mar.",
        "เม.ย.": "Apr.",
        "พ.ค.": "May",
        "มิ.ย": "Jun.",
        "ก.ค.": "Jul.",
        "ส.ค.": "Aug.",
        "ก.ย.": "Sep.",
        "ต.ค.": "Oct.",
        "พ.ย.": "Nov.",
        "ธ.ค.": "Dec.",
    }
    Dth, Mth, Yth = dob.split(' ')
    dob_en = ' '.join([Dth, toEngMonth[Mth], str(int(Yth) - 543)])
    draw.text((350, 295), f"เกิดวันที่", font=font_thai, fill=(0, 0, 0))
    draw.text((460, 290), f"{dob}", font=font_thai_mid, fill=(0, 0, 0))
    draw.text((350, 335), f"Date of Birth", font=font_eng, fill=(0, 0, 102))
    draw.text((525, 330), f"{dob_en}", font=font_eng_mid, fill=(0, 0, 102))

    # ศาสนา (ตำแหน่งด้านล่างจากวันเกิด)
    draw.text((350, 370), f"ศาสนา", font=font_thai, fill=(0, 0, 0))
    draw.text((440, 370), f"{religion}", font=font_thai, fill=(0, 0, 102))

    # ที่อยู่ (ตำแหน่งด้านซ้ายล่างถัดจากศาสนา)
    draw.text((120, 410), f"ที่อยู่ {address}", font=font_thai, fill=(0, 0, 0))

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
    card.save("thai_id_card_real_size_with_positions.png")
    plt.imshow(card)

if __name__ == "__main__":
    
    # ข้อมูลตัวอย่างสำหรับสร้างบัตร
    name_th = "นาย นฤทธิ์ ใจทราม"
    name_en = "Mr. Narit Jaisarm"
    dob_th = "1 ม.ค. 2543"
    dob_en = "1 Jan. 2000"
    religion = "พุทธ"
    address = "123 หมู่ 99999 ถนนสุขสวัสดิ์ เขตคลองเตย กรุงเทพฯ"
    issue_date_th = "1 ม.ค. 2566"
    issue_date_en = "1 Jan. 2023"
    exp_date_th = "1 ม.ค. 2574"
    exp_date_en = "1 Jan. 2031"

    # สร้างบัตรประชาชน
    create_thai_id_card(name_th, name_en, dob_th, religion, address, issue_date_th, exp_date_th)
    plt.show()