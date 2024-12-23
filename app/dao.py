import hashlib
import math
from sqlalchemy import func, cast, text
from models import *
from app import db


# Hàm xác thực người dùng
def authenticate_user(username, password):
    return (db.session.query(User)
            .filter(User.username == username,
                    User.password == hashlib.md5(password.encode('utf-8')).hexdigest()).first())


# Lấy thông tin người dùng theo ID
def get_user_by_id(user_id):
    return db.session.query(User).filter(User.id == user_id).first()


# Hàm đặt phòng
def dat_phong(ten_nguoi_dat, ngay_dat_phong, ngay_tra_phong, cac_chi_tiet_dat_phong):
    # Lấy quy định số người tối đa trong phòng
    quy_dinh_so_nguoi_toi_da = db.session.query(QuyDinh).filter(
        QuyDinh.key == QuyDinhEnum.SO_KHACH_TOI_DA_TRONG_PHONG).first()

    if quy_dinh_so_nguoi_toi_da is None:
        raise Exception("Quy định số khách tối đa trong phòng không tồn tại.")

    so_nguoi_toi_da = quy_dinh_so_nguoi_toi_da.value  # Lấy giá trị số người tối đa

    # Kiểm tra số lượng khách trong phòng
    for ctdt in cac_chi_tiet_dat_phong:
        so_nguoi_trong_phong = len(ctdt['khach_hang'])
        if so_nguoi_trong_phong > so_nguoi_toi_da:
            raise Exception(f'Dặt quá số người tối đa ({so_nguoi_toi_da})')

    # Tạo phiếu đặt phòng
    phieu_dat_phong = PhieuDatPhong(ten_nguoi_dat=ten_nguoi_dat, ngay_dat_phong=ngay_dat_phong,
                                    ngay_tra_phong=ngay_tra_phong)
    db.session.add(phieu_dat_phong)

    # Tạo chi tiết đặt phòng cho mỗi phòng
    for ctdp in cac_chi_tiet_dat_phong:
        id_phong = ctdp['phong']
        p = db.session.query(Phong).filter(Phong.id == int(id_phong),
                                           Phong.tinh_trang == TinhTrangPhongEnum.TRONG).first()
        if p is None:
            raise Exception('Phòng không hợp lệ hoặc không còn trống.')

        chi_tiet_dat_phong = ChiTietDatPhong(id_phong=id_phong, id_phieu_dat_phong=phieu_dat_phong.id,
                                             don_gia=p.don_gia)
        db.session.add(chi_tiet_dat_phong)
        db.session.commit()

        # Thêm thông tin khách hàng
        for kh in ctdp['khach_hang']:
            khach_hang = KhachHang(ten_khach_hang=kh['ten_khach_hang'],
                                   loai_khach_hang=KhachHangEnum[kh['loai_khach_hang']],
                                   cmnd=kh['cmnd'], dia_chi=kh['dia_chi'],
                                   id_chi_tiet_dat_phong=chi_tiet_dat_phong.id)
            db.session.add(khach_hang)

        # Cập nhật tình trạng phòng
        p.tinh_trang = TinhTrangPhongEnum.DA_DAT

    db.session.commit()
    return phieu_dat_phong


# Hàm thống kê doanh thu
def stats_sale(from_date, to_date):
    stats_data = (db.session.query(Phong.loai_phong,
                                   cast(func.sum(ChiTietDatPhong.don_gia).label('doanh_thu'),
                                        Integer),
                                   func.count(ChiTietDatPhong.id_phieu_dat_phong))
                  .join(ChiTietDatPhong)
                  .join(PhieuDatPhong)
                  .group_by(Phong.loai_phong)
                  .filter(PhieuDatPhong.ngay_tra_phong.between(from_date, to_date))
                  .all())

    return [{'loai_phong': loai_phong.name, 'doanh_thu': doanh_thu, 'luot_thue': luot_thue}
            for loai_phong, doanh_thu, luot_thue in stats_data]


# Hàm thống kê mật độ
def stats_mat_do(from_date, to_date):
    stats_data = (db.session.query(Phong.ma_phong,
                                   func.sum(func.datediff(PhieuDatPhong.ngay_tra_phong,
                                                          PhieuDatPhong.ngay_dat_phong)))
                  .select_from(Phong)
                  .join(ChiTietDatPhong)
                  .join(PhieuDatPhong)
                  .group_by(Phong.ma_phong)
                  .filter(PhieuDatPhong.ngay_tra_phong.between(from_date, to_date))
                  .all())

    return [{'ma_phong': ma_phong, 'so_ngay_thue': int(so_ngay_thue)}
            for ma_phong, so_ngay_thue in stats_data]


