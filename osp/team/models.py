from django.db import models
from django.dispatch import receiver
from tag.models import Tag
# from community.models import Article
from user.models import Account

# Create your models here.
class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=150)
    image = models.ImageField(default='img/team/default.jpg', upload_to='img/team/')
    create_date = models.DateTimeField()
    
    def __str__(self) -> str:
        return self.name

class TeamTag(models.Model):
    team = models.ForeignKey(Team, models.CASCADE)
    tag = models.ForeignKey(Tag, models.CASCADE)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'tag'],
                name='unique_team_tag'
            )
        ]

class TeamMember(models.Model):
    team = models.ForeignKey(Team, models.CASCADE)
    member = models.ForeignKey(Account, models.CASCADE)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f'{self.team.name} - {self.member.user.username}'
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['team', 'member'],
                name='unique_team_member'
            )
        ]



class TeamInviteMessage(models.Model):
    STATUS_CHOICES = (
        (0, '대기 중'),
        (1, '승인'),
        (2, '거절'),
    )
    DIRECTION_CHOICES = (
        (True, 'TO_ACCOUNT'),
        (False, 'TO_TEAM')
    )
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, models.CASCADE)
    account = models.ForeignKey(Account, models.CASCADE)
    message = models.TextField(max_length=200)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    direction = models.BooleanField(choices=DIRECTION_CHOICES, default=True)
    send_date = models.DateTimeField()

    # __original_mode = None
    #
    # def __init__(self, *args, **kwargs):
    #     super(Mode, self).__init__(*args, **kwargs)
    #     self.__original_mode = self.mode
    #
    # def save(self, force_insert=False, force_update=False, *args, **kwargs):
    #     if self.mode != self.__original_mode:  # then do this
    #     else:  # do that
    #         super(Mode, self).save(force_insert, force_update, *args, **kwargs)
    #     self.__original_mode = self.mode