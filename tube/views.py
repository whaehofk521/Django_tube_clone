from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Tag, Subscription
from .forms import CommentForm, PostForm
from django.contrib.auth.models import User

def tube_list(request):
    q = request.GET.get('q','')
    if q:
        posts = Post.objects.filter(title__icontains=q) | Post.objects.filter(
            content__icontains=q
        )
        return render(request, 'tube/tube_list.html', {'posts': posts, 'q': q})
    posts = Post.objects.all()
    return render(request, 'tube/tube_list.html', {'posts': posts})

def tube_detail(request, pk):
    post = Post.objects.get(pk=pk)
    form = CommentForm()
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(
            subscriber=request.user, channel=post.author
        ).exists()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            author = request.user
            message = form.cleaned_data['message']
            c = Comment.objects.create(post=post, author=author, message=message)
            c.save()
    else:
        post.view_count += 1
        post.save()
    return render(
        request,
        'tube/tube_detail.html',
        {'post': post, 'form': form, 'is_subscribed': is_subscribed},
    )

@login_required
def tube_create(request):
    if request.method == 'GET':
        form = PostForm()
        return render(request, 'tube/tube_create.html', {'form': form})
    else:
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            return redirect('tube_list')
        else:
            form = PostForm()
            return render(request, 'tube/tube_create.html', {'form': form})

@login_required
def tube_update(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return redirect('tube_list')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('tube_detail', pk)
    else:
        form = PostForm(instance=post)
        return render(request, 'tube/tube_update.html', {'form': form, 'pk': pk})

@login_required
def tube_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return redirect('tube_list')
    
    if request.method == 'POST':
        post.delete()

    return redirect('tube_list')

def tube_tag(request, tag):
    posts = Post.objects.filter(tags__name__iexact=tag)
    return render(request, 'tube/tube_list.html', {'posts': posts})

def tube_comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post
    if request.user == comment.author:
        comment.delete()
    return redirect('tube_detail', post.pk)

@login_required
def tube_subscribe(request, post_id, user_id):
    user = request.user
    channel = get_object_or_404(User, pk=user_id)

    if Subscription.objects.filter(subscriber=user, channel=channel).exists():
        return redirect('tube_detail', pk=post_id)
    
    q = Subscription.objects.create(subscriber=user, channel=channel)
    q.save()

    return redirect('tube_detail', pk=post_id)

@login_required
def tube_unsubscribe(request, post_id, user_id):
    user = request.user
    channel = get_object_or_404(User, pk=user_id)
    
    Subscription.objects.filter(subscriber=user, channel=channel).delete()
    return redirect("tube_detail", pk=post_id)