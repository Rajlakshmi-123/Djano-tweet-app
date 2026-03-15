from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from .models import Tweet, Profile, Comment
from .forms import TweetForm, CommentForm, RegisterForm, ProfileForm


# Auto-create profile for new users
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'tweets/register.html', {'form': form})


@login_required
def home_view(request):
    # Show tweets from people the user follows + own tweets
    following_users = request.user.profile.following.values_list('user', flat=True)
    tweets = Tweet.objects.filter(
        author__in=list(following_users) + [request.user]
    ).select_related('author', 'author__profile')

    form = TweetForm()
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.author = request.user
            tweet.save()
            messages.success(request, 'Tweet posted!')
            return redirect('home')

    return render(request, 'tweets/home.html', {'tweets': tweets, 'form': form})


@login_required
def tweet_detail_view(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    comments = tweet.comments.select_related('author')
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.tweet = tweet
            comment.save()
            return redirect('tweet_detail', pk=pk)

    return render(request, 'tweets/tweet_detail.html', {
        'tweet': tweet,
        'comments': comments,
        'comment_form': comment_form,
    })


@login_required
def like_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk)
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
        liked = False
    else:
        tweet.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': tweet.total_likes()})


@login_required
def delete_tweet(request, pk):
    tweet = get_object_or_404(Tweet, pk=pk, author=request.user)
    tweet.delete()
    messages.success(request, 'Tweet deleted.')
    return redirect('home')


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    tweets = Tweet.objects.filter(author=profile_user)
    is_following = False
    if request.user.is_authenticated:
        is_following = request.user.profile.following.filter(pk=profile.pk).exists()

    return render(request, 'tweets/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'tweets': tweets,
        'is_following': is_following,
    })


@login_required
def follow_toggle(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    my_profile = request.user.profile

    if my_profile.following.filter(pk=target_profile.pk).exists():
        my_profile.following.remove(target_profile)
        following = False
    else:
        my_profile.following.add(target_profile)
        following = True

    return JsonResponse({'following': following,
                         'followers_count': target_profile.followers.count()})


@login_required
def edit_profile_view(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile', username=request.user.username)
    return render(request, 'tweets/edit_profile.html', {'form': form})


def explore_view(request):
    query = request.GET.get('q', '')
    tweets = Tweet.objects.all()
    if query:
        tweets = tweets.filter(content__icontains=query)
    return render(request, 'tweets/explore.html', {'tweets': tweets, 'query': query})