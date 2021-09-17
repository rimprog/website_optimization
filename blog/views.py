from django.shortcuts import render
from django.db.models import Count, Prefetch

from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    tags_with_posts_count = Tag.objects.annotate(posts_count=Count('posts'))
    prefetch_tags = Prefetch('tags', queryset=tags_with_posts_count)

    most_popular_posts = Post.objects.popular()[:5] \
                                     .prefetch_related(prefetch_tags, 'author') \
                                     .fetch_with_comments_count()

    most_fresh_posts = Post.objects.order_by('-published_at')[:5] \
                                   .annotate(comments_amount=Count('comments')) \
                                   .prefetch_related(prefetch_tags, 'author')

    most_popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    tags_with_posts_count = Tag.objects.annotate(posts_count=Count('posts'))
    prefetch_tags = Prefetch('tags', queryset=tags_with_posts_count)

    popular_posts = Post.objects.popular() \
                                .prefetch_related(prefetch_tags, 'author') \
                                .fetch_with_comments_count()

    post = popular_posts.get(slug=slug)

    most_popular_posts = popular_posts[:5]

    most_popular_tags = Tag.objects.popular()[:5]

    comments = post.comments.prefetch_related('author')
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tags_with_posts_count = Tag.objects.annotate(posts_count=Count('posts'))
    prefetch_tags = Prefetch('tags', queryset=tags_with_posts_count)

    most_popular_posts = Post.objects.popular()[:5] \
                                     .prefetch_related(prefetch_tags, 'author') \
                                     .fetch_with_comments_count()

    tag = Tag.objects.get(title=tag_title)

    most_popular_tags = Tag.objects.popular()[:5]

    related_posts = tag.posts.popular()[:20] \
                             .prefetch_related(prefetch_tags, 'author') \
                             .fetch_with_comments_count()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
