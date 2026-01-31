import re
import json
from collections import Counter
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Count
from .models import Post, PostMedia, Comment
from .forms import PostForm

def extract_city_tags(text_list):
    """
    强化版自动分析函数：精准过滤废词，去重统计
    """
    # 1. 合并文本并统一转小写
    full_text = " ".join(text_list).lower()
    
    # 2. 匹配中文字符或 2 位以上的纯英文单词（过滤掉 i, a 等单字）
    words = re.findall(r'[\u4e00-\u9fa5]+|[a-z]{2,}', full_text)
    
    # 3. 终极黑名单：把所有讨厌的虚词都放这里
    stop_words = {
        # 英文废词
        'for', 'and', 'the', 'with', 'this', 'that', 'from', 'you', 'your', 'was', 'were',
        'are', 'not', 'have', 'has', 'but', 'all', 'out', 'can', 'about', 'just', 'get',
        'on','in','the','of','as','is','or','day','to','bund','it','its','at','because','if','am',
        
        # 中文废词
        '这个', '那个', '感觉', '觉得', '去了', '可以', '非常', '真的', '一个', '今天', 
        '地方', '很多', '这种', '这里', '那里', '还是', '就是', '因为', '所以', '虽然', 
        '但是', '已经', '比较', '觉得', '发现', '看到', '东西', '哈哈', '有点'
    }
    
    # 4. 过滤：不在黑名单中、不是纯数字、长度达标
    filtered_words = [
        w for w in words 
        if w not in stop_words and not w.isdigit()
    ]
    
    # 5. 统计词频并取前 4 名
    most_common = Counter(filtered_words).most_common(4)
    
    # 只返回词，不返回次数
    return [word for word, count in most_common]

def index(request):
    # 获取所有帖子，按时间倒序
    posts = Post.objects.all().order_by('-created_at')
    
    # 获取热门城市统计
    hot_cities_query = Post.objects.values('location').annotate(
        count=Count('location')
    ).order_by('-count')[:5]

    hot_locations = []
    for item in hot_cities_query:
        city_name = item['location']
        # 查找该城市下所有帖子的文本内容用于关键词分析
        all_contents = Post.objects.filter(location=city_name).values_list('content', flat=True)
        
        # 使用你原来的强化版过滤器提取关键词
        auto_tags = extract_city_tags(list(all_contents))
        
        # 为了让侧边栏点击后地图能跳转，我们需要该城市其中一个帖子的坐标
        sample_post = Post.objects.filter(location=city_name, lat__isnull=False).first()
        
        hot_locations.append({
            'location': city_name,
            'count': item['count'],
            'keywords': auto_tags,
            'lat': float(sample_post.lat) if sample_post else None,
            'lon': float(sample_post.lon) if sample_post else None,
        })

    # 用于前端计算进度条百分比
    max_count = hot_locations[0]['count'] if hot_locations else 1
    
    # 整理地图打点数据（过滤掉没有坐标的帖子）
    locations_data = [
        {
            'id': p.id, 
            'title': p.title, 
            'lat': float(p.lat), 
            'lon': float(p.lon), 
            'location': p.location
        } 
        for p in posts if p.lat and p.lon
    ]
    
    return render(request, 'travel_posts/index.html', {
        'posts': posts,
        'locations': locations_data,      # 用于 Leaflet 地图初始化打点
        'hot_locations': hot_locations,  # 用于侧边栏城市排行和关键词展示
        'max_count': max_count           # 用于进度条比例
    })

def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            for f in request.FILES.getlist('files'):
                PostMedia.objects.create(post=post, file=f)
            return redirect('index')
    return render(request, 'travel_posts/add_post.html', {'form': PostForm()})

def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.likes += 1
        post.save()
        # 保持你原来的 AJAX 支持
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse(post.likes)
        return redirect('index')
    except:
        return HttpResponse(status=404)

def add_comment(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        author = request.user.username if request.user.is_authenticated else "匿名用户"
        text = request.POST.get('text')
        if text:
            Comment.objects.create(post=post, author=author, text=text)
    return redirect('index')