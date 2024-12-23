from flask import redirect, request, flash, url_for
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.babel import gettext
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.template import TemplateLinkRowAction
from flask_login import logout_user, login_required, current_user

from app import Admin, db, dao
from models import PhieuDatPhong, PhieuThuePhong, Phong, KhachHang, UserRole


class StaffModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN



class StaffBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN


class PhieuDatPhongView(StaffModelView):
    can_view_details = True
    edit_modal = True
    details_modal = True


    column_searchable_list = ['ten_nguoi_dat', 'ngay_dat_phong', 'ngay_tra_phong']
    column_filters = ['ten_nguoi_dat', 'ngay_dat_phong', 'ngay_tra_phong']

    column_labels = dict(tenNguoiDat='Tên người đặt', ngayDatPhong='Ngày đặt phòng', ngayTraPhong='Ngày trả phòng',
                         cacPhong='Các phòng')
    form_columns = ('ten_nguoi_dat', 'ngay_dat_phong', 'ngay_tra_phong', 'cac_chi_tiet_dat_phong')

    list_template = 'admin/phieu_dat_phong_list.html'
    column_extra_row_actions = [
        TemplateLinkRowAction('custom_row_actions.booking_row', 'Booking'),
    ]

    @expose("/booking", methods=("POST",))
    def booking(self):
        id = request.form.get('id')

        try:
            dao.phieu_dat_sang_phieu_thue(id)
        except Exception as e:
            flash(gettext(str(e)), 'error')
        else:
            flash(gettext(f"Đã chuyển phiếu đặt id: {id} thành phiếu thuê"), 'success')

        return redirect(url_for('.index_view'))


class PhieuThuePhongView(StaffModelView):
    can_view_details = True
    edit_modal = True
    details_modal = True


class PhongView(StaffModelView):
    can_view_details = True
    edit_modal = True
    details_modal = True



class KhachHangView(StaffModelView):
    can_view_details = True
    edit_modal = True
    details_modal = True


class HoaDonThanhToanView(StaffBaseView):
    def __init__(self, name, session):
        self.name = name
        self.session = session
        super(HoaDonThanhToanView, self).__init__(name=name)

    @expose('/')
    def list(self):
        data = self.session.query(PhieuThuePhong).all()
        return self.render('/admin/list_bill.html', data=data)

    @expose('/hoa-don/<id>')
    def bill(self, id):
        data = dao.xuat_hoa_don(id_phieu_thue_phong=id)
        return self.render('/admin/bill_details.html', data=data)


Admin.add_view(PhieuDatPhongView(PhieuDatPhong, db.session, name="Phiếu Đặt Phòng"))
Admin.add_view(PhieuThuePhongView(PhieuThuePhong, db.session, name="Phiếu Thuê Phòng"))
Admin.add_view(PhongView(Phong, db.session, name="Quản lý phòng"))
Admin.add_view(KhachHangView(KhachHang, db.session, name="Quản lý khách hàng"))
Admin.add_view(HoaDonThanhToanView(name="Hóa đơn", session=db.session))