# Chuyển phiếu đặt sang phiếu thuê
def phieu_dat_sang_phieu_thue(id_phieu_dat):
    pdp = db.session.query(PhieuDatPhong).filter(PhieuDatPhong.id == int(id_phieu_dat)).first()
    if pdp is None:
        return
    ngay_dat = pdp.ngay_dat_phong
    ngaythue = datetime.now()
    songay = (ngaythue - ngay_dat).days
    if songay > 28:
        raise Exception("Quá số ngày để thực hiện thuê phòng.")
    for ctdt in pdp.cac_chi_tiet_dat_phong:
        ctdt.phong.tinh_trang = TinhTrangPhongEnum.DANG_O

        try:
            ptp = PhieuThuePhong(id_phieu_dat_phong=pdp.id)
            db.session.add(ptp)
            db.session.commit()
        except:
            raise Exception(f"Phiếu đặt id: {id_phieu_dat} đã là phiếu thuê trước đó.")


# Lấy số khách tối đa từ quy định
def get_nguoi_toi_da():
    return db.session.query(QuyDinh).filter(QuyDinh.key == QuyDinhEnum.SO_KHACH_TOI_DA_TRONG_PHONG).first().value


# Lấy các phòng trống
def get_phong_trong():
    return db.session.query(Phong).filter(Phong.tinh_trang == TinhTrangPhongEnum.TRONG).all()


# Tính tiền phòng
def tinh_tien_phong(don_gia_phong, so_nguoi, co_khach_nuoc_ngoai):
    so_nguoi_phu_thu = db.session.query(QuyDinh).filter(QuyDinh.key == QuyDinhEnum.SO_LUONG_KHACH_PHU_THU).first()
    tien_phong = don_gia_phong

    if co_khach_nuoc_ngoai:
        he_so_phu_thu = db.session.query(QuyDinh).filter(QuyDinh.key == QuyDinhEnum.TY_LE_PHU_THU).first()
        tien_phong *= (he_so_phu_thu.value / 100)

    if so_nguoi >= so_nguoi_phu_thu.value:
        tien_phong *= 1.25

    return tien_phong


# Tính tiền của phiếu đặt
def tinh_tien_phieu_dat(cac_chi_tiet_dat_phong):
    tien_phieu_dat = 0

    for ctdp in cac_chi_tiet_dat_phong:
        id_phong = ctdp['phong']
        don_gia_phong = int(db.session.query(Phong.don_gia).filter(Phong.id == id_phong).first()[0])
        so_nguoi = len(ctdp['khach_hang'])
        co_khach_nuoc_ngoai = False
        for khach_hang in ctdp['khach_hang']:
            if KhachHangEnum[khach_hang['loai_khach_hang']] == KhachHangEnum.NUOC_NGOAI:
                co_khach_nuoc_ngoai = True

        tien_phieu_dat += tinh_tien_phong(don_gia_phong, so_nguoi, co_khach_nuoc_ngoai)

    return tien_phieu_dat


# Xuất hóa đơn từ phiếu thuê
def xuat_hoa_don(id_phieu_thue_phong):
    phieu_thue_phong = db.session.query(PhieuThuePhong).filter(PhieuThuePhong.id == id_phieu_thue_phong).first()
    bill_data = {
        'id_phieu_thue': phieu_thue_phong.id,
        'ten_nguoi_dat': phieu_thue_phong.phieu_dat_phong.ten_nguoi_dat,
        'ngay_dat_phong': phieu_thue_phong.phieu_dat_phong.ngay_dat_phong,
        'ngay_tra_phong': phieu_thue_phong.phieu_dat_phong.ngay_tra_phong
    }
    tong_tien = 0

    for ctdp in phieu_thue_phong.phieu_dat_phong.cac_chi_tiet_dat_phong:
        don_gia_phong = ctdp.phong.don_gia
        so_nguoi = len(ctdp.cac_khach_hang)
        co_khach_nuoc_ngoai = False
        for khach_hang in ctdp.cac_khach_hang:
            if khach_hang.loai_khach_hang == KhachHangEnum.NUOC_NGOAI:
                co_khach_nuoc_ngoai = True

        tong_tien += tinh_tien_phong(don_gia_phong, so_nguoi, co_khach_nuoc_ngoai)

    bill_data['tong_tien'] = tong_tien
    return bill_data
