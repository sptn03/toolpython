import json
import mysql.connector
from datetime import datetime

# Kết nối đến MySQL
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root", 
        password="",
        database="provinte"  # Tên database của bạn
    )

def write_log(message):
    print(message)
    with open(f'update_log_ssss.txt', 'a', encoding='utf-8') as f:
        f.write(message + '\n')

# Đọc file JSON
def read_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_name(name):
    """Chuẩn hóa tên để so sánh"""
    return name.lower().replace('-', ' ').replace('  ', ' ').strip()

# Cập nhật tỉnh/thành phố
def update_provinces(provinces_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    write_log("\n=== BẮT ĐẦU CẬP NHẬT TỈNH/THÀNH PHỐ ===")
    
    # Lấy danh sách tỉnh hiện có
    cursor.execute("SELECT id, name FROM province")
    existing_provinces = {normalize_name(name): id for id, name in cursor}
    write_log(f"Tổng số tỉnh trong DB: {len(existing_provinces)}")
    write_log(f"Tổng số tỉnh trong JSON: {len(provinces_data)}")
    
    # Đặt tất cả active = 0
    cursor.execute("UPDATE province SET active = 0")
    
    # Thống kê
    updated_count = 0
    not_found_count = 0
    not_found_list = []
    
    # Cập nhật từ JSON
    for province in provinces_data:
        name = province['Name']
        normalized_name = normalize_name(name)
        code = province['Code']
        write_log(f"\n>>> ĐANG XỬ LÝ TỈNH: {name} (Mã: {code})")
        
        if normalized_name in existing_provinces:
            province_id = existing_provinces[normalized_name]
            cursor.execute("""
                UPDATE province 
                SET active = 1, updated_at = %s
                WHERE id = %s
            """, (datetime.now(), province_id))
            updated_count += 1
            write_log(f"-> Cập nhật active = 1")
        else:
            not_found_count += 1
            not_found_list.append(name)
            write_log(f"-> Không tìm thấy tỉnh trong DB")
            
            # Thêm mới tỉnh - sử dụng code làm id
            cursor.execute("""
                INSERT INTO province (id, name, code, active, updated_at)
                VALUES (%s, %s, %s, 1, %s)
            """, (code, name, code, datetime.now()))
            province_id = code
            write_log(f"-> Đã thêm mới tỉnh với ID: {code}")
            conn.commit()
        
        # Cập nhật districts
        if 'District' in province:
            write_log(f"-> Tìm thấy {len(province['District'])} quận/huyện")
            update_districts(province_id, province['District'])
        else:
            write_log("-> Không có dữ liệu quận/huyện")
    
    # Thống kê kết quả
    write_log("\n=== THỐNG KÊ CẬP NHẬT TỈNH ===")
    write_log(f"Số tỉnh được cập nhật: {updated_count}")
    write_log(f"Số tỉnh được thêm mới: {not_found_count}")
    if not_found_list:
        write_log("Danh sách tỉnh thêm mới:")
        for name in not_found_list:
            write_log(f"- {name}")
    
    conn.commit()

# Cập nhật quận/huyện
def update_districts(province_id, districts_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lấy tên tỉnh
    cursor.execute("SELECT name FROM province WHERE id = %s", (province_id,))
    province_name = cursor.fetchone()[0]
    write_log(f"\n---> CẬP NHẬT QUẬN/HUYỆN CỦA {province_name}")
    
    # Lấy danh sách quận/huyện hiện có
    cursor.execute("SELECT id, name FROM district WHERE province_id = %s", (province_id,))
    existing_districts = {normalize_name(name): id for id, name in cursor}
    
    # Đặt tất cả active = 0
    cursor.execute("UPDATE district SET active = 0 WHERE province_id = %s", (province_id,))
    
    # Thống kê
    updated_count = 0
    not_found_count = 0
    not_found_list = []
    
    # Cập nhật từ JSON
    for district in districts_data:
        name = district['FullName']
        normalized_name = normalize_name(name)
        code = district['Code']
        write_log(f"\n----> Đang xử lý quận/huyện: {name} (Mã: {code})")
        
        if normalized_name in existing_districts:
            district_id = existing_districts[normalized_name]
            cursor.execute("""
                UPDATE district 
                SET active = 1, updated_at = %s
                WHERE id = %s
            """, (datetime.now(), district_id))
            updated_count += 1
            write_log(f"-----> Cập nhật active = 1")
        else:
            not_found_count += 1
            not_found_list.append(name)
            write_log(f"-----> Không tìm thấy trong DB")
            
            # Thêm mới huyện - sử dụng code làm id
            cursor.execute("""
                INSERT INTO district (id, province_id, name, code, active, updated_at)
                VALUES (%s, %s, %s, %s, 1, %s)
            """, (code, province_id, name, code, datetime.now()))
            district_id = code
            write_log(f"-----> Đã thêm mới huyện với ID: {code}")
            conn.commit()
        
        # Cập nhật wards
        wards = district.get('Ward', [])  # Lấy danh sách ward, nếu không có thì là list rỗng
        if wards:  # Kiểm tra có ward không
            write_log(f"-----> Tìm thấy {len(wards)} phường/xã")
            update_wards(district_id, name, wards)
        else:
            write_log("-----> Không có dữ liệu phường/xã")
    
    # Thống kê kết quả
    write_log(f"\n---> THỐNG KÊ CẬP NHẬT QUẬN/HUYỆN CỦA {province_name}")
    write_log(f"Số quận/huyện được cập nhật: {updated_count}")
    write_log(f"Số quận/huyện được thêm mới: {not_found_count}")
    if not_found_list:
        write_log("Danh sách quận/huyện thêm mới:")
        for name in not_found_list:
            write_log(f"- {name}")
    
    conn.commit()

# Cập nhật phường/xã
def update_wards(district_id, district_name, wards_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    write_log(f"\n------> CẬP NHẬT PHƯỜNG/XÃ CỦA {district_name}")
    
    # Lấy danh sách phường/xã hiện có và các ID đã sử dụng
    cursor.execute("SELECT id, name, district_id FROM ward")
    existing_wards = {}
    used_ids = set()
    updated_ids = set()  # Thêm set để theo dõi các ID đã được cập nhật
    
    for ward_id, name, ward_district_id in cursor:
        normalized_name = normalize_name(name)
        if normalized_name not in existing_wards:
            existing_wards[normalized_name] = []
        existing_wards[normalized_name].append((ward_id, ward_district_id))
        used_ids.add(ward_id)
    
    # Đặt tất cả active = 0 cho district hiện tại
    cursor.execute("UPDATE ward SET active = 0 WHERE district_id = %s", (district_id,))
    
    # Thống kê
    updated_count = 0
    not_found_count = 0
    not_found_list = []
    
    # Cập nhật từ JSON
    for ward in wards_data:
        name = ward['FullName']
        normalized_name = normalize_name(name)
        code = ward['Code']
        write_log(f"\n--------> Đang xử lý phường/xã: {name} (Mã: {code})")
        
        if normalized_name in existing_wards:
            # Kiểm tra xem có ward nào thuộc district_id hiện tại không
            ward_found = False
            for ward_id, ward_district_id in existing_wards[normalized_name]:
                if ward_district_id == district_id and ward_id not in updated_ids:
                    cursor.execute("""
                        UPDATE ward 
                        SET active = 1, updated_at = %s
                        WHERE id = %s AND district_id = %s
                    """, (datetime.now(), ward_id, district_id))
                    updated_count += 1
                    ward_found = True
                    updated_ids.add(ward_id)  # Đánh dấu ID đã được cập nhật
                    write_log(f"---------> Cập nhật active = 1 cho ward_id: {ward_id}")
                    break
            
            # Nếu không tìm thấy ward trong district hiện tại hoặc đã được cập nhật, thêm mới
            if not ward_found:
                not_found_count += 1
                not_found_list.append(name)
                write_log(f"---------> Không tìm thấy trong district hiện tại hoặc đã được cập nhật")
                
                # Tạo ID mới và kiểm tra cho đến khi không trùng
                new_id = code
                write_log(f"---------> Thử ID: {new_id}")
                
                # Kiểm tra xem ID đã tồn tại hoặc đã được sử dụng chưa
                if new_id in used_ids or new_id in updated_ids:
                    new_id = f"{code}111"
                    write_log(f"---------> ID đã tồn tại, thử ID mới: {new_id}")
                    
                    # Kiểm tra lại ID mới
                    while new_id in used_ids or new_id in updated_ids:
                        suffix = int(new_id[-3:]) + 1
                        new_id = f"{code}{suffix}"
                        write_log(f"---------> Thử ID mới: {new_id}")
                
                used_ids.add(new_id)
                updated_ids.add(new_id)  # Đánh dấu ID mới đã được sử dụng
                
                # Thêm mới xã với ID mới
                cursor.execute("""
                    INSERT INTO ward (id, district_id, name, active, updated_at)
                    VALUES (%s, %s, %s, 1, %s)
                """, (new_id, district_id, name, datetime.now()))
                write_log(f"---------> Đã thêm mới phường/xã với ID: {new_id}")
                conn.commit()
        else:
            not_found_count += 1
            not_found_list.append(name)
            write_log(f"---------> Không tìm thấy trong DB")
            
            # Tạo ID mới cho ward mới
            new_id = code
            if new_id in used_ids or new_id in updated_ids:
                new_id = f"{code}111"
                while new_id in used_ids or new_id in updated_ids:
                    suffix = int(new_id[-3:]) + 1
                    new_id = f"{code}{suffix}"
            
            used_ids.add(new_id)
            updated_ids.add(new_id)  # Đánh dấu ID mới đã được sử dụng
            
            # Thêm mới xã
            cursor.execute("""
                INSERT INTO ward (id, district_id, name, active, updated_at)
                VALUES (%s, %s, %s, 1, %s)
            """, (new_id, district_id, name, datetime.now()))
            write_log(f"---------> Đã thêm mới phường/xã với ID: {new_id}")
            conn.commit()
    
    # Thống kê kết quả
    write_log(f"\n------> THỐNG KÊ CẬP NHẬT PHƯỜNG/XÃ CỦA {district_name}")
    write_log(f"Số phường/xã được cập nhật: {updated_count}")
    write_log(f"Số phường/xã được thêm mới: {not_found_count}")
    if not_found_list:
        write_log("Danh sách phường/xã thêm mới:")
        for name in not_found_list:
            write_log(f"- {name}")
    
    conn.commit()

def main():
    try:
        # Đọc file JSON chứa toàn bộ dữ liệu
        write_log("Đang đọc file JSON...")
        data = read_json_file('full.json')
        
        # Cập nhật dữ liệu
        update_provinces(data)
        
        write_log("\nCập nhật dữ liệu thành công!")
    except Exception as e:
        write_log(f"\nCó lỗi xảy ra: {str(e)}")

if __name__ == "__main__":
    main()
