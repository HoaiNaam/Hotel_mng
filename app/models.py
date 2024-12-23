import enum
import hashlib
import random
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime, Boolean, BOOLEAN, DATETIME
from sqlalchemy.orm import relationship

from app import db, app


class UserRole(enum.Enum):
    NHAN_VIEN = 1
    QUAN_LY = 2


class QuyDinhEnum(enum.Enum):
    SO_KHACH_TOI_DA_TRONG_PHONG = "so_khach_toi_da_trong_phong"
    SO_LUONG_KHACH_PHU_THU = "so_luong_khach_phu_thu"
    TY_LE_PHU_THU = "ty_le_phu_thu"


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String(45), unique=True, nullable=True)
    password = Column(String(45), nullable=True)
    ten = Column(String(45), nullable=False)
    ho = Column(String(22), nullable=False)
    gioi_tinh = Column(BOOLEAN, nullable=False, default=False)
    ngay_sinh = Column(DATETIME, nullable=True)
    cccd = Column(String(15), nullable=False, unique=True)
    user_role = Column(Enum(UserRole), default=UserRole.QUAN_LY)


class LoaiPhongEnum(enum.Enum):
    VIP = 1
    THUONG = 2
    SIEUVIP = 3


class TinhTrangPhongEnum(enum.Enum):
    TRONG = "Trống"
    DA_DAT = "Đã đặt"
    DANG_O = "Đang ở"


class KhachHangEnum(enum.Enum):
    NOI_DIA = "Nội địa"
    NUOC_NGOAI = "Nước ngoài"


