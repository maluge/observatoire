# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, render, redirect, get_object_or_404
from django.views import generic
from .forms import CommentaireForm, EntreeForm, TagForm, RechercheForm
from .models import Entree, Tag, User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
from django.core import mail


class BlogDetail(generic.DetailView):
    template_name = 'blog/blogdetail.html'
    model = Entree


@login_required(login_url='/login/')
def listing(request):
#    if request.user.is_authenticated:
        post_list = Entree.objects.all()
        paginator = Paginator(post_list, 5) # Show 5 post par page
        tag_list = Tag.objects.all() # Utilisé pour la liste de tous les mots clefs avec un lien
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            posts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            posts = paginator.page(paginator.num_pages)

        return render(request, 'blog/list.html', {'posts': posts, 'tags':tag_list})
#    else:
   #Do something for anonymous users.
#	return HttpResponseRedirect('/admin/login/')


@login_required(login_url='/login/')
def commentaire_new(request, pk):
    billetacommenter = Entree.objects.get(pk=pk)
    posttitre=billetacommenter.titre_en
    if request.method == "POST":
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.entree = Entree.objects.get(pk=pk)
            commentaire.author = request.user
            commentaire.save()
            sujet = "Nouveau commentaire dans le blog de l'observatoire"
            textecourriel = u'Un nouveau commentaire au billet intitulé : ' + posttitre + u' vient d\'être publié par '\
                + commentaire.author.first_name \
                + ' ' + commentaire.author.last_name
            with mail.get_connection() as connection:
                mail.EmailMessage(
                    sujet, textecourriel, 'de moi', ['malijai.caulet@videotron.ca','malijai.caulet@videotron.ca' ],
                    connection=connection,
                ).send()
            return redirect('blogdetail', pk=pk)
    else:
        form = CommentaireForm()
    return render(request, "blog/commentaire_edit.html", {'form': form,  
                                                        'post_id': pk,
                                                        'Posttitre':  posttitre})

@login_required(login_url='/login/')
def entree_new(request):
    tag_list = Tag.objects.all()
    if request.method == "POST":
        form = EntreeForm(request.POST)
        if form.is_valid():
            entree = form.save(commit=False)
            entree.author = request.user
            entree.save()
            form.save_m2m()             # form save many to many (ici les tags selectionnes)
             #import ipdb; ipdb.set_trace()
            sujet = "Nouveau billet dans le blog de l'observatoire"
            textecourriel = u'Un nouveau billet intitulé : ' + entree.titre_en + u' vient d\'être publié par '\
                + entree.author.first_name \
                + ' ' + entree.author.last_name
            with mail.get_connection() as connection:
                mail.EmailMessage(
                    sujet, textecourriel, 'de moi', ['malijai.caulet@videotron.ca','malijai.caulet@videotron.ca' ],
                    connection=connection,
                ).send()
            return redirect('blogdetail', entree.id)
    else:
        form = EntreeForm()
    return render(request, "blog/entree_edit.html", {'form': form, 'tags':tag_list})


@login_required(login_url='/login/')
def tag_new(request):
    tag_list = Tag.objects.all()
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            tag = form.save(commit=False)
            tag.slug=slugify(tag.mot_en)
            tag.save()
            return redirect('entree_new')
    else:
        form = TagForm()
    return render(request, "blog/tag_edit.html", {'form': form, 'tags': tag_list })

@login_required(login_url='/login/')
def view_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    return render_to_response('blog/view_tag.html', {
        'tag': tag,
        'entrees': Entree.objects.filter(tag=tag)[:10]
    })


@login_required(login_url='/login/')
def get_recherchetexte(request):
    form_class = RechercheForm
    if request.method == 'POST':
        form = form_class(data=request.POST)
        if form.is_valid():
            texte = request.POST.get('recherchetexte', '')
            post_list = Entree.objects.filter(texte_en__icontains=texte)
            if post_list:
                tag_list = Tag.objects.all()
                return render(request, 'blog/list.html', {'posts': post_list, 'tags': tag_list})
            else:
                return render(request, 'blog/recherche.html', {'form': form_class, 'message': texte})
    else:
        form_class = RechercheForm()

    return render(request, 'blog/recherche.html', {'form': form_class})


#Probablement a jeter plus tard
def index(request):
    return render(request, 'index.html')


