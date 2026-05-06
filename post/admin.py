from django.contrib import admin
from post.models.blood_need_mod import BloodNeedPost
from post.models.medicine_need_mod import MedicineNeedPost
from post.models.equipment_need_mod import EquipmentNeedPost
from post.models.general_post_mod import GeneralPost


@admin.register(BloodNeedPost)
class BloodNeedPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'blood_group', 'bags_needed', 'hospital_name', 'needed_date', 'urgency', 'status', 'created']
    list_filter = ['blood_group', 'urgency', 'status', 'division', 'district', 'created']
    search_fields = ['patient_name', 'hospital_name', 'contact_number', 'user__email']
    ordering = ['-created']
    readonly_fields = ['created', 'updated']


@admin.register(MedicineNeedPost)
class MedicineNeedPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'medicine_name', 'quantity', 'user', 'district', 'urgency', 'status', 'created']
    list_filter = ['urgency', 'status', 'division', 'district', 'created']
    search_fields = ['medicine_name', 'user__email', 'contact_number']
    ordering = ['-created']
    readonly_fields = ['created', 'updated']


@admin.register(EquipmentNeedPost)
class EquipmentNeedPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'equipment_name', 'quantity', 'condition', 'user', 'district', 'urgency', 'status', 'created']
    list_filter = ['condition', 'urgency', 'status', 'division', 'district', 'created']
    search_fields = ['equipment_name', 'user__email', 'contact_number']
    ordering = ['-created']
    readonly_fields = ['created', 'updated']


@admin.register(GeneralPost)
class GeneralPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'district', 'status', 'created']
    list_filter = ['status', 'division', 'district', 'created']
    search_fields = ['title', 'content', 'user__email']
    ordering = ['-created']
    readonly_fields = ['created', 'updated']
