from django.shortcuts import render, redirect
from core.models import Post, Comment, ReplyComment, FriendRequest
from userauths.models import User
from django.utils.text import slugify
from django.http import JsonResponse
from django.utils.timesince import timesince
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import shortuuid

# Create your views here.


@login_required
def index(request):
    posts = Post.objects.filter(
        active=True, visibility="Everyone").order_by("-id")
    context = {"posts": posts}
    return render(request, "core/index.html", context)


@login_required
def post_detail(request, slug):
    post = Post.objects.get(slug=slug, active=True, visibility="Everyone")
    context = {"p": post}
    return render(request, "core/post-detail.html", context)


@csrf_exempt
def create_post(request):

    if request.method == "POST":
        title = request.POST.get("post-caption")
        visibility = request.POST.get("visibility")
        image = request.FILES.get("post-thumbnail")

        uuid_key = shortuuid.uuid()
        uniqueid = uuid_key[:4]

        if title and image:
            post = Post(title=title,
                        image=image,
                        visibility=visibility,
                        user=request.user,
                        slug=slugify(title) + "_" + str(uniqueid.lower())
                        )
            post.save()
            return JsonResponse({'post': {
                "title": post.title,
                "image": post.image.url,
                "full_name": post.user.profile.full_name,
                "profile_image": post.user.profile.image.url,
                "date": timesince(post.date),
                "id": post.id
            }})
        else:
            return JsonResponse({"error": "Image or title does not exists"})

    return JsonResponse({"data": "sent"})


def like_post(request):
    id = request.GET['id']
    post = Post.objects.get(id=id)
    user = request.user
    bool = False

    if user in post.likes.all():
        post.likes.remove(user)
        bool = False
    else:
        post.likes.add(user)
        bool = True

    data = {
        "bool": bool,
        "likes": post.likes.all().count()
    }
    return JsonResponse({"data": data})


def comment_on_post(request):
    id = request.GET['id']
    comment = request.GET['comment']
    post = Post.objects.get(id=id)
    comment_count = Comment.objects.filter(post=post).count()
    user = request.user

    new_comment = Comment.objects.create(
        post=post,
        comment=comment,
        user=user
    )

    data = {
        "bool": True,
        "comment": new_comment.comment,
        "profile_image": new_comment.user.profile.image.url,
        "date": timesince(new_comment.date),
        "comment_id": new_comment.id,
        "post_id": new_comment.post.id,
        "comment_count": comment_count + int(1),
    }
    return JsonResponse({"data": data})


def like_comment(request):
    id = request.GET['id']
    comment = Comment.objects.get(id=id)
    user = request.user
    bool = False

    if user in comment.likes.all():
        comment.likes.remove(user)
        bool = False
    else:
        comment.likes.add(user)
        bool = True

    data = {
        "bool": bool,
        "likes": comment.likes.all().count()
    }

    return JsonResponse({"data": data})


def reply_comment(request):
    id = request.GET['id']
    reply = request.GET['reply']

    comment = Comment.objects.get(id=id)
    user = request.user

    new_reply = ReplyComment.objects.create(
        comment=comment,
        user=user,
        reply=reply
    )

    data = {
        "bool": True,
        "reply": new_reply.reply,
        "profile_image": new_reply.user.profile.image.url,
        "d ate": timesince(new_reply.date),
        "reply_id": new_reply.id,
        "post_id": new_reply.comment.post.id
    }
    return JsonResponse({"data": data})


def delete_comment(request):
    id = request.GET['id']
    comment = Comment.objects.get(id=id)
    comment.delete()

    data = {
        "bool": True
    }

    return JsonResponse({"data": data})


def add_friend(request):
    sender = request.user
    receiver_id = request.GET['id']
    bool = False

    if sender.id == int(receiver_id):
        JsonResponse({"error": "You cannot send a friend request to yourself"})

    receiver = User.objectsget(id=receiver_id)

    try:
        friend_request = FriendRequest.objects.get(
            sender=sender, receiver=receiver)
        if friend_request:
            friend_request.delete()
        bool = False
        return JsonResponse({"error": "Cancelled", "bool": bool})

    except FriendRequest.DoesNotExist:
        friend_request = FriendRequest(sender=sender, receiver=receiver)
        friend_request.save()
        bool = True
        return JsonResponse({"success": "Sent", "bool": bool})
