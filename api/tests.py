# Create your tests here.

# tried to make an endpoint with all media files of an instance

# def post(self, request, **kwargs):
#         # add render_classes
#         model_name = request.data.get('modelName').capitalize()
#         model_id = request.data.get('modelId')
#         instance = getattr(api.models, model_name).objects.get(id=model_id)
#         try:
#             all_media = list(instance.media.all())
#             body = dict()
#             for idx, media in enumerate(all_media):
#                 body[f"media_{idx}_name"] = media.name
#                 body[f"media_{idx}_file"] = (
#                     media.name,
#                     bytes(base64.b64decode(media.binary)),
#                     "image/png"
#                 )
#             multipart_data = MultipartEncoder(body)
#             return Response(multipart_data.to_string(), content_type=multipart_data.content_type, status=200)
#         except MediaFile.DoesNotExist:
#             return JsonResponse({'error': 'Not Found',
#                                  'message': "MediaFile object isn't found"}, status=404)
#
# from requests_toolbelt.multipart.encoder import MultipartEncoder
# from django.core.management.base import BaseCommand
# class MultipartRenderer(BaseRenderer):
#     media_type = 'multipart/form-data'
#     format = 'multipart'
#
#     def render(self, data, media_type=None, renderer_context=None):
#         multipart_data = MultipartEncoder(fields=data)
#         return multipart_data.to_string()
#
#
# class GetMediaFileElement(APIView):
#     renderer_classes = [MultipartRenderer]
#
#     def get(self, request, **kwargs):
#         try:
#             media = MediaFile.objects.get(id=kwargs['media_id'])
#             return Response({'mediaName': media.name,
#                              'mediaBlob': media.binary},
#                             content_type='multipart/form-data',
#                             status=status.HTTP_200_OK)
#         except MediaFile.DoesNotExist:
#             return JsonResponse({'error': 'Not Found',
#                                  'message': "MediaFile object isn't found"}, status=404)

import requests

test_response = requests.request(method='get', url='http://127.0.0.1:8000/test', params={'colors': ['red', 'green', 'blue']})
print(test_response)

