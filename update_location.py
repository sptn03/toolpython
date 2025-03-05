import requests
import mysql.connector
import json
from typing import Dict, List
import time

class GHNApi:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://online-gateway.ghn.vn/shiip/public-api"
        self.base_url_dev = "https://dev-online-gateway.ghn.vn/shiip/public-api"
        self.headers = {
            "Content-Type": "application/json", 
            "Token": self.token
        }

    def get_provinces(self) -> List[Dict]:
        """Lấy danh sách tỉnh/thành phố"""
        # Thử đọc từ cache
        data = self.load_api_data("provinces")
        if data:
            return data
        
        # Nếu không có cache thì gọi API
        url = f"{self.base_url}/master-data/province"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()["data"]
            self.save_api_data("provinces", data)
            return data
        return []

    def get_districts(self, province_id: int) -> List[Dict]:
        """Lấy danh sách quận/huyện của tỉnh"""
        # Thử đọc từ cache
        data = self.load_api_data(f"districts_{province_id}")
        if data:
            return data
        
        url = f"{self.base_url}/master-data/district"
        params = {"province_id": province_id}
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            data = response.json()["data"]
            self.save_api_data(f"districts_{province_id}", data)
            return data
        return []

    def get_wards(self, district_id: int) -> List[Dict]:
        """Lấy danh sách phường/xã của quận/huyện"""
        # Thử đọc từ cache
        data = self.load_api_data(f"wards_{district_id}")
        if data:
            return data
        
        url = f"{self.base_url}/master-data/ward"
        params = {"district_id": district_id}
        response = requests.get(url, headers=self.headers, params=params)
        try:
            if response.status_code == 200:
                data = response.json()["data"]
                if data:
                    self.save_api_data(f"wards_{district_id}", data)
                    return data
        except Exception as e:
            print(f"Error parsing ward response: {e}")
        return []

    def save_api_data(self, key: str, data: List[Dict]):
        """Lưu data API"""
        filename = f"api_data_{key}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load_api_data(self, key: str) -> List[Dict]:
        """Đọc data API đã lưu"""
        filename = f"api_data_{key}.json"
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

class Database:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()

    def check_province_exists(self, province_id: int) -> bool:
        """Kiểm tra tỉnh đã tồn tại chưa"""
        sql = "SELECT id FROM province WHERE id = %s"
        self.cursor.execute(sql, (province_id,))
        return bool(self.cursor.fetchone())

    def check_district_exists(self, district_id: int) -> bool:
        """Kiểm tra quận/huyện đã tồn tại chưa"""
        sql = "SELECT id FROM district WHERE id = %s"
        self.cursor.execute(sql, (district_id,))
        return bool(self.cursor.fetchone())

    def check_ward_exists(self, ward_code: str) -> bool:
        """Kiểm tra phường/xã đã tồn tại chưa"""
        sql = "SELECT id FROM ward WHERE id = %s"
        self.cursor.execute(sql, (ward_code,))
        return bool(self.cursor.fetchone())

    def insert_province(self, province_id: int, name: str):
        """Thêm mới tỉnh/thành phố"""
        sql = """
            INSERT INTO province (id, name, active)
            VALUES (%s, %s, 1)
        """
        self.cursor.execute(sql, (province_id, name))
        self.conn.commit()

    def insert_district(self, district_id: int, province_id: int, name: str):
        """Thêm mới quận/huyện"""
        sql = """
            INSERT INTO district (id, province_id, name, active)
            VALUES (%s, %s, %s, 1)
        """
        self.cursor.execute(sql, (district_id, province_id, name))
        self.conn.commit()

    def insert_ward(self, ward_code: str, district_id: int, name: str):
        """Thêm mới phường/xã"""
        sql = """
            INSERT INTO ward (id, district_id, name, active)
            VALUES (%s, %s, %s, 1)
        """
        self.cursor.execute(sql, (ward_code, district_id, name))
        self.conn.commit()

    def update_province(self, province_id: int, name: str):
        """Cập nhật tỉnh/thành phố"""
        sql = """
            UPDATE province 
            SET active = 1
            WHERE id = %s AND name = %s
        """
        self.cursor.execute(sql, (province_id, name))
        self.conn.commit()

    def update_district(self, district_id: int, province_id: int, name: str):
        """Cập nhật quận/huyện"""
        sql = """
            UPDATE district
            SET active = 1 
            WHERE id = %s AND province_id = %s AND name = %s
        """
        self.cursor.execute(sql, (district_id, province_id, name))
        self.conn.commit()

    def update_ward(self, ward_code: str, district_id: int, name: str):
        """Cập nhật phường/xã"""
        sql = """
            UPDATE ward
            SET active = 1
            WHERE id = %s AND district_id = %s AND name = %s
        """
        self.cursor.execute(sql, (ward_code, district_id, name))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

def save_state(province_id: int = None, district_id: int = None):
    """Lưu trạng thái hiện tại"""
    state = {
        "last_province_id": province_id,
        "last_district_id": district_id
    }
    with open("state.json", "w") as f:
        json.dump(state, f)