class KhachHang(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_khach_hang = Column(String(30), nullable=False)
    loai_khach_hang = Column(Enum(KhachHangEnum), nullable=False)
    cmnd = Column(String(15), nullable=False)
    dia_chi = Column(String(50), nullable=False)
    id_chi_tiet_dat_phong = Column(Integer, ForeignKey('chi_tiet_dat_phong.id'), nullable=False)


class ChiTietDatPhong(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)

    id_phieu_dat_phong = Column(Integer, ForeignKey('phieu_dat_phong.id'))
    id_phong = Column(Integer, ForeignKey('phong.id'))

    don_gia = Column(Integer, nullable=False)
    phong = relationship('Phong')
    phieu_dat_phong = relationship('PhieuDatPhong', back_populates='cac_chi_tiet_dat_phong')
    cac_khach_hang = relationship('KhachHang')


class Phong(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_phong = Column(String(10), nullable=False)
    loai_phong = Column(Enum(LoaiPhongEnum), nullable=False)
    don_gia = Column(Integer, nullable=False)
    tinh_trang = Column(Enum(TinhTrangPhongEnum), nullable=False)


class PhieuDatPhong(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_nguoi_dat = Column(String(30), nullable=False)
    ngay_dat_phong = Column(DateTime, nullable=False)
    ngay_tra_phong = Column(DateTime, nullable=False)
    cac_chi_tiet_dat_phong = relationship('ChiTietDatPhong', back_populates='phieu_dat_phong')


class PhieuThuePhong(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_phieu_dat_phong = Column(Integer, ForeignKey('phieu_dat_phong.id'), unique=True)
    phieu_dat_phong = relationship('PhieuDatPhong')


class QuyDinh(db.Model):
    key = Column(Enum(QuyDinhEnum), primary_key=True)
    value = Column(Integer, nullable=False)


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

        # KhachHang
        khachhang1 = KhachHang(ten_khach_hang="Le Thi B", loai_khach_hang=KhachHangEnum.NOI_DIA, cmnd=123456789,
                               dia_chi="Hanoi",
                               id_chi_tiet_dat_phong=1)

        # ChiTietDatPhong
        ctdp1 = ChiTietDatPhong(id_phieu_dat_phong=1, id_phong=1, don_gia=500000)

        # Phong
        phong1 = Phong(ma_phong="P001", loai_phong=LoaiPhongEnum.VIP, don_gia=1000000,
                       tinh_trang=TinhTrangPhongEnum.TRONG)

        # PhieuDatPhong
        phieudat1 = PhieuDatPhong(ten_nguoi_dat="Tran Van C", ngay_dat_phong=datetime(2024, 1, 15),
                                  ngay_tra_phong=datetime(2024, 1, 20))

        # PhieuThuePhong
        phieuthe1 = PhieuThuePhong(id_phieu_dat_phong=1)
        # KhachHang

        db.session.add_all([khachhang1, ctdp1, phong1, phieudat1, phieudat1])
        db.session.commit()
        # KhachHang
        khachhang2 = KhachHang(ten_khach_hang="Nguyen Van F", loai_khach_hang=KhachHangEnum.NOI_DIA, cmnd=987654321,
                               dia_chi="Da Nang", id_chi_tiet_dat_phong=2)

        # ChiTietDatPhong
        ctdp2 = ChiTietDatPhong(id_phieu_dat_phong=2, id_phong=2, don_gia=600000)

        # Phong
        phong2 = Phong(ma_phong="P002", loai_phong=LoaiPhongEnum.THUONG, don_gia=800000,
                       tinh_trang=TinhTrangPhongEnum.DA_DAT)

        # PhieuDatPhong
        phieudat2 = PhieuDatPhong(ten_nguoi_dat="Tran Thi D", ngay_dat_phong=datetime(2024, 2, 1),
                                  ngay_tra_phong=datetime(2024, 2, 5))

        # PhieuThuePhong
        phieuthe2 = PhieuThuePhong(id_phieu_dat_phong=2)

        # KhachHang
        khachhang3 = KhachHang(ten_khach_hang="Ho Van G", loai_khach_hang=KhachHangEnum.NOI_DIA, cmnd=112233445,
                               dia_chi="Quang Ninh", id_chi_tiet_dat_phong=3)

        # ChiTietDatPhong
        ctdp3 = ChiTietDatPhong(id_phieu_dat_phong=3, id_phong=3, don_gia=750000)

        # Phong
        phong3 = Phong(ma_phong="P003", loai_phong=LoaiPhongEnum.SIEUVIP, don_gia=1200000,
                       tinh_trang=TinhTrangPhongEnum.DANG_O)

        # PhieuDatPhong
        phieudat3 = PhieuDatPhong(ten_nguoi_dat="Nguyen Van H", ngay_dat_phong=datetime(2024, 3, 10),
                                  ngay_tra_phong=datetime(2024, 3, 15))

        # PhieuThuePhong
        phieuthe3 = PhieuThuePhong(id_phieu_dat_phong=3)

        # KhachHang
        khachhang4 = KhachHang(ten_khach_hang="Tran Thi I", loai_khach_hang=KhachHangEnum.NUOC_NGOAI, cmnd=999888777,
                               dia_chi="Hue", id_chi_tiet_dat_phong=4)

        # ChiTietDatPhong
        ctdp4 = ChiTietDatPhong(id_phieu_dat_phong=4, id_phong=1, don_gia=600000)

        # Phong
        phong4 = Phong(ma_phong="P004", loai_phong=LoaiPhongEnum.THUONG, don_gia=700000,
                       tinh_trang=TinhTrangPhongEnum.DA_DAT)

        # PhieuDatPhong
        phieudat4 = PhieuDatPhong(ten_nguoi_dat="Ho Van K", ngay_dat_phong=datetime(2024, 4, 5),
                                  ngay_tra_phong=datetime(2024, 4, 10))

        # PhieuThuePhong
        phieuthe4 = PhieuThuePhong(id_phieu_dat_phong=4)

        # KhachHang
        khachhang5 = KhachHang(ten_khach_hang="Le Van L", loai_khach_hang=KhachHangEnum.NOI_DIA, cmnd=555444333,
                               dia_chi="Sai Gon", id_chi_tiet_dat_phong=5)

        # ChiTietDatPhong
        ctdp5 = ChiTietDatPhong(id_phieu_dat_phong=5, id_phong=2, don_gia=850000)

        # Phong
        phong5 = Phong(ma_phong="P005", loai_phong=LoaiPhongEnum.VIP, don_gia=1100000,
                       tinh_trang=TinhTrangPhongEnum.TRONG)

        # PhieuDatPhong
        phieudat5 = PhieuDatPhong(ten_nguoi_dat="Pham Van M", ngay_dat_phong=datetime(2024, 5, 20),
                                  ngay_tra_phong=datetime(2024, 5, 25))

        # PhieuThuePhong
        phieuthe5 = PhieuThuePhong(id_phieu_dat_phong=5)

        # Commit to the database
        db.session.add_all([khachhang2, ctdp2, phong2, phieudat2, phieuthe2,
                            khachhang3, ctdp3, phong3, phieudat3, phieuthe3,
                            khachhang4, ctdp4, phong4, phieudat4, phieuthe4,
                            khachhang5, ctdp5, phong5, phieudat5, phieuthe5])
        db.session.commit()
        # KhachHang
        khachhang6 = KhachHang(ten_khach_hang="Phan Thi N", loai_khach_hang=KhachHangEnum.NUOC_NGOAI, cmnd=1122335566,
                               dia_chi="Vinh Long", id_chi_tiet_dat_phong=6)

        # ChiTietDatPhong
        ctdp6 = ChiTietDatPhong(id_phieu_dat_phong=6, id_phong=3, don_gia=900000)

        # Phong
        phong6 = Phong(ma_phong="P006", loai_phong=LoaiPhongEnum.SIEUVIP, don_gia=1500000,
                       tinh_trang=TinhTrangPhongEnum.TRONG)

        # PhieuDatPhong
        phieudat6 = PhieuDatPhong(ten_nguoi_dat="Huynh Van O", ngay_dat_phong=datetime(2024, 6, 5),
                                  ngay_tra_phong=datetime(2024, 6, 10))

        # PhieuThuePhong
        phieuthe6 = PhieuThuePhong(id_phieu_dat_phong=6)

        # KhachHang
        khachhang7 = KhachHang(ten_khach_hang="Tran Van P", loai_khach_hang=KhachHangEnum.NOI_DIA, cmnd=765432189,
                               dia_chi="Binh Duong", id_chi_tiet_dat_phong=7)

        # ChiTietDatPhong
        ctdp7 = ChiTietDatPhong(id_phieu_dat_phong=7, id_phong=1, don_gia=700000)

        # Phong
        phong7 = Phong(ma_phong="P007", loai_phong=LoaiPhongEnum.VIP, don_gia=1100000,
                       tinh_trang=TinhTrangPhongEnum.TRONG)

        # PhieuDatPhong
        phieudat7 = PhieuDatPhong(ten_nguoi_dat="Nguyen Thi Q", ngay_dat_phong=datetime(2024, 7, 15),
                                  ngay_tra_phong=datetime(2024, 7, 20))

        # PhieuThuePhong
        phieuthe7 = PhieuThuePhong(id_phieu_dat_phong=7)

        # Commit to the database
        db.session.add_all([khachhang6, ctdp6, phong6, phieudat6, phieuthe6,
                            khachhang7, ctdp7, phong7, phieudat7, phieuthe7])
        db.session.commit()

        admin = User(username='admin', password=hashlib.md5('123'.encode('utf-8')).hexdigest(), ten='admin', ho='admin',
                     gioi_tinh=True, cccd="123", user_role=UserRole.QUAN_LY)
        nv = User(username='nv', password=hashlib.md5('123'.encode('utf-8')).hexdigest(), ten='admin', ho='admin',
                  gioi_tinh=True, cccd="12333", user_role=UserRole.NHAN_VIEN)

        db.session.add(nv)
        db.session.add(admin)
        db.session.commit()
