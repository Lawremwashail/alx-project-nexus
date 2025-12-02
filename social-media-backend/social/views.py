import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

@csrf_exempt
@require_POST
def upload_image(request):
    """
    Accepts multipart/form-data with field 'image'.
    Returns JSON: { "url": "/post_images/filename.jpg" }
    """
    image = request.FILES.get('image')
    if not image:
        return JsonResponse({"error": "No image provided"}, status=400)

    # Save under MEDIA_ROOT/post_images/
    save_path = os.path.join('post_images', image.name)
    path = default_storage.save(save_path, ContentFile(image.read()))

    # Build URL relative to MEDIA_URL
    url = settings.MEDIA_URL.rstrip('/') + '/' + os.path.basename(path) if settings.MEDIA_URL else '/post_images/' + os.path.basename(path)
   
    return JsonResponse({"url": url}, status=201)