def load_state() -> dict:
    """Đọc trạng thái đã lưu"""
    try:
        with open("state.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_province_id": None, "last_district_id": None}

def process_location_data(ghn: GHNApi, db: Database):
    """Xử lý dữ liệu địa chỉ"""
    try:
        state = load_state()
        provinces = ghn.get_provinces()
        print(f"Found {len(provinces)} provinces")
        time.sleep(5)

        start_found = False if state["last_province_id"] else True
        
        for province in provinces:
            if not start_found:
                if province["ProvinceID"] == state["last_province_id"]:
                    start_found = True
                else:
                    continue

            print(f"Processing province: {province['ProvinceName']}")
            
            if db.check_province_exists(province["ProvinceID"]):
                db.update_province(
                    province_id=province["ProvinceID"],
                    name=province["ProvinceName"]
                )
            else:
                db.insert_province(
                    province_id=province["ProvinceID"],
                    name=province["ProvinceName"]
                )
            
            time.sleep(2)
            districts = ghn.get_districts(province["ProvinceID"])
            print(f"Found {len(districts)} districts")

            for district in districts:
                print(f"Processing district: {district['DistrictName']}")
                
                if db.check_district_exists(district["DistrictID"]):
                    db.update_district(
                        district_id=district["DistrictID"],
                        province_id=province["ProvinceID"],
                        name=district["DistrictName"]
                    )
                else:
                    db.insert_district(
                        district_id=district["DistrictID"],
                        province_id=province["ProvinceID"],
                        name=district["DistrictName"]
                    )

                time.sleep(3)
                # Lấy và xử lý wards cho mỗi district
                wards = ghn.get_wards(district["DistrictID"])
                if wards:
                    print(f"Found {len(wards)} wards")
                    for ward in wards:
                        print(f"Processing ward: {ward['WardName']}")
                        if db.check_ward_exists(ward["WardCode"]):
                            db.update_ward(
                                ward_code=ward["WardCode"],
                                district_id=district["DistrictID"],
                                name=ward["WardName"]
                            )
                        else:
                            db.insert_ward(
                                ward_code=ward["WardCode"],
                                district_id=district["DistrictID"],
                                name=ward["WardName"]
                            )

            save_state(province["ProvinceID"], None)

    except Exception as e:
        print(f"Error processing data: {e}")

def scan_saved_json_files(ghn: GHNApi, db: Database):
    """Quét lại toàn bộ dữ liệu từ file JSON đã lưu"""
    try:
        # Quét provinces
        provinces = ghn.load_api_data("provinces")
        if provinces:
            print(f"Scanning saved provinces data: {len(provinces)} provinces")
            for province in provinces:
                print(f"Checking province: {province['ProvinceName']}")
                if db.check_province_exists(province["ProvinceID"]):
                    db.update_province(
                        province_id=province["ProvinceID"],
                        name=province["ProvinceName"]
                    )
                else:
                    db.insert_province(
                        province_id=province["ProvinceID"],
                        name=province["ProvinceName"]
                    )

                # Quét districts của province
                districts = ghn.load_api_data(f"districts_{province['ProvinceID']}")
                if districts:
                    print(f"Scanning saved districts data: {len(districts)} districts")
                    for district in districts:
                        print(f"Checking district: {district['DistrictName']}")
                        if db.check_district_exists(district["DistrictID"]):
                            db.update_district(
                                district_id=district["DistrictID"],
                                province_id=province["ProvinceID"],
                                name=district["DistrictName"]
                            )
                        else:
                            db.insert_district(
                                district_id=district["DistrictID"],
                                province_id=province["ProvinceID"],
                                name=district["DistrictName"]
                            )

                        # Quét wards của district
                        wards = ghn.load_api_data(f"wards_{district['DistrictID']}")
                        if wards:
                            print(f"Scanning saved wards data: {len(wards)} wards")
                            for ward in wards:
                                print(f"Checking ward: {ward['WardName']}")
                                if db.check_ward_exists(ward["WardCode"]):
                                    db.update_ward(
                                        ward_code=ward["WardCode"],
                                        district_id=district["DistrictID"],
                                        name=ward["WardName"]
                                    )
                                else:
                                    db.insert_ward(
                                        ward_code=ward["WardCode"],
                                        district_id=district["DistrictID"],
                                        name=ward["WardName"]
                                    )

    except Exception as e:
        print(f"Error scanning saved data: {e}")

def main():
    ghn = GHNApi("353e5111-f8d1-11ef-99a6-0684416c0dbe")
    db = Database(
        host="localhost",
        user="root",
        password="",
        database="provinte_new"
    )

    try:
        # Bước 1: Quét lại toàn bộ dữ liệu đã lưu
        print("Step 1: Scanning all saved JSON data...")
        scan_saved_json_files(ghn, db)

        # Bước 2: Tiếp tục lấy dữ liệu mới từ API
        print("\nStep 2: Continuing with new API calls...")
        process_location_data(ghn, db)

    finally:
        db.close()

if __name__ == "__main__":
    main() 