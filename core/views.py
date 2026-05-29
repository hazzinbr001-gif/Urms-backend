from django.views.generic import TemplateView

class PlaceholderView(TemplateView):
    template_name = 'core/placeholder.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feature_name'] = self.request.GET.get('feature', 'This Feature')
        return context
