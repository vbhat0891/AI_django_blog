from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator
from watson_developer_cloud import PersonalityInsightsV3 as PersonalityInsights


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='a6501e93-0e87-4a9f-8b0d-9d72345dd3a4',
        password='KcldEctODn5S',
        version='2016-05-19 ')

    language_translator = LanguageTranslator(
        username='0cf4be9c-cf6a-40a8-917a-765aa80d5652',
        password='FlFKH2OtT24B')

    personality_insights = PersonalityInsights (
        version= '2017-10-13',
        username='3c82441d-14f0-4329-ab41-1625d158167b',
        password='OBRSvTv01pkV',)


    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        posting = post.text
        toneObj= json.dumps(tone_analyzer.tone(tone_input=posting,
                                   content_type="text/plain"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        post.angerScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][0]['score']
        post.disgustScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][1]['score']
        post.fearScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][2]['score']
        post.joyScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][3]['score']
        post.sadScore = post.toneObj2['document_tone']['tone_categories'][0]['tones'][4]['score']
        # print(post.toneObj2)

        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='es')
        obj = json.dumps(translation, indent=2, ensure_ascii=False)
        post.obj2 = json.loads(obj)
        post.translations = post.obj2['translations']
        post.translation = post.translations[0]
        post.spanish = post.translation['translation']
        post.word_count = post.obj2['word_count']
        post.character_count = post.obj2['character_count']

        profile = personality_insights.profile(
            content= post.text,
            accept='application/json',
            content_type='text/plain',
            raw_scores= True)
        persobj = json.dumps(profile, indent=2)
        post.persobj2 = json.loads(persobj)
        post.type0 = post.persobj2['personality'][0]['name']
        post.rawscore0 = post.persobj2['personality'][0]['raw_score']
        post.type1 = post.persobj2['personality'][1]['name']
        post.rawscore1 = post.persobj2['personality'][1]['raw_score']
        post.type2 = post.persobj2['personality'][2]['name']
        post.rawscore2 = post.persobj2['personality'][2]['raw_score']
        post.type3 = post.persobj2['personality'][3]['name']
        post.rawscore3 = post.persobj2['personality'][3]['raw_score']
        post.type4 = post.persobj2['personality'][4]['name']
        post.rawscore4 = post.persobj2['personality'][4]['raw_score']

    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Post.objects.get(pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
