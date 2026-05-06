from django.contrib import admin
from blog.models.blog_post_mod import BlogPost
from blog.models.blog_media_mod import BlogMedia
from blog.models.blog_like_mod import BlogLike
from blog.models.blog_comment_mod import BlogComment, BlogCommentLike


class BlogMediaInline(admin.TabularInline):
    model = BlogMedia
    extra = 1


class BlogCommentReplyInline(admin.TabularInline):
    model = BlogComment
    fk_name = 'parent'
    extra = 0
    readonly_fields = ['user', 'content', 'like_count', 'created']
    can_delete = True
    verbose_name = 'Reply'
    verbose_name_plural = 'Replies'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'doctor', 'category', 'status', 'views', 'like_count', 'comment_count', 'created']
    list_filter = ['status', 'category', 'created']
    search_fields = ['title', 'content', 'doctor__first_name', 'doctor__last_name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'like_count', 'comment_count']
    ordering = ['-created']
    inlines = [BlogMediaInline]


@admin.register(BlogMedia)
class BlogMediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'media_type', 'caption', 'order']
    list_filter = ['media_type']
    search_fields = ['post__title', 'caption']


@admin.register(BlogLike)
class BlogLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'created']
    search_fields = ['post__title', 'user__email']
    ordering = ['-created']


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'post', 'user', 'parent', 'like_count', 'created']
    list_filter = ['created']
    search_fields = ['post__title', 'user__email', 'content']
    ordering = ['-created']
    inlines = [BlogCommentReplyInline]


@admin.register(BlogCommentLike)
class BlogCommentLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment', 'user', 'created']
    search_fields = ['user__email']
    ordering = ['-created']
