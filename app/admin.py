from flask import redirect
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user

from app import Admin, db
from models import UserRole, QuyDinh, QuyDinhEnum


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.QUAN_LY


class AdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.QUAN_LY


class LogoutView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

    @expose('/')
    def logout(self):
        logout_user()
        return redirect('/admin/login')


class BaoCaoThangView(AdminBaseView):
    @expose('/')
    def bill(self):
        return self.render('/admin/BaoCaoThang.html')


class BaoCaoMatDoView(AdminBaseView):
    @expose('/')
    def bill(self):
        return self.render('/admin/BaoCaoMatDo.html')


class QuyDinhView(AdminModelView):
    column_display_pk = True
    edit_modal = True
    can_create = False
    can_delete = False

    column_list = ['key', 'value']
    column_labels = {
        'Key': 'Quy định',
        'value': 'Giá trị',
    }

    def get_pk_value(self, model):
        return model.key.name

    def on_model_change(self, form, model, is_created):
        if model.key == QuyDinhEnum.SO_KHACH_TOI_DA_TRONG_PHONG:
            phu_thu = db.session.query(QuyDinh).filter(QuyDinh.key == QuyDinhEnum.SO_LUONG_KHACH_PHU_THU).first()
            if not model.value >= phu_thu.value:
                raise Exception(
                    f'So luong khach toi da phai lon hon hoac bang so luong khach phu thu (>= {phu_thu.value})')
        if model.key == QuyDinhEnum.SO_LUONG_KHACH_PHU_THU:
            toi_da = db.session.query(QuyDinh).filter(QuyDinh.key == QuyDinhEnum.SO_KHACH_TOI_DA_TRONG_PHONG).first()
            if not model.value <= toi_da.value:
                raise Exception(
                    f'So luong khach phu thu phai nho hon hoac bang so luong khach toi da (<= {toi_da.value})')


Admin.add_view(BaoCaoThangView(name="Báo cáo tháng"))
Admin.add_view(BaoCaoMatDoView(name="Báo cáo mật độ"))
Admin.add_view(QuyDinhView(QuyDinh, db.session, name="Quản lý quy định"))

Admin.add_view(LogoutView(name="Đăng xuất"))
