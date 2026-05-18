import logging
from notification.models.app_notification_mod import AppNotification
from core.result import ServiceResult
from firebase_admin import messaging
logger = logging.getLogger(__name__)

'''app notification -2 : Write services to creae notification'''
class AppNotificationService:
    @staticmethod
    def create_notification(user, title="Undefined", message="Undefined"):
        try:
            notification = AppNotification.objects.create(
                user=user,
                title=title,
                message=message
            )

            
            return ServiceResult(
                success=True,
                data=notification
            )

        except Exception as e:
            logger.exception("Notification creation failed")

            return ServiceResult(
                success=False,
                error=str(e)
            )
        
        
            

class PushNotification:
    '''send notification use all devices'''    
    @staticmethod
    def send_to_user(user, title, body):
        from notification.models.push_not_model import Device
        '''getting all devices of  user'''
        tokens = Device.objects.filter(user=user).values_list('token', flat=True)
        
        
        results = []
        for token in tokens:
            try:
                response = messaging.send(
                    messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    token=token,
                ))
                results.append(response)
            except Exception as e:
                logger.warning(f"Push failed for token {token[:30]}: {e}")
        return results


        
        
    "send only a devices with out user track,based on the token"
    @staticmethod
    def send_to_token(token, title, body):
        return messaging.send(messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=token,
        ))