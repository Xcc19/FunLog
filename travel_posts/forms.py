from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # ⬅️ 删掉 'mood' 和 'weather'，只保留模型里确实存在的字段
        fields = ['title', 'content', 'location', 'lat', 'lon']