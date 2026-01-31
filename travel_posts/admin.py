from django.contrib import admin
from .models import Post, Comment, PostMedia # ⬅️ 必须导入 PostMedia

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 3

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'author')
    inlines = [PostMediaInline] # ⬅️ 这样后台就有上传图片/视频的地方了

admin.site.register(Comment)