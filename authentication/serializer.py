from rest_framework import serializers
from utilities.enum import GenderChoices
from authentication.models import User
from location.models import Division, District, Upozila, Union


class DoctorSignUPSerializer(serializers.Serializer):

  email          = serializers.EmailField()
  password       = serializers.CharField(write_only=True)
  password2      = serializers.CharField(write_only=True)

  first_name     = serializers.CharField(max_length=100)
  middle_name    = serializers.CharField(max_length=100, required=False, allow_blank=True)
  last_name      = serializers.CharField(max_length=100)
  gender         = serializers.ChoiceField(choices=GenderChoices.choices)
  contact_number = serializers.CharField(max_length=15)

  division = serializers.PrimaryKeyRelatedField(queryset=Division.objects.all())
  district = serializers.PrimaryKeyRelatedField(queryset=District.objects.none())
  upozila  = serializers.PrimaryKeyRelatedField(queryset=Upozila.objects.none())
  union    = serializers.PrimaryKeyRelatedField(queryset=Union.objects.none())

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    data = kwargs.get('data', {})

    division_id = data.get('division')
    if division_id:
      self.fields['district'].queryset = District.objects.filter(division_id=division_id)

    district_id = data.get('district')
    if district_id:
      self.fields['upozila'].queryset = Upozila.objects.filter(district_id=district_id)

    upozila_id = data.get('upozila')
    if upozila_id:
      self.fields['union'].queryset = Union.objects.filter(upozila_id=upozila_id)

  def validate(self, data):
    if data['password'] != data['password2']:
      raise serializers.ValidationError({'password': 'Passwords do not match.'})
    if User.objects.filter(email=data['email']).exists():
      raise serializers.ValidationError({'email': 'Email already in use.'})
    return data

  def to_cache(self) -> dict:
    """Returns a plain dict safe to store in cache (FK objects → int IDs)."""
    data = self.validated_data.copy()
    for field in data:
      if data.get(field):
        data[field] = data[field]
    return data
    