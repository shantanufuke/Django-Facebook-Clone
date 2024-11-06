from django.db import models
from userauths.models import User, Profile, user_directory_path
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
import shortuuid


VISIBILITY = (
    ("Only Me", "Only Me"),
    ("Everyone", "Everyone"),
)

FRIEND_REQUEST = (
    ("pending", "pending"),
    ("accept", "accept"),
    ("reject", "reject"),
)

NOTIFICATION_TYPE = (
    ("Friend Request", "Friend Request"),
    ("Friend Request Accepted", "Friend Request Accepted"),
    ("New Follower", "New Follower"),
    ("New Like", "New Like"),
    ("New Comment", "New Comment"),
    ("Comment Liked", "Comment Liked"),
    ("Comment Replied", "Comment Replied"),
)


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    video = models.FileField(
        upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(
        max_length=500, choices=VISIBILITY, default="Everyone")
    pid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')
    like = models.ManyToManyField(User, blank=True, related_name="likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    view = models.PositiveBigIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.user.username

    def save(self, *args, **kwargs):
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + '-' + uniqueid
        super(Post, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px;" />' % (self.image))


class Gallery(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="gallery", blank=True, null=True)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.post)

    class Meta:
        verbose_name_plural = 'Gallery'

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px" />' % (self.image))


class FriendRequest(models.Model):
    fid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver")
    status = models.CharField(
        max_length=100, default="Pending", choices=FRIEND_REQUEST)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.sender)

    class Meta:
        verbose_name_plural = 'Friend Request'


class Friend(models.Model):
    fid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user")
    friend = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="friend")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name_plural = 'Friend'


class Comment(models.Model):
    comment = models.CharField(max_length=1000)
    cid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(
        User, blank=True, related_name="comment_likes")

    def __str__(self):
        return str(self.post)

    class Meta:
        verbose_name_plural = 'Comment'


class ReplyComment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reply_user")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    reply = models.CharField(max_length=1000)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)
    cid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')

    def __str__(self):
        return str(self.comment)

    class Meta:
        verbose_name_plural = 'ReplyComment'


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="noti_user")
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="noti_sender")
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.ForeignKey(
        Comment, on_delete=models.SET_NULL, null=True, blank=True)
    notification_type = models.CharField(
        max_length=500, choices=NOTIFICATION_TYPE)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    nid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')

    def __str__(self):
        return str(self.user)

    class Meta:
        verbose_name_plural = 'Notification'


class Group(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="group_user")
    members = models.ManyToManyField(User, related_name="group_members")

    image = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    video = models.FileField(
        upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(
        max_length=500, choices=VISIBILITY, default="Everyone")
    gid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    view = models.PositiveBigIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.user.username

    def save(self, *args, **kwargs):
        print("inside save method")
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + '-' + str(uniqueid.lower())
        super(Group, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px" />' % (self.image))


class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    video = models.FileField(
        upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(
        max_length=500, choices=VISIBILITY, default="Everyone")
    pid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')
    like = models.ManyToManyField(
        User, blank=True, related_name="group_post_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    view = models.PositiveBigIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.user.username

    def save(self, *args, **kwargs):
        print("inside save method")
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + '-' + str(uniqueid.lower())
        super(GroupPost, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px" />' % (self.image))


class Page(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="page_user")
    followers = models.ManyToManyField(User, related_name="page_members")

    image = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    name = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(max_length=500, blank=True, null=True)
    video = models.FileField(
        upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(
        max_length=500, choices=VISIBILITY, default="Everyone")
    pid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    view = models.PositiveBigIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.user.username

    def save(self, *args, **kwargs):
        print("inside save method")
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.name) + '-' + str(uniqueid.lower())
        super(Page, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px" />' % (self.image))


class PagePost(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, blank=True, null=True)
    image = models.ImageField(
        upload_to=user_directory_path, blank=True, null=True)
    video = models.FileField(
        upload_to=user_directory_path, blank=True, null=True)
    visibility = models.CharField(
        max_length=500, choices=VISIBILITY, default="Everyone")
    pid = ShortUUIDField(length=7, max_length=25,
                         alphabet='abcdefghijklmnopqrstuvwxyz')
    like = models.ManyToManyField(
        User, blank=True, related_name="page_post_likes")
    active = models.BooleanField(default=True)
    slug = models.SlugField(unique=True)
    view = models.PositiveBigIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return self.user.username

    def save(self, *args, **kwargs):
        print("inside save method")
        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:2]
        if self.slug == "" or self.slug == None:
            self.slug = slugify(self.title) + '-' + str(uniqueid.lower())
        super(PagePost, self).save(*args, **kwargs)

    def thumbnail(self):
        return mark_safe('<img src="/media/%s" width="50" height="50" object-fit:"cover" style="border-radius: 5px" />' % (self.image))
