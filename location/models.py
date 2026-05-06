from django.db import models



"""Division Model"""
class Division(models.Model):
  division_id = models.IntegerField(unique=True,blank=False,null=False)
  division_name_bn = models.CharField(max_length=100,blank=False,null=False)
  division_name_eng = models.CharField(max_length=100,blank=False,null=False)
  
  def __str__(self) -> str:
    return self.division_name_bn
  
  
  
  
  
"""District Model"""
class District(models.Model):
  division = models.ForeignKey(Division, on_delete=models.CASCADE)
  district_id = models.IntegerField(unique=True,blank=False,null=False)
  district_name_bn = models.CharField(max_length=100,blank=False,null=False)
  district_name_eng = models.CharField(max_length=100,blank=False,null=False)
  lattitude  = models.DecimalField(decimal_places=10,max_digits=12)
  logitude = models.DecimalField(decimal_places=10,max_digits=12) 
  
  def __str__(self) -> str:
    return self.district_name_bn
    

    
"""Upzila Model"""
class Upozila(models.Model):
  upozila = models.IntegerField(unique=True,blank=False,null=False)
  district = models.ForeignKey(District,on_delete=models.CASCADE)
  upoila_name_bn = models.CharField(max_length=100)
  upozila_name_eng = models.CharField(max_length=100)
  
  def __str__(self) -> str:
    return self.upoila_name_bn
    


"""Union Model"""
class Union(models.Model):
  union = models.IntegerField(unique=True, blank=False, null=False)
  upozila = models.ForeignKey(Upozila, on_delete=models.CASCADE)
  union_name_bn = models.CharField(max_length=100)
  union_name_eng = models.CharField(max_length=100)

  def __str__(self) -> str:
    return self.union_name_bn