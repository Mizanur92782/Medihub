from django.db import models


class RoleChoices(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    DOCTOR = 'doctor', 'Doctor'
    REGULAR = 'regular', 'Regular'
    AMBULANCE = 'ambulance', 'Ambulance'
    PHARMACY = 'pharmacy', 'Pharmacy'
    DIAGNOSTIC = 'diagnostic', 'Diagnostic'
    BLOOD_DONOR = 'blood_donor', 'Blood Donor'
    
    

class GenderChoices(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'



class DayChoices(models.TextChoices):
    SATURDAY = 'saturday', 'Saturday'
    SUNDAY = 'sunday', 'Sunday'
    MONDAY = 'monday', 'Monday'
    TUESDAY = 'tuesday', 'Tuesday'
    WEDNESDAY = 'wednesday', 'Wednesday'
    THURSDAY = 'thursday', 'Thursday'
    FRIDAY = 'friday', 'Friday'


class BloodGroupChoices(models.TextChoices):
    A_POS = 'A+', 'A+'
    A_NEG = 'A-', 'A-'
    B_POS = 'B+', 'B+'
    B_NEG = 'B-', 'B-'
    AB_POS = 'AB+', 'AB+'
    AB_NEG = 'AB-', 'AB-'
    O_POS = 'O+', 'O+'
    O_NEG = 'O-', 'O-'


class AvailabilityChoices(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    UNAVAILABLE = 'unavailable', 'Unavailable'


class AmbulanceTypeChoices(models.TextChoices):
    BASIC = 'basic', 'Basic'
    ADVANCED = 'advanced', 'Advanced'
    ICU = 'icu', 'ICU'
    

class BlogStatusChoices(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    PUBLISHED = 'published', 'Published'


class BlogCategoryChoices(models.TextChoices):
    GENERAL = 'general', 'General'
    CARDIOLOGY = 'cardiology', 'Cardiology'
    NEUROLOGY = 'neurology', 'Neurology'
    PEDIATRICS = 'pediatrics', 'Pediatrics'
    GYNECOLOGY = 'gynecology', 'Gynecology'
    DERMATOLOGY = 'dermatology', 'Dermatology'
    ORTHOPEDICS = 'orthopedics', 'Orthopedics'
    NUTRITION = 'nutrition', 'Nutrition'
    MENTAL_HEALTH = 'mental_health', 'Mental Health'
    DIABETES = 'diabetes', 'Diabetes'
    FIRST_AID = 'first_aid', 'First Aid'
    AWARENESS = 'awareness', 'Awareness'


class BlogMediaTypeChoices(models.TextChoices):
    IMAGE = 'image', 'Image'
    VIDEO = 'video', 'Video'
    

class PostStatusChoices(models.TextChoices):
    OPEN = 'open', 'Open'
    FULFILLED = 'fulfilled', 'Fulfilled'
    CLOSED = 'closed', 'Closed'


class PostTypeChoices(models.TextChoices):
    BLOOD_NEED = 'blood_need', 'Blood Need'
    MEDICINE_NEED = 'medicine_need', 'Medicine Need'
    EQUIPMENT_NEED = 'equipment_need', 'Equipment Need'
    GENERAL = 'general', 'General'


class UrgencyChoices(models.TextChoices):
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class EquipmentConditionChoices(models.TextChoices):
    NEW = 'new', 'New'
    GOOD = 'good', 'Good'
    FAIR = 'fair', 'Fair'
    POOR = 'poor', 'Poor'
